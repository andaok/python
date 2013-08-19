'''
Created on 2013-8-18

@author: root
'''

import cherrypy

class HelloWorld(object):
    
    def index(self):
        return "hello world!!!"
    
    index.expose = True
    
cherrypy.quickstart(HelloWorld())