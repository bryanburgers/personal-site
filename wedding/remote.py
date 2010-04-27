#!/usr/bin/python
import code
import getpass
import sys

sys.path.append("C:\\Program Files\\Google\\AppEngine")
sys.path.append("C:\\Program Files\\Google\\AppEngine\\Lib\\django")
sys.path.append("C:\\Program Files\\Google\\AppEngine\\Lib\\webob")
sys.path.append("C:\\Program Files\\Google\\AppEngine\\Lib\\yaml\\lib")

from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import db

def auth_func():
  return raw_input('Username:'), getpass.getpass('Password:')

host = 'bryan-burgers.appspot.com'

remote_api_stub.ConfigureRemoteDatastore('bryan-burgers', '/remote_api', auth_func, host)

code.interact('App Engine interactive console for %s' % ('bryan-burgers',), None, locals())
  