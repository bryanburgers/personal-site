from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class Redirect(webapp.RequestHandler):
	def get(self):
		self.response.set_status(301)
		self.response.headers['Location'] = self.address

class RedirectResume(Redirect):
        def __init__(self):
                self.address = '/resume/'

class RedirectPortfolio(Redirect):
        def __init__(self):
                self.address = '/portfolio/'
		

application = webapp.WSGIApplication(
	[
		('/', RedirectResume),
		('/resume', RedirectResume),
		('/portfolio', RedirectPortfolio),
	],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
