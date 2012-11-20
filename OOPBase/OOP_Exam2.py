class Person:
    PersonNum = 0
    def __init__(self,name,age):
        self.name = name
        self.age = age
        Person.PersonNum +=1
    def tell(self):
        print "this person information name %s,age %s"%(self.name,self.age)
    def currentPerNum(self):
        print "Current person number is %s"%(Person.PersonNum)
    def __del__(self):
        Person.PersonNum -=1

class Student(Person):
    def __init__(self,name,age,mark):
        Person.__init__(self, name, age)
        self.mark = mark
    def tell(self):
        Person.tell(self)
        print "student mark is %s"%(self.mark)

s1 = Student("hack","26","67")
s1.tell()
s1.currentPerNum()

s2 = Student("kill","27","76")

s3 = Student("woji","26","87")
s3.tell()
s3.currentPerNum()

#del s2
s1.currentPerNum()
s3.currentPerNum()