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

#切分技术实现startswith和endswitch



