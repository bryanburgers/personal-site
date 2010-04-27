import cgi
import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class GradesHandler(webapp.RequestHandler):

	def get(self):
                total = self.request.get('t', '20')
                try:
                        total = int(total)
                except:
                        total = 20

                self.response.out.write('<!DOCTYPE html>')
                self.response.out.write('<html><head><title>Grades</title></head><body><table><thead><tr><th>Right</th><th>Wrong</th><th>Percent</th></tr></thead><tbody>')
                for i in xrange(total*2, 0, -1):
                        right = i / 2.0
                        wrong = total - right
                        percent = int(round((right/total)*100))
                        self.response.out.write('<tr><td>' + str(right) + '</td><td>' + str(wrong) + '</td><td>' + str(percent) + '%</td></tr>')
                self.response.out.write('</tbody></table></body></html>')
                                                
application = webapp.WSGIApplication(
	[
		('/2010/grades', GradesHandler),
	],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
