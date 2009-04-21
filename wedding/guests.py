import cgi
import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class Guest(db.Model):
	name       = db.StringProperty()
	lastname   = db.StringProperty()
	children   = db.StringProperty(multiline=True)
	address    = db.StringProperty(multiline=True)
	type       = db.StringProperty()
	side       = db.StringProperty()
	invited    = db.IntegerProperty()
	expected   = db.IntegerProperty()
	rsvpstatus = db.StringProperty()
	rsvpcount  = db.IntegerProperty()

class RedirectToGuests(webapp.RequestHandler):
	def get(self):
		self.redirect('/guests')

class Guests(webapp.RequestHandler):
	def get(self):
		guests = db.GqlQuery("SELECT * FROM Guest ORDER BY side, type, lastname")

		template_values = {
			'guests': guests,
		}

		path = os.path.join(os.path.dirname(__file__), 'guests.html')

		if (self.request.headers['Accept'] == "text/xml" or self.request.url.endswith(".xml")):
			path = os.path.join(os.path.dirname(__file__), 'guests.xml')
			self.response.headers['Content-Type'] = 'text/xml'

		self.response.out.write(template.render(path, template_values))

class GuestR(webapp.RequestHandler):
	def get(self, key):
		if (self.request.get('mode') == 'edit'):
			self.getEdit(key)
		else:
			self.getView(key)

	def getView(self, key):
		guest = db.get(db.Key(key))

		template_values = {
			'guest': guest,
		}

		path = os.path.join(os.path.dirname(__file__), 'guest.html')
		self.response.out.write(template.render(path, template_values))
	
	def getEdit(self, key):
		guest = db.get(db.Key(key))

		template_values = {
			'guest': guest,
		}

		path = os.path.join(os.path.dirname(__file__), 'edit.html')
		self.response.out.write(template.render(path, template_values))

	def post(self, key):
		guest = db.get(db.Key(key))

		edit = self.request.get('edit', default_value = None)
		delete = self.request.get('delete', default_value = None)

		if (not(delete == None)):
			self.delete(key)
			return

		name = self.request.get('name', default_value = None)
		lastname = self.request.get('lastname', default_value = None)
		children = self.request.get('children', default_value = None)
		address = self.request.get('address', default_value = None)
		side = self.request.get('side', default_value = None)
		type = self.request.get('type', default_value = None)
		invited = self.request.get('invited', default_value = None)
		expected = self.request.get('expected', default_value = None)
		rsvpstatus = self.request.get('rsvpstatus', default_value = None)
		rsvpcount = self.request.get('rsvpcount', default_value = None)

		if (not(name == None)):
			guest.name = name
		if (not(lastname == None)):
			guest.lastname = lastname
		if (not(children == None)):
			guest.children = children
		if (not(address == None)):
			guest.address = address
		if (not(side == None)):
			guest.side = side
		if (not(type == None)):
			guest.type = type
		if (not(invited == None)):
			try:
				guest.invited = int(invited)
			except:
				pass
		if (not(expected == None)):
			try:
				guest.expected = int(expected)
			except:
				pass
		if (not(rsvpstatus == None)):
			guest.rsvpstatus = rsvpstatus
		if (not(rsvpcount == None)):
			try:
				guest.rsvpcount = int(rsvpcount)
			except:
				pass

		guest.put()

		self.redirect('/wedding/guest/' + key)

	def delete(self, key):
		guest = db.get(db.Key(key))
		guest.delete()

		self.redirect('/wedding/guests')

class AddGuest(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'guests-add.html')
		self.response.out.write(template.render(path, {}))

	def post(self):
		guest = Guest()

		name = self.request.get('name', default_value = None)
		lastname = self.request.get('lastname', default_value = None)
		children = self.request.get('children', default_value = None)
		address = self.request.get('address', default_value = None)
		side = self.request.get('side', default_value = None)
		type = self.request.get('type', default_value = None)
		invited = self.request.get('invited', default_value = None)
		expected = self.request.get('expected', default_value = None)
		rsvpstatus = self.request.get('rsvpstatus', default_value = None)
		rsvpcount = self.request.get('rsvpcount', default_value = None)

		if (not(name == None)):
			guest.name = name
		if (not(lastname == None)):
			guest.lastname = lastname
		if (not(children == None)):
			guest.children = children
		if (not(address == None)):
			guest.address = address
		if (not(side == None)):
			guest.side = side
		if (not(type == None)):
			guest.type = type
		if (not(invited == None)):
			try:
				guest.invited = int(invited)
			except:
				pass
		if (not(expected == None)):
			try:
				guest.expected = int(expected)
			except:
				pass
		if (not(rsvpstatus == None)):
			guest.rsvpstatus = rsvpstatus
		if (not(rsvpcount == None)):
			try:
				guest.rsvpcount = int(rsvpcount)
			except:
				pass

		guest.put()
		self.redirect('/wedding/guests')


application = webapp.WSGIApplication(
	[
		('/wedding', RedirectToGuests),
		('/wedding/guests(?:\.xml)?', Guests),
		('/wedding/guest/([^/]*)', GuestR),
		('/wedding/guests/add', AddGuest)
	],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
