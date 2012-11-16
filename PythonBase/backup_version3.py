# -*- encoding: utf-8 -*-

'''
Created on Mar 21, 2012

@author: root
'''

import  os
import  subprocess
import  time

source = ['/home/wye/Desktop/wye_cloudiya_fiile/']
target_dir = '/usr/local/src/backup'

today =target_dir + os.sep +time.strftime('%Y%m%d')
now = time.strftime('%H%M%S')

if not os.path.exists(today):
    os.mkdir(today)
    print('success create dir',today)

#str_comment = input('Enter a comment for this backup: ')  use in python3!
str_comment = raw_input('Enter a comment for this backup: ')

if len(str_comment) == 0:
    target = today + os.sep + now + '.tar.gz'
else:
    target = today + os.sep + str_comment.replace(' ', '_') + '_' + now + '.tar.gz'

targz_cmd = 'tar czPf {0} {1}'.format(target, ' '.join(source))

if os.system(targz_cmd) == 0:
    print('success backup file to ',target)
else:
    print('failed backup file ')
    
    


 
