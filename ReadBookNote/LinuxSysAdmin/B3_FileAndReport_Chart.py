import gdchart
import shelve

shelve_file = shelve.open("File/BytesSumPerHost.bat")

#元组列表
items_list = [(i[1],i[0]) for i in shelve_file.items()]
items_list.sort()

bytes_sent = [i[0] for i in items_list]
ip_addresses = [i[1] for i in items_list]

 