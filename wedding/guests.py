import cgi
import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

def checkUser(user):
	if user == None:
		return False
	if user.email().lower() == 'bryan.burgers@gmail.com':
		return True
	if user.email().lower() == 'kmvanbemmel@ole.augie.edu':
		return True
	if user.email().lower() == 'burgers.travis@gmail.com':
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

class Home(webapp.RequestHandler):
	def get(self):

		user = users.get_current_user()
		if checkUser(user):
			template_values = {
				'logout_url': users.create_logout_url('/wedding'),
			}
			path = os.path.join(os.path.dirname(__file__), 'home-logged-in.html')
			self.response.out.write(template.render(path, template_values))
		else:
			template_values = {
				'logon_url': users.create_login_url('/wedding'),
			}
			path = os.path.join(os.path.dirname(__file__), 'home-logged-out.html')
			self.response.out.write(template.render(path, template_values))

class Guests(webapp.RequestHandler):
	@loginRequired
	def get(self):

		queryArguments = []
		requestArguments = []
		for arg in self.request.arguments():
			requestArguments.append(arg.lower())

		whereClauses = []
		whereClausesTransformed = []

		if "address" in requestArguments:
			queryArguments.append(self.request.get("address"))
			whereClauses.append("address = :1")

		if "rsvpstatus" in requestArguments:
			queryArguments.append(self.request.get("rsvpstatus"))
			whereClauses.append("rsvpstatus = :1")

		iCounter = 1

		for whereClause in whereClauses:
			whereClausesTransformed.append(whereClause.replace(":1", ":" + str(iCounter)))
			iCounter = iCounter + 1

		whereClause = ""
		if len(whereClausesTransformed) > 0:
			whereClause = "WHERE " + " AND ".join(whereClausesTransformed)

		guests = db.GqlQuery("SELECT * FROM Guest " + whereClause + " ORDER BY side, type, lastname, name", *queryArguments)

		template_values = {
			'logout_url': users.create_logout_url('/wedding'),
			'guests': guests,
		}

		path = os.path.join(os.path.dirname(__file__), 'guests.html')

		if (self.request.headers['Accept'] == "text/xml" or self.request.path.endswith(".xml")):
			path = os.path.join(os.path.dirname(__file__), 'guests.xml')
			self.response.headers['Content-Type'] = 'text/xml'

		self.response.out.write(template.render(path, template_values))

class GuestR(webapp.RequestHandler):
	@loginRequired
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

	@loginRequired
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

	@loginRequired
	def delete(self, key):
		guest = db.get(db.Key(key))
		guest.delete()

		self.redirect('/wedding/guests')

class AddGuest(webapp.RequestHandler):
	@loginRequired
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'guests-add.html')
		self.response.out.write(template.render(path, {}))

	@loginRequired
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

class Statistics(webapp.RequestHandler):
	@loginRequired
	def get(self):

		guests = db.GqlQuery("SELECT * FROM Guest")

		totalExpected = 0
		totalPotential = 0
		totalEntities = 0
		rsvpPositiveEntities = 0
		rsvpNegativeEntities = 0
		rsvpNotResponded = 0
		rsvpCount = 0
		# How much the estimate was off by. Positive
		#   means more people RSVPd than we expected
		#   and negative means less people RSVPd than
		#   we expected
		rsvpExpectedDelta = 0
		nonRsvpPotential = 0
		nonRsvpExpected = 0

		for guest in guests:

			totalPotential += guest.invited
			totalExpected += guest.expected
			totalEntities += 1

			if guest.rsvpstatus == "Yes":
				rsvpExpectedDelta += guest.rsvpcount - guest.expected

				if guest.rsvpcount == 0:
					rsvpNegativeEntities += 1
				else:
					rsvpPositiveEntities += 1
					rsvpCount += guest.rsvpcount
			else:
				rsvpNotResponded += 1
				nonRsvpPotential += guest.invited
				nonRsvpExpected += guest.expected

		template_values = {
			'totalExpected': totalExpected,
			'totalPotential': totalPotential,
			'totalEntities': totalEntities,
			'rsvpTotalEntities': rsvpPositiveEntities + rsvpNegativeEntities,
			'rsvpPositiveEntities': rsvpPositiveEntities,
			'rsvpNegativeEntities': rsvpNegativeEntities,
			'rsvpNotResponded': rsvpNotResponded,
			'rsvpCount': rsvpCount,
			'rsvpExpectedDelta': rsvpExpectedDelta,
			'nonRsvpPotential': nonRsvpPotential,
			'nonRsvpExpected': nonRsvpExpected,
			'guestEstimate': rsvpCount + nonRsvpExpected,
		}

		path = os.path.join(os.path.dirname(__file__), 'statistics.html')

		self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
	[
		('/wedding', Home),
		('/wedding/guests(?:\.xml)?', Guests),
		('/wedding/guest/([^/]*)', GuestR),
		('/wedding/guests/add', AddGuest),
		('/wedding/statistics', Statistics),
	],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
