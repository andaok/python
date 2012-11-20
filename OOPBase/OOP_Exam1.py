import time

class Person:
    PersonNum = 0
    def __init__(self,name,age):
        self.name = name
        self.age = age
        Person.PersonNum +=1
    def tell(self):
        print "now beijing time is %s"%(time.strftime('%Y%m%d%H%M%S'))
        print "this person information name %s,age %s"%(self.name,self.age)
    def currentPerNum(self):
        print "Current person number is %s"%(Person.PersonNum)
    def __del__(self):
        Person.PersonNum -=1
p1 = Person("jack","25")
p1.tell()
p1.currentPerNum()

time.sleep(3)

p2 = Person("jilly","18")
p3 = Person("terry","90")

p3.tell()
p3.currentPerNum()
del p2
p1.currentPerNum()
p3.currentPerNum()

