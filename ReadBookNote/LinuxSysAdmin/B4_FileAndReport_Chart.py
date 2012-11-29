#-*- encoding:utf-8 -*-

import gdchart
import shelve

def chartBar():
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
    chart.draw("File/bytes_ip_bar.png")
    shelve_file.close()

#chartBar()

import itertools
def chartPie():
    shelve_file = shelve.open("File/BytesSumPerHost.bat")
    items_list = [(i[1],i[0]) for i in shelve_file.items() if i[1]>0]
    items_list.sort()
    bytes_sent = [i[0] for i in items_list]
    ip_addresses = [i[1] for i in items_list]
    chart = gdchart.Pie()
    chart.width = 400
    chart.height = 400
    chart.bg_color = 'white'
    color_cycle = itertools.cycle([0xDDDDDD,0x111111,0x777777])
    color_list = []
    for i in bytes_sent:
        color_list.append(color_cycle.next())
    chart.color = color_list
    chart.plot_color = 'black'
    chart.title = "Usage By Ip Address "
    
    #chart.setData()不能直接接受list为参数,应该是个bug
    chart.setData(*bytes_sent)
    chart.setLabels(ip_addresses)
    chart.draw("File/bytes_ip_pie.png")

    shelve_file.close()    
    
#chartPie()    
   
def chartLine():
    shelve_file = shelve.open("File/BytesSumPerHost.bat")

    #元组列表
    items_list = [(i[1],i[0]) for i in shelve_file.items()]
    items_list.sort()

    bytes_sent = [i[0] for i in items_list]
    ip_addresses = [i[1] for i in items_list]

    chart = gdchart.Line() 
    chart.width = 400
    chart.height = 400
    chart.bg_color = "white"
    chart.plot_color = "black"
    chart.xtitle = "Tasktracker Nums"
    chart.ytitle = "Time (s)"
    chart.title = "Block Size 8MB,Block Nums 8"
    chart.setData([0,501.174,469.293,452.384,464.434,475.99,307.415])
    chart.setLabels([0,3,4,5,6,7,8])
    chart.draw("File/linevideo1.png")
    shelve_file.close()    

chartLine() 
    
    
    