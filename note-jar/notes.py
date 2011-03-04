import cgi
import datetime
import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from django.utils import simplejson

def date_from_id(id):
        referenceDate = datetime.datetime(1970, 1, 1)
        return referenceDate + datetime.timedelta(id)
def id_from_date(date):
        referenceDate = datetime.datetime(1970, 1, 1)
        return (date - referenceDate).days

class Note(db.Model):
        id = db.IntegerProperty()
        title = db.StringProperty()
        text = db.StringProperty()

        def to_data(self):
                return {
                        'id': self.id,
                        'title': self.title,
                        'text': self.text,
                        'date': str(self.date),
                        }

        def get_date(self):
                return date_from_id(self.id)

        date = property(get_date)

class DataHandler(webapp.RequestHandler):

	def get(self):
                notes = Note.all().order('id')

                result = {
                        'notes': [ note.to_data() for note in notes.fetch(1000) ]
                }

                self.response.headers["Content-Type"] = "application/json"
                self.response.out.write(simplejson.dumps(result, indent=2))                

        def post(self):
                innote = simplejson.loads(self.request.body)
                id = int(innote['id'])
                title = innote['title']
                text = innote['text']

                note = Note()
                note.id = id
                note.title = title
                note.text = text
                note.put()

                self.redirect('/notes/data.json')

application = webapp.WSGIApplication(
	[
                ('/notes/data.json', DataHandler),
#		('/notes/', NotesHandler),
#		('/notes', NotesHandler),
	],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
