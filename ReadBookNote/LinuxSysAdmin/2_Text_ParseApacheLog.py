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