import signal

def myHandler(signum,frame):
	print "now ,it's the time to stop"
	raise AssertionError

signal.signal(signal.SIGALRM,myHandler)
signal.alarm(2)

try:
	while True:
		print "not yet!"
except AssertionError:
	print "timeout happen!"

print "this is end!"

