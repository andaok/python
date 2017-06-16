import signal

def myHandler(signum,frame):
	print "now ,it's the time to stop"
	exit()

signal.signal(signal.SIGALRM,myHandler)
signal.alarm(5)

while True:
	print "not yet!"

print "this is end!"