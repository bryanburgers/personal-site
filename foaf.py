import cgi
import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import auth

html = 'text/html'
xhtml = 'application/xhtml+xml'
rdf_xml = 'application/rdf+xml'
rdf_n3 = 'application/rdf+n3'

def checkUser(user):
	if user == None:
		return False
	if user.email().lower() == 'bryan.burgers@gmail.com':
		return True
	return False

def loginRequired(func):
	def wrapper(self, *args, **kw):
		user = users.get_current_user()
		if not checkUser(user):
			self.redirect(users.create_login_url(self.request.uri))
		else:
			func(self, *args, **kw)
	return wrapper

class File(db.Model):
	mimeType = db.StringProperty()
	updated  = db.DateTimeProperty(auto_now_add=True)
	content  = db.TextProperty()

class Redirect(webapp.RequestHandler):
	def get(self):
		type = self.request.accept.best_match([html, xhtml, rdf_xml, rdf_n3])

		if type == rdf_xml or type == rdf_n3:
			self.response.set_status(303)
			self.response.headers['Location'] = '/data/bryan'
		else:
			self.response.set_status(303)
			self.response.headers['Location'] = '/profile/bryan'

class Data(webapp.RequestHandler):

	def get(self):
		file = File.all().filter('mimeType =', rdf_xml).order('-updated').get()

		self.response.headers['Content-Type'] = file.mimeType
		self.response.out.write(file.content)

	@auth.authorizationRequired
	def put(self):
		contentType = self.request.headers['Content-Type']
		if contentType == rdf_xml:
			file = File()
			file.content = self.request.body
			file.mimeType = contentType
			file.put()
			return

		self.response.set_status(406)

class Profile(webapp.RequestHandler):

	def get(self):
		file = File.all().filter('mimeType =', html).order('-updated').get()

		self.response.headers['Content-Type'] = file.mimeType
		self.response.out.write(file.content)

	@auth.authorizationRequired
	def put(self):
		contentType = self.request.headers['Content-Type']
		if contentType == html:
			file = File()
			file.content = self.request.body
			file.mimeType = contentType
			file.put()
			return

		self.response.set_status(406)

application = webapp.WSGIApplication(
	[
		('/id/bryan', Redirect),
		('/profile/bryan', Profile),
		('/data/bryan', Data),
	],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
