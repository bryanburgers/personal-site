import cgi
import datetime
import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class Date(db.Model):
        year = db.IntegerProperty()
        month = db.IntegerProperty()
        day = db.IntegerProperty()
	text = db.StringProperty()

	def to_data(self):
                return {
                        'uri': self.uri,
                        'year': self.year,
                        'month': self.month,
                        'monthName': get_month_name(self.month),
                        'day': self.day,
                        'text': self.text,
                        }

        def get_uri(self):
                try:
                        return '/date/' + str(self.key().id())
                except:
                        return '/date/new'
        uri = property(get_uri)

def get_month_name(number):
        months = [
                'January',
                'February',
                'March',
                'April',
                'May',
                'June',
                'July',
                'August',
                'September',
                'October',
                'November',
                'December'
                ]
        return months[number - 1]

class DateHandler(webapp.RequestHandler):

	def get(self, identifier):
                try:
                        date = Date.get_by_id(int(identifier))
                        
                        template_values = {
                                'date': date.to_data(),
                                'postLocation': date.uri
                        }

                   	path = os.path.join(os.path.dirname(__file__), 'date.html')
        		self.response.out.write(template.render(path, template_values))
        	except:
                        self.response.out.write('<html><body>Not found</body></html>')

        def post(self, identifier):
                try:
                        date = Date.get_by_id(int(identifier))

                        year = self.request.get('year', None)
                        month = self.request.get('month', None)
                        day = self.request.get('day', None)
                        text = self.request.get('text', None)
                        
                        write = False

                        if year == '':
                                date.year = None
                                write = True
                        elif year <> None:
                                try:
                                        date.year = int(year)
                                        write = True
                                except:
                                        pass

                        if month <> None:
                                try:
                                        date.month = int(month)
                                        write = True
                                except:
                                        pass

                        if day <> None:
                                try:
                                        date.day = int(day)
                                        write = True
                                except:
                                        pass

                        if text <> None:
                                date.text = text
                                write = True

                        if write:
                                date.put()
                                self.redirect('/dates')
                        else:
                                self.response.out.write('<html><body>No correct parameter specified</body></html>')                                
                except:
                        self.response.out.write('<html><body>Fail</body></html>')

class NewDateHandler(webapp.RequestHandler):

	def get(self):
                date = Date(year=None, month=1, day=1, text="New date")
                        
                template_values = {
                        'date': date.to_data(),
                        'postLocation': '/dates'
                        }

                path = os.path.join(os.path.dirname(__file__), 'date.html')
        	self.response.out.write(template.render(path, template_values))        	

class DatesHandler(webapp.RequestHandler):

        def get(self):
                dates = Date.all().order('month').order('day').order('year')

                template_values = {
                        'dates': [ date.to_data() for date in dates.fetch(1000) ]
                }

           	path = os.path.join(os.path.dirname(__file__), 'dates.html')
		self.response.out.write(template.render(path, template_values))

        def post(self):

                try:
                        year = int(self.request.get('year', None))
                except:
                        year = None
                month = int(self.request.get('month'))
                day = int(self.request.get('day'))
                text = self.request.get('text')

                date = Date(year=year, month=month, day=day, text=text)
                date.put()

                self.redirect('/dates')

class DatesIcsHandler(webapp.RequestHandler):

        def get(self):
                self.response.headers['Content-Type'] = 'text/calendar'
                self.response.headers['Cache-Control'] = 'max-age=86400'

                self.response.out.write('''BEGIN:VCALENDAR
PRODID:-//Google Inc//Google Calendar 70.9054//EN
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Birthdays and Anniversaries
X-WR-TIMEZONE:America/Chicago
X-WR-CALDESC:
BEGIN:VTIMEZONE
TZID:America/Chicago
X-LIC-LOCATION:America/Chicago
BEGIN:DAYLIGHT
TZOFFSETFROM:-0600
TZOFFSETTO:-0500
TZNAME:CDT
DTSTART:19700308T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0500
TZOFFSETTO:-0600
TZNAME:CST
DTSTART:19701101T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
END:STANDARD
END:VTIMEZONE
'''.replace('\n', '\r\n'))
                dates = Date.all().order('year').order('month').order('day')
                today = datetime.date.today()
                for date in dates:
                        startdate = datetime.date(today.year, date.month, date.day)
                        if today > startdate:
                                startdate = datetime.date(today.year + 1, date.month, date.day)

                        for offset in [-1, 0, 1]:

                                uid = str(date.key().id()) + "o" + str(offset + 1) + "@bryan-burgers.appspot.com"
                                outdate = datetime.date(startdate.year + offset, startdate.month, startdate.day)
                                text = date.text
                                if date.year == None:
                                        text = date.text + ' (?)'
                                else:
                                        text = date.text + ' (' + str(outdate.year - date.year) + ')'
                                self.write_date(outdate, uid, text)

                self.response.out.write('END:VCALENDAR')

        def write_date(self, startdate, uid, text):
                enddate = startdate + datetime.timedelta(1)
                self.response.out.write('''BEGIN:VEVENT
DTSTART;VALUE=DATE:%s
DTEND;VALUE=DATE:%s
UID:%s
CLASS:PUBLIC
STATUS:CONFIRMED
TRANSP:TRANSPARENT
SUMMARY:%s
END:VEVENT
'''.replace('\n', '\r\n') % (startdate.strftime('%Y%m%d'), enddate.strftime('%Y%m%d'), uid, text))

class DatesTurtleHandler(webapp.RequestHandler):

        def get(self):
                self.response.headers['Content-Type'] = 'text/turtle'
                self.response.headers['Cache-Control'] = 'max-age=86400'

                self.response.out.write('''@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix foaf: <http://xmlns.com/foaf/0.1/>.
@prefix bio: <http://purl.org/vocab/bio/0.1/>.
@prefix rel: <http://purl.org/vocab/relationship/>.

''')

                dates = Date.all().order('year').order('month').order('day')
                today = datetime.date.today()
                for date in dates:
                        if not(date.year == None):
                                startdate = datetime.date(date.year, date.month, date.day)
                                self.response.out.write('''
[] a bio:Event;
   rdfs:label "%s";
   bio:date "%s".
''' % (date.text, startdate.strftime('%Y-%m-%d')))

                                                
application = webapp.WSGIApplication(
	[
                ('/date/new', NewDateHandler),
		('/date/(.*)', DateHandler),
		('/dates', DatesHandler),
                ('/dates.ics', DatesIcsHandler),
                ('/dates.ttl', DatesTurtleHandler),
	],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
