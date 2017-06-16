import signal
import salt.client

def myHandler(signum,frame):
    print "now ,it's the time to stop"
    raise AssertionError


def get_host_status(hostname):
    signal.signal(signal.SIGALRM,myHandler)
    signal.alarm(1)
    local = salt.client.LocalClient()
    try:
        resp = local.cmd(hostname,'test.ping')
        if resp and resp[hostname]:
            return 1
        else:
            return 0
    except AssertionError:
        return 0


def get_host_status_no_timeout_stop(hostname):
    local = salt.client.LocalClient()
    resp = local.cmd(hostname,'test.ping')

    if resp and resp[hostname]:
        return 1
    else:
        return 0


for host in ['Q607-SECURITY-1','W612-JENKDOCK-3','W612-JENKDOCK-4']:
    print get_host_status(host)
    #print get_host_status_no_timeout_stop(host)

