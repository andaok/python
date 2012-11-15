#-*- encoding:utf-8 -*-

'''
Created on 2012-11-15

@author: root
'''

print "hello world ,'jack'"

print "hello world,\"jack\""

print " jack  \
        terry \
        luay  \
      "
      
print """ jack
          terry 
          luay
      """
      
uname = "Linux #1 SMP Tue Feb"

print "Linux" in uname
print "Linux" not in uname

print uname.find("SMP")
print uname.index("SMP")

SMP_index = uname.index("SMP")
print uname[SMP_index:]
print uname[:SMP_index]

print uname.startswith("Linux")
print uname.endswith("Feb1")

#切分技术实现startswith和endswith

if uname[:len("Linux")] == "Linux":
    print True
else:
    print False

#lstrip,rstrip,strip不只是被用来删除前后空格

xml_tag = "<some_tag>"
print xml_tag.lstrip("<")
print xml_tag.rstrip(">")

#strip不是仅仅删除匹配"<>",是删除"<"和">"任何可能的组合
print xml_tag.strip("<>")  # some_tag
#strip删除字符串中包含的"<","f","o","o",">"四个字符
print "<foooooooo>blsh<foo>".strip("<foo>")  #blsh


print "XiHa".lower() == "xiha"
print "XiHa".upper() == "XIHA"

print "jack,terry,jilly".split(',')
print "jack123terry123jilly".split("123")

print "jack,terry,jilly,hello".split(",",1)

#splitlines由字符串中每行组成的列表
multi_line_string = """ this
                        is
                        a multiline
                        piece of
                        text
                        """
print multi_line_string.splitlines()


list = ["jack","terry","jilly"]
print '|'.join(list)

print range(10)

",".join([str(i) for i in range(10)])

print "jack,terry,jilly,dog".replace("dog", "lucy")

#RE正则表达式

