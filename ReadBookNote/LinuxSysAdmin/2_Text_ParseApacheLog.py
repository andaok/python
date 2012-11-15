'''
Created on 2012-11-16

@author: root
'''

import sys

def dictify_logline(line):
    split_line = line.split()
    return {'remote_host':split_line[0],
            'status':split_line[8],
            'bytes_sent':split_line[9]
            }
    
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
    