# -*- encoding:utf-8 -*-




import redis

# urls = ['http://www.163.com','http://www.baidu.cn']

r = redis.Redis(host='127.0.0.1',port=6379,db=0)

# num = 0

# while True:
# 	for url in urls:
# 		r.rpush('pool',url)
# 		num = num + 1
# 		print num


num = 0

while True:
	r.rpush('pool',num)
	num = num + 1

