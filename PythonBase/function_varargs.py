# -*- encoding:utf-8 -*-

'''
Created on Apr 5, 2012

@author: root
'''
#可接受任意多个形参的函数！
def total(inits=5,*numbers,**keywords):
    ''' 这里放置Docstrings ,首行头字母大写，句号结尾，第二行为空
    
       第三行开始详细的描述 
    '''
       
    count = inits
    for number in numbers:
        count += number
    for key in keywords:
        count += keywords[key]
    return count

def main():
    print(total(10,1,2,3,vegetables=50,fruits=100))
    print(total.__doc__)

if __name__ == "__main__":
    main()

#error!,关键字实参之后不能是非关键字实参。
#print(total(inits=10,10,1,2,3,vegetables=50,fruits=100))

#只能以关键字赋值的形参（keyword-only param）,将其放置在*号形参后面！
#如果这类形参没有默认值，则必须在调用函数时以关键字实参为其赋值！
#...........

 


    