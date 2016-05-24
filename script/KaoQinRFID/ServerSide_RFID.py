#! /usr/bin/env python
# -*- encoding:utf-8 -*-

# --------------------------------------- /
#Created on 2015-10-18
#author: wye
#Copyright @ 2014 - 2015  Cloudiya Tech . Inc
#
#Purpose:
#  Receive attendance equipment data,send commands to the attendance equipment.
#@date:2015-10-18
#@Achieve basic functions,Build version v1.0
#@date:2015-11-10
#@Alert for a attendance information contain 12 bytes serialid ,4 bytes timestamp , 16 bytes total.
#@date:2015-11-30
#@Save Parameters To ROM 
#@date:2016-01-18
#@add command for get attendance device config parameter
#@date:2016-01-26
#@increased support for multiple antennas
# --------------------------------------- /



from asyncore import dispatcher
from asynchat import async_chat
from cStringIO import StringIO
import logging.handlers
import socket , asyncore
import binascii
import logging
import struct
import time
import redis
import sys
import os



# ---------------------- /
# Log Function
# ---------------------- /

def GetLogger(logflag,loglevel="debug"):
    logger = logging.Logger(logflag)
    logfile = "/var/log/%s.log"%logflag
    hdlr = logging.handlers.RotatingFileHandler(logfile, maxBytes = 5*1024*1024, backupCount = 5)
    formatter = logging.Formatter("%(asctime)s -- [ %(name)s ] -- %(levelname)s -- %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)    
    if loglevel == "debug": 
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger



# ---------------------- /
# Server To Single Session
# ---------------------- /


class ChatSession(async_chat):

    def __init__(self,server,sock,RemoteIP,logger):

        async_chat.__init__(self,sock)

        self.server = server
        self.logger = logger
        self.SerialID = None
        self.RemoteIP = RemoteIP
        self.set_terminator(None)

        # ----------------- /
        # Related To Redis
        # ----------------- /

        self.redataIP = "10.2.10.19"
        self.redataPort = 6379
        self.redataDB = 0

        # ----------------- /
        # Packet Type Command Description 
        # ----------------- /

        #####################
        # Server To Device Commands
        #####################

        #@Restart Reader Cmd To Device
        self.cmd_svr_restart_reader = "5501" # 0x5501 

        #@Sync Server Time To Device
        self.cmd_svr_sync_time  = "5502" # 0x5502

        #@Set Network Parameters To Device
        self.cmd_svr_set_net_para = "5503" #0x5503

        #@Send Command To Device For Get Config Parameter
        self.cmd_svr_get_conf_para = "5504"  #0x5504

        # #@Set Heartbeat Packet Interval To Device
        # self.cmd_svr_set_heartbeat_interval = "5504" #0x5504

        # #@Set Antenna Power To Device
        # self.cmd_svr_antenna_power = "5505" #0x5505

        # #@Set Reader SerialID To Device
        # self.cmd_svr_set_reader_serialid = "5506" #0x5506  
 
        ######################
        # Device To Server Commands
        ######################

        #@Request Sync Time From Device
        self.cmd_dev_sync_time  = "aa01"  # 0xaa01

        #@Attendance Data Or Heartbeat Packet From Device
        self.cmd_dev_data_packet = "aa02" # 0xaa02

        #@Attendance Device Confg Parameter From Device
        self.cmd_dev_conf_para = "aa03"  # 0xaa03 

        #######################
        # Admin Platform Api to Server Commands
        #######################

        #@Restart Reader To Specified Device
        self.cmd_admin_restart_reader = "cc01" # 0xcc01 
        
        #@Sync Server Time To Specified Device
        self.cmd_admin_sync_time  = "cc02" # 0xcc02

        #@Set Network Parameters To Specified Device
        self.cmd_admin_set_net_para = "cc03" # 0xcc03

        #@Send Command To Device For Get Config Parameter
        self.cmd_admin_get_conf_para = "cc04" # 0xcc04

        # #@Set Heartbeat Packet Interval To Specified Device
        # self.cmd_admin_set_heartbeat_interval = "cc04" #0xcc04

        # #@Set Antenna Power To Specified Device
        # self.cmd_admin_antenna_power = "cc05" #0xcc05        


    def collect_incoming_data(self,OriData):
   
        AscOriData = binascii.b2a_hex(OriData)
        self.logger.debug("Received Data : %s"%AscOriData)

        OriDataBuf = StringIO(OriData)
        OriPacketCmdCode  = OriDataBuf.read(2)
        PacketCmdCode = binascii.b2a_hex(OriPacketCmdCode)

        try:
            FunObj = getattr(self, 'do_'+PacketCmdCode)
        except AttributeError:
            self.logger.error("Received Packet Type Is Not Known,Packet Command Code is %s"%PacketCmdCode)
            pass
        else:
            self.logger.debug("Call Function : %s"%('do_'+PacketCmdCode))
            FunObj(OriDataBuf)
    

    def handle_close(self):
        async_chat.handle_close(self)
        self.server.disconnect(self.SerialID)


    def sync_server_time(self):
        time_stamp = int(time.time())
        binary_TimeStamp = struct.pack('<i',time_stamp)
        ascii_TimeStamp =  binascii.b2a_hex(binary_TimeStamp)  
        ascii_PacketData =  self.cmd_svr_sync_time + ascii_TimeStamp
        binary_PacketData = binascii.a2b_hex(ascii_PacketData)
        return binary_PacketData       


    # --------------------------------------  /
    # Handle Command Function
    # --------------------------------------  / 

    ######################
    # Device To Server Commands
    ######################

    #@Request Sync Time From Device
    def do_aa01(self,OriDataBuf):
        self.logger.info("Packet Type : Request Sync Time From Device")
        OriDevSerialID  = OriDataBuf.read(4)
        self.SerialID = struct.unpack('<i', OriDevSerialID)[0]
        self.logger.info("Add Device %s Session To Session Container"%self.SerialID)
        self.server.save_session(self.SerialID,self)
        self.logger.info("Sync Server Time to Device %s"%self.SerialID)
        self.push(self.sync_server_time())

        OriPacketCmdCode  = OriDataBuf.read(2)
        if OriPacketCmdCode != "":
            self.logger.info("Request Sync Time Packet Include Attendance Data")
            self.do_aa02(OriDataBuf)


    #@Attendance Data Or Heartbeat Packet From Device
    def do_aa02(self,OriDataBuf):
        self.logger.info("Packet Type : Attendance Data Or Heartbeat Packet From Device")
        OriDevSerialID  = OriDataBuf.read(4)
        SerialID = struct.unpack('<i', OriDevSerialID)[0]
        OriTimeStamp = OriDataBuf.read(4)
        TimeStamp = struct.unpack('<i', OriTimeStamp)[0]
        OriTagNum = OriDataBuf.read(1)
        if OriTagNum == "" or struct.unpack('<b', OriTagNum)[0] == 0:
            self.logger.debug("Heartbeat Packet , Device SerialID : %s , TimeStamp : %s"%(SerialID,time.ctime(TimeStamp)))
            self.write_StaData_to_redis(SerialID,TimeStamp)
        else:
            TagNum = struct.unpack('<b', OriTagNum)[0]
            self.logger.debug("Data Packet , Device SerialID : %s , TimeStamp : %s , TagNum : %s"%(SerialID,time.ctime(TimeStamp),TagNum))
            OriAttenData = OriDataBuf.read(TagNum*16)
            self.write_AttenData_to_redis(OriAttenData,TagNum,SerialID)

            OriPacketCmdCode  = OriDataBuf.read(2)
            if OriPacketCmdCode != "":
                self.logger.info("Continue To Handle Attendance Data......")
                self.do_aa02(OriDataBuf)

            self.write_StaData_to_redis(SerialID,TimeStamp)


    #@Attendance Device Config Parameter From Device
    def do_aa03(self,OriDataBuf):
        try:
            self.logger.info("Packet Type : Attendance Device Config Parameter From Device")
            # Server Side IP Address
            OriField1 = OriDataBuf.read(1)
            Field1 = struct.unpack('<B',OriField1)[0]
            OriField2 = OriDataBuf.read(1)
            Field2 = struct.unpack('<B',OriField2)[0]
            OriField3 = OriDataBuf.read(1)
            Field3 = struct.unpack('<B',OriField3)[0]
            OriField4 = OriDataBuf.read(1)
            Field4 = struct.unpack('<B',OriField4)[0]
            ServerIPAddr = str(Field1) + "." + str(Field2) + "." + str(Field3) + "." + str(Field4)
            # Server Side Port
            OriServerPort = OriDataBuf.read(2)
            ServerPort = struct.unpack('<H',OriServerPort)[0]
            # Device IP Address
            OriField1 = OriDataBuf.read(1)
            Field1 = struct.unpack('<B',OriField1)[0]
            OriField2 = OriDataBuf.read(1)
            Field2 = struct.unpack('<B',OriField2)[0]
            OriField3 = OriDataBuf.read(1)
            Field3 = struct.unpack('<B',OriField3)[0]
            OriField4 = OriDataBuf.read(1)
            Field4 = struct.unpack('<B',OriField4)[0]        
            DevIPAddr = str(Field1) + "." + str(Field2) + "." + str(Field3) + "." + str(Field4)
            # Device Sub NetMask
            OriField1 = OriDataBuf.read(1)
            Field1 = struct.unpack('<B',OriField1)[0]
            OriField2 = OriDataBuf.read(1)
            Field2 = struct.unpack('<B',OriField2)[0]
            OriField3 = OriDataBuf.read(1)
            Field3 = struct.unpack('<B',OriField3)[0]
            OriField4 = OriDataBuf.read(1)
            Field4 = struct.unpack('<B',OriField4)[0]        
            DevNetmask = str(Field1) + "." + str(Field2) + "." + str(Field3) + "." + str(Field4)
            # Device Gateway
            OriField1 = OriDataBuf.read(1)
            Field1 = struct.unpack('<B',OriField1)[0]
            OriField2 = OriDataBuf.read(1)
            Field2 = struct.unpack('<B',OriField2)[0]
            OriField3 = OriDataBuf.read(1)
            Field3 = struct.unpack('<B',OriField3)[0]
            OriField4 = OriDataBuf.read(1)
            Field4 = struct.unpack('<B',OriField4)[0]        
            DevGateway = str(Field1) + "." + str(Field2) + "." + str(Field3) + "." + str(Field4)  
            # Device Serial ID           
            OriDevSerialID  = OriDataBuf.read(4)
            SerialID = struct.unpack('<i', OriDevSerialID)[0]
            # Device Heartbeat Packet Time Interval
            OriHBInter = OriDataBuf.read(1)
            HBInter = struct.unpack('<B',OriHBInter)[0]
            # Device Card Induction Time Interval
            OriCardInt = OriDataBuf.read(1)
            CardInt = struct.unpack('<B',OriCardInt)[0]
            # Device Antenna Power
            OriAPNum = OriDataBuf.read(1)
            APNum = struct.unpack('<B',OriAPNum)[0]
            # Device Local Time
            OriTimeStamp = OriDataBuf.read(4)
            TimeStamp = struct.unpack('<i', OriTimeStamp)[0]
            # Device Antenna Number
            OriANNum = OriDataBuf.read(1)
            ANNum = struct.unpack('<B',OriANNum)[0]

            DataMap = {"GetConfTime":TimeStamp,"ServerIPAddr":ServerIPAddr,"ServerPort":ServerPort,"DevIPAddr":DevIPAddr,"DevNetmask":DevNetmask,"DevGateway":DevGateway,"SerialID":SerialID,"HBInter":HBInter,"CardInt":CardInt,"APNum":APNum,"ANNum":ANNum}

            redispool = redis.ConnectionPool(host=self.redataIP,port=self.redataPort,db=self.redataDB)
            redata = redis.Redis(connection_pool=redispool)
            redpipe = redata.pipeline()
            redpipe.hmset("%s_status"%SerialID,DataMap)
            redpipe.execute()
        except Exception,e:
            self.logger.error("Handle Attendacen Device Config Info Exception,Error is %s,But Main Program Not Quit......"%e)

   
    #####################
    # Server To Device Commands
    #####################

    #@Reboot Attendacen Device Controller
    def do_5501(self,OriDataBuf):
        self.logger.info("Packet Type : Restart Controller Cmd To Device")
        OriDevSerialID  = OriDataBuf.read(4)
        SerialID = struct.unpack('<i', OriDevSerialID)[0]

        BinFunCode = struct.pack('<B',1)
        ascii_FunCode = binascii.b2a_hex(BinFunCode)

        ascii_PacketData = self.cmd_svr_restart_reader + ascii_FunCode
        binary_PacketData = binascii.a2b_hex(ascii_PacketData)
        self.logger.info("Restart Controller Cmd To Device %s , Ascii Data : %s"%(SerialID,ascii_PacketData))
        self.server.send_data_to_device(SerialID,binary_PacketData)


    #@Sync Server Time To Device
    def do_5502(self,OriDataBuf):
        self.logger.info("Packet Type : Sync Server Time To Device")
        OriDevSerialID  = OriDataBuf.read(4)
        SerialID = struct.unpack('<i', OriDevSerialID)[0]
        binary_PacketData = self.sync_server_time()
        self.logger.info("Sync Server Time To Device %s , Ascii Data : %s"%(SerialID,binascii.b2a_hex(binary_PacketData)))
        self.server.send_data_to_device(SerialID,binary_PacketData)

    
    #@Set Network Parameters To Device
    def do_5503(self,OriDataBuf):
        self.logger.info("Packet Type : Set Network Parameters To Device")
        OriDevSerialID  = OriDataBuf.read(4)
        SerialID = struct.unpack('<i', OriDevSerialID)[0]
        OriNetParaData = OriDataBuf.read(30)
        ascii_PacketData = self.cmd_svr_set_net_para + binascii.b2a_hex(OriNetParaData)
        binary_PacketData = binascii.a2b_hex(ascii_PacketData)
        self.logger.info("Set Network Parameters To Device %s , Ascii Data : %s"%(SerialID,ascii_PacketData))
        self.server.send_data_to_device(SerialID,binary_PacketData)

    #@Get Config Parameter From Device
    def do_5504(self,OriDataBuf):
        self.logger.info("Packet Type : Get Config Parameter Cmd To Device")
        OriDevSerialID  = OriDataBuf.read(4)
        SerialID = struct.unpack('<i', OriDevSerialID)[0]

        BinFunCode = struct.pack('<B',1)
        ascii_FunCode = binascii.b2a_hex(BinFunCode)

        ascii_PacketData = self.cmd_svr_get_conf_para + ascii_FunCode
        binary_PacketData = binascii.a2b_hex(ascii_PacketData)
        self.logger.info("Get Config Parameter Cmd To Device %s , Ascii Data : %s"%(SerialID,ascii_PacketData))
        self.server.send_data_to_device(SerialID,binary_PacketData)
       
    
    # #@Set Heartbeat Packet Interval To Device
    # def do_5504(self,OriDataBuf):
    #     self.logger.info("Packet Type : Set Heartbeat Packet Interval To Device")
    #     OriDevSerialID  = OriDataBuf.read(4)
    #     SerialID = struct.unpack('<i', OriDevSerialID)[0]
    #     OriHBInter = OriDataBuf.read(1)
    #     ascii_PacketData = self.cmd_svr_set_heartbeat_interval + binascii.b2a_hex(OriHBInter)
    #     binary_PacketData = binascii.a2b_hex(ascii_PacketData)
    #     self.logger.info("Set Heartbeat Packet Interval To Device %s , Ascii Data : %s"%(SerialID,ascii_PacketData))
    #     self.server.send_data_to_device(SerialID,binary_PacketData)


    # #@Set Antenna Power To Device
    # def do_5505(self,OriDataBuf):
    #     self.logger.info("Packet Type : Set Antenna Power To Device")
    #     OriDevSerialID  = OriDataBuf.read(4)
    #     SerialID = struct.unpack('<i', OriDevSerialID)[0]
    #     OriAPNum = OriDataBuf.read(1)
    #     ascii_PacketData = self.cmd_svr_antenna_power + binascii.b2a_hex(OriDevSerialID) + binascii.b2a_hex(OriAPNum)
    #     binary_PacketData = binascii.a2b_hex(ascii_PacketData)
    #     self.logger.info("Set Antenna Power To Device %s , Ascii Data : %s"%(SerialID,ascii_PacketData))
    #     self.server.send_data_to_device(SerialID,binary_PacketData)


    # #@Ser Reader SerialID To Device
    # def do_5506(self,OriDataBuf):
    #     self.logger.info("Packet Type : Set Serial ID To Device")
    #     OldDevSerialID  = OriDataBuf.read(4)
    #     OldSerialID = struct.unpack('<i', OldDevSerialID)[0]
    #     NewDevSerialID  = OriDataBuf.read(4)
    #     ascii_PacketData = self.cmd_svr_set_reader_serialid + binascii.b2a_hex(NewDevSerialID)
    #     binary_PacketData = binascii.a2b_hex(ascii_PacketData)
    #     self.logger.info("Set Reader SerialID To Device %s , Ascii Data : %s"%(OldSerialID,ascii_PacketData))
    #     self.server.send_data_to_device(OldSerialID,binary_PacketData)


    #####################
    # Admin Platform Api to Server Commands
    #####################

    #@Restart Controller To Specified Device
    def do_cc01(self,OriDataBuf):
        self.do_5501(OriDataBuf)

    #@Sync Server Time To Specified Device
    def do_cc02(self,OriDataBuf):
        self.do_5502(OriDataBuf)

    #@Set Network Parameters To Specified Device
    def do_cc03(self,OriDataBuf):
        self.do_5503(OriDataBuf)

    #@Send Command To Specified Device For Get Config Parameter 
    def do_cc04(self,OriDataBuf):
        self.do_5504(OriDataBuf)    

    # #@Set Heartbeat Packet Interval To Specified Device
    # def do_cc04(self,OriDataBuf):
    #     self.do_5504(OriDataBuf)

    # #@Set Antenna Power To Specified Device
    # def do_cc05(self,OriDataBuf):
    #     self.do_5505(OriDataBuf)

    # #@Set Reader SerialID To Specified Device
    # def do_cc06(self,OriDataBuf):
    #     self.do_5506(OriDataBuf)   

    
    #######################
    # Interaction With Redis
    #######################
    def write_AttenData_to_redis(self,OriAttenData,TagNum,SerialID):
        try:
            redispool = redis.ConnectionPool(host=self.redataIP,port=self.redataPort,db=self.redataDB)
            redata = redis.Redis(connection_pool=redispool)
            redpipe = redata.pipeline()

            OriAttenDataBuf = StringIO(OriAttenData)
            while TagNum != 0:
                # Obtain Tag Serial ID
                # Serial Number Has Two Ways Of Express
                # (1) String 24 , Ascii Code
                OriTagSerialID = OriAttenDataBuf.read(12)
                TagSerialID = binascii.b2a_hex(OriTagSerialID)
                # (2) String 8 , Decimal System
                # OriAttenDataBuf.read(8)
                # OriTagSerialID = OriAttenDataBuf.read(4)
                # TagSerialID = struct.unpack('<i', OriTagSerialID)[0]
                
                # Obtain Atten Stamp Time
                OriTimeStamp = OriAttenDataBuf.read(4)
                TimeStamp = struct.unpack('<i', OriTimeStamp)[0]
                
                redpipe.rpush("OriAttenDataList","%s-%s-%s"%(SerialID,TimeStamp,TagSerialID))

                self.logger.debug("%s - %s - %s - %s"%(TagNum,TimeStamp,time.ctime(TimeStamp),TagSerialID))

                TagNum = TagNum - 1
            redpipe.execute()
        except Exception,e:
            self.logger.error("Write Atten Data To Redis Exception,Error is %s,But Main Program Not Quit......"%e)

    def write_StaData_to_redis(self,SerialID,TimeStamp):
        try:
            redispool = redis.ConnectionPool(host=self.redataIP,port=self.redataPort,db=self.redataDB)
            redata = redis.Redis(connection_pool=redispool)
            redpipe = redata.pipeline()
            DataMap = {"time":TimeStamp,"ip":self.RemoteIP}
            redpipe.hmset("%s_status"%SerialID,DataMap)
            redpipe.execute()
        except Exception,e:
            self.logger.error("Write Status Data To Redis Exception,Main Program Not Quit......")


# ---------------------- /
# Generate a New Session For The Connection And
# Operate Session Of Attendance Equipment 
# ---------------------- /

class ChatServer(dispatcher):

    def __init__(self,host,port,logger):

        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host,port))
        self.listen(10)
        self.logger = logger
        self.sessions = {}
        
    def disconnect(self,serialid):
        if self.sessions.has_key(serialid):
            self.sessions.pop(serialid)

    def save_session(self,serialid,session):
        self.sessions[serialid] = session

    def send_data_to_device(self,serialid,data):
        self.sessions[serialid].push(data)

    def handle_accept(self):
        conn,addr = self.accept()
        ChatSession(self,conn,addr[0],self.logger)


if __name__ == "__main__":

    host = "61.183.254.135"
    port = 5005
    logger = GetLogger("KaoQinRFID")
    s = ChatServer(host,port,logger)
    try:
        asyncore.loop()
    except Exception,e:
        logger.error("KaoQinRFID Program Exception,Error is %s"%e)
        




