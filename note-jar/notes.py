import cgi
import datetime
import random
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

        def to_website_data(self):
                data = self.to_data()
                data['editUrl'] = '/notes/id/' + str(self.id)
                return data

        def get_date(self):
                return date_from_id(self.id)

        date = property(get_date)

class RandomNote(db.Model):
        title = db.StringProperty()
        text = db.StringProperty()
        rand = db.FloatProperty()

        def to_data(self):
                return {
                        'rand': self.rand,
                        'title': self.title,
                        'text': self.text,
                        }

class RedirectHandler(webapp.RequestHandler):
        def __init__(self, location):
                self.location = location

        def get(self):
                self.redirect(self.location)
                
class HomeRedirect(webapp.RequestHandler):
        def get(self):
                self.redirect('notes/')
                
class HomeHandler(webapp.RequestHandler):
        def get(self):

                nowid = id_from_date(datetime.datetime.now())
                
                upcomingNotes = Note.all().filter('id >=', nowid).order('id').fetch(5)
                randomNotes = RandomNote.all().filter('rand >', random.random()).order('rand').fetch(5)
                if len(randomNotes) < 5:
                        moreRandomNotes = RandomNote.all().order('rand').fetch(5 - len(randomNotes))
                        randomNotes.extend(moreRandomNotes)

                template_values = {
                        'upcomingNotes': [ note.to_website_data() for note in upcomingNotes ],
                        'randomNotes': [ note.to_data() for note in randomNotes ],                        
                }

               	path = os.path.join(os.path.dirname(__file__), 'home.html')
		self.response.out.write(template.render(path, template_values))


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

class NoteIdHandler(webapp.RequestHandler):

        def get(self, id):                        
                note = Note.all().filter('id =', int(id)).get()
                noteData = None
                if note == None:
                        noteData = {
                                'id': int(id),
                                'title': '',
                                'text': ''
                        }
                else:
                        noteData = note.to_data()

                template_values = {
                        'postLocation': self.request.url,
                        'note': noteData,
                }
                
               	path = os.path.join(os.path.dirname(__file__), 'note.html')
		self.response.out.write(template.render(path, template_values))

	def post(self, id):
                note = Note.all().filter('id =', int(id)).get()
                if note == None:
                        note = Note()
                        note.id = int(id)

                note.title = self.request.get('title', '')
                note.text = self.request.get('text', '')
                note.put()
                
                self.redirect('../')

class NoteDateHandler(webapp.RequestHandler):

        def get(self, year, month, day):
                id = id_from_date(datetime.datetime(int(year), int(month), int(day)))
                self.redirect('../id/' + str(id))

application = webapp.WSGIApplication(
	[
                ('/notes', HomeRedirect),
		('/notes/', HomeHandler),
                ('/notes/data.json', DataHandler),
                ('/notes/id/([0-9]+)', NoteIdHandler),
                ('/notes/date/([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})', NoteDateHandler),
#		('/notes', NotesHandler),
	],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
