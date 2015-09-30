
from cStringIO import StringIO
import struct
import time

def decode(f):

    def read_le16(f):
        oridata  = f.read(2)
        print "ORI DATA IS :", repr(oridata)
        undata = struct.unpack('<h', oridata)[0]
        print "UNPACK DATA IS :", undata
        return undata

    def read_timestamp(f):
        oridata  = f.read(4)
        print "ORI TIME DATA IS :", repr(oridata)        
        ts = struct.unpack('<l', oridata)[0]
        print "UNPACK TIME DATA IS :", ts
        return time.ctime(ts)

    def read_byte(f):
        oridata  = f.read(1)
        print "ORI BYTE DATA IS :", repr(oridata)
        ordata = ord(oridata) 
        print "ORI BYTE ORD DATA IS :", ordata         
        return ordata

    def read_pascal(f):
        oridata  = f.read(1)
        print "ORI PASCAL DATA IS :", repr(oridata)          
        l = ord(oridata)
        print "ORI PASCAL ORD DATA IS:",l
        pascalstr = f.read(l)
        print "PASCALSTR is :",pascalstr
        return pascalstr

    result = []

    # Read total length
    result.append('Total message length is %d bytes' % read_le16(f))

    # Read timestamp
    result.append(read_timestamp(f))

    # Read 3 x byte
    result.append(read_byte(f))
    result.append(read_byte(f))
    result.append(read_byte(f))

    # Read 1 x LE16
    result.append(read_le16(f))

    # Read 3 x pascal string
    result.append(read_pascal(f))
    result.append(read_pascal(f))
    result.append(read_pascal(f))

    return result

s = 'L\x00k\x07vQ\n\x01\xffh\x00\x04NGIN\x04MAIN6Product XX finished reprocessing cdc XXXXX at jesadr 0c\x00k\x07vQ\n\x01\xffF\x00\x06CSSPRD\x0cliab_checkerCCheckpointed to XXXXXXXXXXXXXXXX:XXXXXXX.XXX at jesadr 0 (serial 0)[\x00l\x07vQ\n\x00\xff\x01\x00\x05MLIFE\x06dayendBdayend 1 Copyright XXXX XXXXXXX XXXXXXX XXXXX XXX XXXXXX XXXXXXXX.'

f = StringIO(s)
print decode(f)
print decode(f)
print decode(f)