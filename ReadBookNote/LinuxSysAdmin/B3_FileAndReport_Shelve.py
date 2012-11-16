#-*- encoding:utf-8 -*-

import shelve
import B2_Text_ParseApacheLog_Re


#shelve将一个磁盘上的文件与一个“dict-like”对象关联起来，操作这个“dict-like”对象，就像操作dict对象一样，
#最后可以将“dict-like”的数据持久化到文件。对这个"dict-like"对象进行操作的时候，key和value的类型必须是字符串。
#它支持在"dict-like"对象中存储任何可以被pickle序列化的对象

logfile = open("File/access.log",'r')
shelve_file = shelve.open("File/BytesSumPerHost.bat")

for line in logfile:
    d_line = B2_Text_ParseApacheLog_Re.dictify_logline(line)
    shelve_file[d_line['remote_host']] = \
        shelve_file.setdefault(d_line['remote_host'],0) + \
        int(d_line['bytes_sent'])

logfile.close()
shelve_file.close()

dict_obj = shelve.open("File/BytesSumPerHost.bat",'r')
for item in dict_obj.items():
    print item