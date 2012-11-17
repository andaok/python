#-*- encoding:utf-8 -*-

import gdchart
import shelve

shelve_file = shelve.open("File/BytesSumPerHost.bat")

#元组列表
items_list = [(i[1],i[0]) for i in shelve_file.items()]
items_list.sort()

bytes_sent = [i[0] for i in items_list]
ip_addresses = [i[1] for i in items_list]

chart = gdchart.Bar() 
chart.width = 400
chart.height = 400
chart.bg_color = "white"
chart.plot_color = "black"
chart.xtitle = "IP ADDRESS"
chart.ytitle = "Bytes Sent"
chart.title = "Usage bytes by ip address"
chart.setData(bytes_sent)
chart.setLabels(ip_addresses)
chart.draw("File/bytes_ip_adr.png")

shelve_file.close()