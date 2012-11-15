from StringIO import StringIO

conf_string = open("File/Apache.conf").read()

conf_file = StringIO(conf_string)

for line in conf_file:
    print line