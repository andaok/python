
import sys
import re

log_line_re = re.compile(r'''(?P<remote_host>\S+)  #remote host ip
                             \s+                   #whitespace
                             \S+                   #"-"
                             \s+                   #whitespace
                             \S+                   #"-"
                             \s+                   #whitespace
                             \[[^\[\]]+\]          #time
                             \s+                   #whitespace
                             "[^"]+"               #first line of request
                             \s+                   #whitespace
                             (?P<status>\d+)       #status
                             \s+                   #whitespace
                             (?P<bytes_sent>-|\d+) #bytes sent to client
                             \s*                   #whitespace 
                         ''',re.VERBOSE)

def dictify_logline(line):
    m = log_line_re.match(line)
    if m:
        groupdict = m.groupdict()
        if groupdict['bytes_sent'] == '-':
            groupdict['bytes_sent'] = "0"
        return groupdict
    else:
        return {'remote_host':None,'status':None,'bytes_sent':"0"}
    
def generate_log_report(logfile):
    report_dict = {}
    for line in logfile:
        line_dict = dictify_logline(line)
        print line_dict
        try:
            bytes_sent = int(line_dict['bytes_sent'])
        except ValueError:
            continue
        report_dict.setdefault(line_dict['remote_host'],[]).append(bytes_sent)
    return report_dict

if __name__ == "__main__":
    try:
        infile = open("File/access.log",'r')
    except IOError:
        sys.exit(1)
    print generate_log_report(infile)
    
    infile.close()