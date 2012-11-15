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

import re
re_obj = re.compile("{{(.*?)}}")
some_string = "this is a string with {{words}} embedded in \
{{curly brackers}} to show an {{example}} of {{regular expressions}}"
for match in re_obj.findall(some_string):
    print "MATCH->",match


pattern = 'pDq'
re_obj = re.compile(pattern)
print re_obj.search("xiha,pDq,xczxc,pDq").group()
print re_obj.search("xiha,pDq,xczxc,pDq").start()
print re_obj.search("xiha,pDq,xczxc,pDq").end()
print re_obj.search("xiha,pDq,xczxc,pDq").span()
print re_obj.search("xiha,pDq,xczxc,pDq").groupdict()



some_string = 'a few little words'    
raw_pattern = r'\b[a-z]+\b'
re_obj = re.compile(raw_pattern)
print re_obj.findall(some_string)

re_obj = re.compile(r'\bt.*?e\b')
print re_obj.findall("time,tame,tune,tint,tire")

re_obj = re.compile(r'\b\w*e\b')
print re_obj.findall("time,tame,tune,tint,tire")

#模式分组
re_obj = re.compile(r"""
(
A\W+\b(big|small)\b\W+\b
(brown|purple)\b\W+\b(cow|dog)\b\W+\b(ran|jumped)\b\W+\b
(to|down)\b\W+\b(the)\b\W+\b(street|moon).*?\.
)""",re.VERBOSE)

print re_obj.findall('A big brown dog ran down the street. \
A small purple cow jumped to the moon.')

#finditer
for item in re_obj.finditer('A big brown dog ran down the street. A small purple cow jumped to the moon.'):
    print item
    print item.groups()
    
#match,search
print "Start Test match and search...."
re_obj = re.compile("FOO")
print re_obj.search("xiha FOO and")
print re_obj.search("xiha FOO and",5,8)

print re_obj.match("xiha FOO")
print re_obj.match("xiha FOO and",5,8)

#re.sub()
text = "hello world , my friends"
print re.sub(r'\s+',"-",text)

#或
re_obj = re.compile(r'\s+')
print re_obj.sub("-",text)


text = "DocumentRoot /var/www/"
pattern = r'(DocumentRoot\s+)(\S+)'
re_obj = re.compile(pattern)
print re_obj.sub(r'\1xiha',text) # DocumentRoot xiha

text = "<VirtualHost localhost:80> <VirtualHost local2:80> <VirtualHost local3:80>"
pattern = r'<VirtualHost\s+(.*?)>'
re_obj = re.compile(pattern)
print re_obj.match(text).groups()  # ('localhost:80',)
print re_obj.search(text).groups() # ('localhost:80',)
print re_obj.findall(text)         # ['localhost:80', 'local2:80', 'local3:80']

#enumerate函数，一般遍历list得不到item的index.

list = ["my%s"%str(i) for i in range(10)]
print list
for index , item in enumerate(list):
    print index,":",item 

#字典setdefault
dict = {}
dict.setdefault("groups",[])

