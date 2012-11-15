
from StringIO import StringIO

import re

vhost_start = re.compile(r'<VirtualHost\s+(.*?)>')
vhost_end = re.compile(r'</VirtualHost')
docroot_re = re.compile(r'(DocumentRoot\s+)(\S+)')

def replace_docroot(conf_string,vhost,new_docroot):
    conf_file = StringIO(conf_string)
    in_vhost = False
    curr_vhost = None
    for line in conf_file:
        print "LINE 1",line
        vhost_start_match = vhost_start.search(line)
        if vhost_start_match:
           curr_vhost = vhost_start_match.groups()[0]
           in_vhost = True
        if in_vhost and (curr_vhost == vhost):
           print "LINE 2",line
           docroot_match = docroot_re.search(line)
           if docroot_match:
              sub_line = docroot_re.sub(r'\1%s'%new_docroot,line)
              line = sub_line
        vhost_end_match = vhost_end.search(line)
        if vhost_end_match:
           in_vhost = False
        yield line
 
if __name__ == '__main__':
     conf_string = open("File/Apache.conf").read()
     for line in replace_docroot(conf_string,"local2:80","/tmp"):
         print line

    
