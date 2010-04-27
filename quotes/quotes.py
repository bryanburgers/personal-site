import cgi
import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class Quote(db.Model):
	text   = db.StringProperty()
	source = db.StringProperty()

class Quotes(webapp.RequestHandler):

	def get(self):
		count = 10
		page = self.request.get("page", 1)
		offset = (page - 1) * count

		quotesGql = Quote.all().fetch(count + 1, offset=offset)

		template_values = {
			'page': '/quotes?page=' + str(page),
			'quotes': quotesGql,
		}

		if page > 1:
			template_values['prev_page'] = '/quotes?page=' + str(page - 1)
		if len(quotesGql) == count:
			tempalte_values['next_page'] = '/quotes?page=' + str(page + 1)


		path = os.path.join(os.path.dirname(__file__), 'quotes.html')
		self.response.out.write(template.render(path, template_values))

	def post(self):
		quote = Quote()
		quote.source = self.request.get("source", "")
		quote.text = self.request.get("text", "")
		quote.put()

		self.response.redirect('/quotes')

#
#class GuestR(webapp.RequestHandler):
#	@loginRequired
#	def get(self, key):
#		
#		if (self.request.get('mode') == 'edit'):
#			self.getEdit(key)
#		else:
#			self.getView(key)
#
#	def getView(self, key):
#		guest = db.get(db.Key(key))
#
#		template_values = {
#			'guest': guest,
#		}
#
#		path = os.path.join(os.path.dirname(__file__), 'guest.html')
#		self.response.out.write(template.render(path, template_values))
#	
#	def getEdit(self, key):
#		guest = db.get(db.Key(key))
#
#		template_values = {
#			'guest': guest,
#		}
#
#		path = os.path.join(os.path.dirname(__file__), 'edit.html')
#		self.response.out.write(template.render(path, template_values))
#
#	@loginRequired
#	def post(self, key):
#		guest = db.get(db.Key(key))
#
#		edit = self.request.get('edit', default_value = None)
#		delete = self.request.get('delete', default_value = None)
#
#		if (not(delete == None)):
#			self.delete(key)
#			return
#
#		name = self.request.get('name', default_value = None)
#		lastname = self.request.get('lastname', default_value = None)
#		children = self.request.get('children', default_value = None)
#		address = self.request.get('address', default_value = None)
#		side = self.request.get('side', default_value = None)
#		type = self.request.get('type', default_value = None)
#		invited = self.request.get('invited', default_value = None)
#		expected = self.request.get('expected', default_value = None)
#		rsvpstatus = self.request.get('rsvpstatus', default_value = None)
#		rsvpcount = self.request.get('rsvpcount', default_value = None)
#
#		if (not(name == None)):
#			guest.name = name
#		if (not(lastname == None)):
#			guest.lastname = lastname
#		if (not(children == None)):
#			guest.children = children
#		if (not(address == None)):
#			guest.address = address
#		if (not(side == None)):
#			guest.side = side
#		if (not(type == None)):
#			guest.type = type
#		if (not(invited == None)):
#			try:
#				guest.invited = int(invited)
#			except:
#				pass
#		if (not(expected == None)):
#			try:
#				guest.expected = int(expected)
#			except:
#				pass
#		if (not(rsvpstatus == None)):
#			guest.rsvpstatus = rsvpstatus
#		if (not(rsvpcount == None)):
#			try:
#				guest.rsvpcount = int(rsvpcount)
#			except:
#				pass
#
#		guest.put()
#
#		self.redirect('/wedding/guest/' + key)
#
#	@loginRequired
#	def delete(self, key):
#		guest = db.get(db.Key(key))
#		guest.delete()
#
#		self.redirect('/wedding/guests')
#
#class AddGuest(webapp.RequestHandler):
#	@loginRequired
#	def get(self):
#		path = os.path.join(os.path.dirname(__file__), 'guests-add.html')
#		self.response.out.write(template.render(path, {}))
#
#	@loginRequired
#	def post(self):
#		guest = Guest()
#
#		name = self.request.get('name', default_value = None)
#		lastname = self.request.get('lastname', default_value = None)
#		children = self.request.get('children', default_value = None)
#		address = self.request.get('address', default_value = None)
#		side = self.request.get('side', default_value = None)
#		type = self.request.get('type', default_value = None)
#		invited = self.request.get('invited', default_value = None)
#		expected = self.request.get('expected', default_value = None)
#		rsvpstatus = self.request.get('rsvpstatus', default_value = None)
#		rsvpcount = self.request.get('rsvpcount', default_value = None)
#
#		if (not(name == None)):
#			guest.name = name
#		if (not(lastname == None)):
#			guest.lastname = lastname
#		if (not(children == None)):
#			guest.children = children
#		if (not(address == None)):
#			guest.address = address
#		if (not(side == None)):
#			guest.side = side
#		if (not(type == None)):
#			guest.type = type
#		if (not(invited == None)):
#			try:
#				guest.invited = int(invited)
#			except:
#				pass
#		if (not(expected == None)):
#			try:
#				guest.expected = int(expected)
#			except:
#				pass
#		if (not(rsvpstatus == None)):
#			guest.rsvpstatus = rsvpstatus
#		if (not(rsvpcount == None)):
#			try:
#				guest.rsvpcount = int(rsvpcount)
#			except:
#				pass
#
#		guest.put()
#		self.redirect('/wedding/guests')
#
#class Statistics(webapp.RequestHandler):
#	@loginRequired
#	def get(self):
#
#		guests = db.GqlQuery("SELECT * FROM Guest")
#
#		totalEntities = 0
#		totalExpected = 0
#		totalInvited = 0
#
#		rsvpPositiveEntities = 0
#		rsvpPositiveExpected = 0
#		rsvpPositiveCount = 0
#
#		rsvpNegativeEntities = 0
#		rsvpNegativeExpected = 0
#		rsvpNegativeCount = 0
#
#		nonRsvpEntities = 0
#		nonRsvpExpected = 0
#		nonRsvpInvited = 0
#
#		for guest in guests:
#
#			totalEntities += 1
#			totalExpected += guest.expected
#			totalInvited += guest.invited
#
#			if guest.rsvpstatus == "Yes":
#				if guest.rsvpcount == 0:
#					rsvpNegativeEntities += 1
#					rsvpNegativeExpected += guest.expected
#				else:
#					rsvpPositiveEntities += 1
#					rsvpPositiveCount += guest.rsvpcount
#					rsvpPositiveExpected += guest.expected
#			else:
#				nonRsvpEntities += 1
#				nonRsvpInvited += guest.invited
#				nonRsvpExpected += guest.expected
#
#		rsvpCount = rsvpPositiveCount + rsvpNegativeCount
#		rsvpExpected = rsvpPositiveExpected + rsvpNegativeExpected
#
#		template_values = {
#			'totalEntities': totalEntities,
#			'totalExpected': totalExpected,
#			'totalInvited': totalInvited,
#			'rsvpEntities': rsvpPositiveEntities + rsvpNegativeEntities,
#			'rsvpPositiveEntities': rsvpPositiveEntities,
#			'rsvpPositiveExpected': rsvpPositiveExpected,
#			'rsvpPositiveCount': rsvpPositiveCount,
#			'rsvpPositiveDiff': rsvpPositiveCount - rsvpPositiveExpected,
#			'rsvpNegativeEntities': rsvpNegativeEntities,
#			'rsvpNegativeExpected': rsvpNegativeExpected,
#			'rsvpNegativeCount': rsvpNegativeCount,
#			'rsvpNegativeDiff': rsvpNegativeCount - rsvpNegativeExpected,
#			'rsvpDiff': rsvpCount - rsvpExpected,
#			'nonRsvpEntities': nonRsvpEntities,
#			'nonRsvpExpected': nonRsvpExpected,
#			'nonRsvpInvited': nonRsvpInvited,
#			'currentExpected': rsvpCount + nonRsvpExpected,
#			'currentInvited': rsvpCount + nonRsvpInvited,
#		}
#
#		path = os.path.join(os.path.dirname(__file__), 'statistics.html')
#
#		self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
	[
		('/quotes', Quotes),
#		('/wedding/guests(?:\.xml|\.csv)?', Guests),
#		('/wedding/guest/([^/]*)', GuestR),
#		('/wedding/guests/add', AddGuest),
#		('/wedding/statistics', Statistics),
	],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
