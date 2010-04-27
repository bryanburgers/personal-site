import cgi
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
	text = db.TextProperty()

def write_date(date, writer):
        writer.write('<date id="/date/%i">' % date.key().id() )
        writer.write('<year>' + str(date.year) + '</year>')
        writer.write('<month>' + str(date.month) + '</month>')
        writer.write('<day>' + str(date.day) + '</day>')
        writer.write('<text><![CDATA[' + date.text + ']]></text>')
        writer.write('</date>')

class DateHandler(webapp.RequestHandler):

	def get(self, identifier):
                try:
                        date = Date.get_by_id(int(identifier))
                        
        		self.response.headers['Content-Type'] = "application/xml"
                        write_date(date, self.response.out)
        	except:
                        self.response.out.write('<result>Fail</result>')

        def post(self, identifier):
                try:
                        date = Date.get_by_id(int(identifier))

                        year = self.request.get('year', None)
                        month = self.request.get('month', None)
                        day = self.request.get('day', None)
                        text = self.request.get('text', None)
                        
                        write = False
                      
                        if year <> None:
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
                                self.response.out.write('<html><body>OK</body></html>')
                        else:
                                self.response.out.write('<html><body>No correct parameter specified</body></html>')                                
                except:
                        self.response.out.write('<html><body>Fail</body></html>')

class DatesHandler(webapp.RequestHandler):

        def get(self):
                dates = Date.all().order('year').order('month').order('day')

                self.response.headers['Content-Type'] = 'application/xml'
                self.response.out.write('<dates xmlns="tag:bryan-burgers.appspot.com,2010:dates">')

                for date in dates:
                        write_date(date, self.response.out)
                
                self.response.out.write('</dates>')

        def post(self):

                year = int(self.request.get('year'))
                month = int(self.request.get('month'))
                day = int(self.request.get('day'))
                text = self.request.get('text')

                date = Date(year=year, month=month, day=day, text=text)
                date.put()

                self.response.out.write('<html><body>OK</body></html>')

class DatesIcsHandler(webapp.RequestHandler):

        def get(self):
                self.response.header['Content-Type'] = 'text/calendar'

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
'''
                dates = Date.all().order('year').order('month').order('day')
                for date in dates:
                        self.response.out.write('''BEGIN:VEVENT
DTSTART;VALUE=DATE:%s
DTEND;VALUE=DATE:%s
UID:/date/%i
STATUS:CONFIRMED
SUMMARY:%s
END:VEVENT
'''

                self.response.out.write('END:VCALENDAR')
                                                
application = webapp.WSGIApplication(
	[
		('/date/(.*)', DateHandler),
		('/dates', DatesHandler),
                ('/dates.ics', DatesIcsHandler),
	],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
