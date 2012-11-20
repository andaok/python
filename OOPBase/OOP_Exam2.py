class Person:
    PersonNum = 0
    def __init__(self,name,age):
        self.name = name
        self.age = age
        Person.PersonNum +=1
        #self.__class__.PersonNum +=1
        

    def tell(self):
        print "this person information name %s,age %s"%(self.name,self.age)
    def currentPerNum(self):
        print "Current person number is %s"%(Person.PersonNum)
    def __del__(self):
        
        Person.PersonNum -=1
        #self.__class__.PersonNum -=1

class Student(Person):
    def __init__(self,name,age,mark):
        Person.__init__(self, name, age)
        self.mark = mark
    def tell(self):
        Person.tell(self)
        print "student mark is %s"%(self.mark)


z1 = Student("hack","26","67")
z1.tell()
z1.currentPerNum()

z2 = Student("kill","27","76")

z3 = Student("woji","26","87")
z3.tell()
z3.currentPerNum()

del z2
z1.currentPerNum()
z3.currentPerNum()