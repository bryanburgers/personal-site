import datetime
import logging

from xml.dom.minidom import parseString

from google.appengine.api import urlfetch
from google.appengine.api import xmpp
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

chatbot_name = 'reminder-bot@bryan-burgers.appspotchat.com'
wikibot_name = 'wikipedia-bot@bryan-burgers.appspotchat.com'
testbot_name = 'test-bot@bryan-burgers.appspotchat.com'

class Reminder(db.Model):
        recipient = db.StringProperty(required=True)
        text = db.StringProperty(required=True)
        enabled = db.BooleanProperty()
        
class WikipediaWatchlist(db.Model):
        recipient = db.StringProperty(required=True)
        enabled = db.BooleanProperty()
        username = db.StringProperty()
        password = db.StringProperty()
        lastcheck = db.DateTimeProperty()

class Remind(webapp.RequestHandler):
        def get(self):
                reminders = Reminder.all().filter('enabled =', True).fetch(1000)
                for reminder in reminders:
                        if xmpp.get_presence(reminder.recipient, from_jid=chatbot_name):
                                xmpp.send_message(reminder.recipient, reminder.text, from_jid=chatbot_name)
                        else:
                                logging.info(reminder.recipient + ' was not online.')
                                
class WikipediaCronHandler(webapp.RequestHandler):
        def get(self):
                watchlist = WikipediaWatchlist.all().filter('enabled =', True).fetch(1000)
                for wikiwatch in watchlist:
                        if xmpp.get_presence(wikiwatch.recipient, from_jid=wikibot_name):
                                taskqueue.add(url='/_ah/bot/wikipedia/login/' + str(wikiwatch.key().id()), method='GET')
                                

class WikipediaLoginHandler(webapp.RequestHandler):
        def get(self, parameter):
                wikiwatch = WikipediaWatchlist.get_by_id(int(parameter))
                if wikiwatch == None:
                        return

                response = urlfetch.fetch(
                        url='http://en.wikipedia.org/w/api.php?action=login&format=xml',
                        payload='lgname=' + wikiwatch.username + '&lgpassword=' + wikiwatch.password,
                        method=urlfetch.POST,
                        headers={'Content-Type': 'application/x-www-form-urlencoded'})

                doc = parseString(response.content)
                login = doc.documentElement.firstChild
                result = login.getAttribute("result")
                userid = login.getAttribute("lguserid")
                username = login.getAttribute("lgusername")
                token = login.getAttribute("lgtoken")
                cookieprefix = login.getAttribute("cookieprefix")
                sessionid = login.getAttribute("sessionid")

                
                url = '/_ah/bot/wikipedia/watchlist/' + parameter
                payload = str('userid=' + userid + '&username=' + username + '&token=' + token + '&cookieprefix=' + cookieprefix + '&sessionid=' + sessionid)
                logging.info(payload)
                taskqueue.add(url=url + '?' + payload, method='GET')

class WikipediaWatchlistHandler(webapp.RequestHandler):
        def get(self, parameter):
                wikiwatch = WikipediaWatchlist.get_by_id(int(parameter))
                if wikiwatch == None:
                        return

                result = self.request.get('result')
                userid = self.request.get('userid')
                username = self.request.get('username')
                token = self.request.get('token')
                cookieprefix = self.request.get('cookieprefix')
                sessionid = self.request.get('sessionid')
                
                cookie = cookieprefix + 'UserName=' + username
                cookie += '; ' + cookieprefix + 'UserID=' + userid
                cookie += '; ' + cookieprefix + 'Token=' + token
                cookie += '; ' + cookieprefix + '_session' + sessionid

                lastchecktime = wikiwatch.lastcheck.strftime("%Y-%m-%dT%H:%M:%SZ")
                response = urlfetch.fetch(
                        url='http://en.wikipedia.org/w/api.php?action=query&list=watchlist&format=xml&wlexcludeuser=' + username + '&wlprop=user|comment|timestamp|title|flags|ids&wldir=newer&wlstart=' + lastchecktime,
                        method=urlfetch.GET,
                        headers={
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'Cookie': cookie,
                                })

                doc = parseString(response.content)
                watchlistnode = None
                for node in doc.documentElement.firstChild.childNodes:
                        if node.localName == 'watchlist':
                                watchlistnode = node

                if watchlistnode <> None:
                        for node in watchlistnode.childNodes:
                                s = node.getAttribute('title') + ' was edited by ' + node.getAttribute('user') + ' at ' + node.getAttribute('timestamp')
                                s += '\r\nComment: ' + node.getAttribute('comment')
                                pageid = node.getAttribute('pageid')
                                revid = node.getAttribute('revid')
                                title = node.getAttribute('title')
                                title = title.replace(' ', '_')
                                url = 'http://en.wikipedia.org/w/index.php?title=' + title + '&curid=' + pageid + '&diff=' + revid
                                s += '\r\n' + url
                                xmpp.send_message(wikiwatch.recipient, s, from_jid=wikibot_name)

                wikiwatch.lastcheck = datetime.datetime.utcnow()
                wikiwatch.put()
                        
                                
class Chat(webapp.RequestHandler):
        def post(self):

                message = xmpp.Message(self.request.POST)
                bot = ChatBot()
                if message.to.lower() == chatbot_name.lower() or message.to.lower() == chatbot_name.lower() + '/bot':
                        bot = ReminderBot()
                if message.to.lower() == wikibot_name.lower() or message.to.lower() == wikibot_name.lower() + '/bot':
                        bot = WikipediaBot()
                if message.to.lower() == testbot_name.lower() or message.to.lower() == testbot_name.lower() + '/bot':
                        bot = TestBot()
                bot.chat(message)

class ChatBot:
        def chat(self, message):
                message.reply(message.to)
        
class ReminderBot(ChatBot):
        def chat(self, message):
                sender = message.sender.lower().split('/')[0]
                if message.command == 'on':
                        try:
                                reminder = Reminder.all().filter('recipient =', sender).get()
                                if reminder == None:
                                        reminder = Reminder(recipient=sender, text='Alarm', enabled=True)
                                        reminder.put()
                                        message.reply("All signed up; you should be good to go. Type '/help' for help or '/off' to stop receiving reminders.")
                                else:
                                        reminder.enabled = True
                                        if message.arg <> None:
                                                reminder.text = message.arg
                                        reminder.put()
                                        message.reply("I've updated your data. Next time I send you a reminder, I'll say:\r\n" + reminder.text)
                        except Exception, e:
                                message.reply('There was a bit of an error. Sorry.')
                                message.reply(e.message)
                                
                elif message.command == 'off':
                        try:
                                reminder = Reminder.all().filter('recipient =', sender).get()
                                if reminder == None:
                                        message.reply("I wasn't reminding you anyway. Oh well. Type '/on' to start getting reminders.")
                                else:
                                        reminder.enabled = False
                                        reminder.put()
                                        message.reply("OK, I won't send you reminders anymore. Type '/on' to get reminders again.")
                        except Exception, e:
                                message.reply('There was a bit of an error. Sorry.')
                                message.reply(e.message)
                                
                elif message.command == 'show':
                        try:
                                reminder = Reminder.all().filter('recipient =', sender).get()
                                if reminder == None:
                                        message.reply("Sorry bud, I don't know anything about you.")
                                else:
                                        text = ''
                                        if reminder.enabled:
                                                text += "Yep, you're currently receiving the reminder '" + reminder.text + "'"
                                        else:
                                                text += "Nope, you're not current receiving a reminder."
                                        message.reply(text)
                        except Exception, e:
                                message.reply('There was a bit of an error. Sorry.')
                                message.reply(e.message)

                elif message.command == 'whoami':
                        message.reply("Why, to me you appear to be '" + sender + "'")                                

                elif message.command == 'help':
                        message.reply("Reminder Bot")
                        message.reply('/on [text] - Start receiving reminders. If [text] is present, [text] is what will be sent to you.')
                        message.reply('/off - Stop receiving reminders.')
                        message.reply('/show - Show information about the reminders that you may or may not be receiving.')
                        message.reply('/whoami - I''ll tell you who you are in my eyes.')
                        message.reply('/help - Show this screen.')

                elif message.command <> None:
                        message.reply("Sorry bud, but I don't understand that command. Try '/help' for commands I do understand.")

                else:
                        message.reply("Yeah, I'm not exactly cognizant, so I don't know what's going on. Try '/help' to see what I do understand.")

class WikipediaBot(ChatBot):
        def chat(self, message):
                sender = message.sender.lower().split('/')[0]
                if message.command == 'on':
                        try:
                                wikiwatch = WikipediaWatchlist.all().filter('recipient =', sender).get()
                                if wikiwatch == None:
                                        wikiwatch = WikipediaWatchlist(recipient=sender, enabled=True)
                                        wikiwatch.lastcheck = datetime.datetime.utcnow()
                                        wikiwatch.put()
                                        message.reply("All signed up; you should be good to go. You should probably set your username and password, though. Type '/help' for help or '/quiet' to have me chill out for a while.")
                                else:
                                        wikiwatch.enabled = True
                                        wikiwatch.lastcheck = datetime.datetime.utcnow()
                                        wikiwatch.put()
                                        message.reply("I've updated your data.")
                        except Exception, e:
                                message.reply('There was a bit of an error. Sorry.')
                                message.reply(e.message)
                                
                elif message.command == 'quiet':
                        try:
                                wikiwatch = WikipediaWatchlist.all().filter('recipient =', sender).get()
                                if wikiwatch == None:
                                        message.reply("I wasn't watching your watchlist anyway. Oh well. Type '/on' to start getting reminders.")
                                else:
                                        wikiwatch.enabled = False
                                        wikiwatch.put()
                                        message.reply("OK, I won't send you reminders anymore. Type '/on' to get reminders again.")
                        except Exception, e:
                                message.reply('There was a bit of an error. Sorry.')
                                message.reply(e.message)
                                
                elif message.command == 'show':
                        try:
                                wikiwatch = WikipediaWatchlist.all().filter('recipient =', sender).get()
                                if wikiwatch == None:
                                        message.reply("Sorry bud, I don't know anything about you.")
                                else:
                                        text = ''
                                        if wikiwatch.enabled:
                                                text += "Yep, I'm currently watching your watchlist."
                                        else:
                                                text += "Nope, you asked me to be quiet."
                                        message.reply(text)
                        except Exception, e:
                                message.reply('There was a bit of an error. Sorry.')
                                message.reply(e.message)

                elif message.command == 'username':
                        try:
                                wikiwatch = WikipediaWatchlist.all().filter('recipient =', sender).get()
                                if wikiwatch == None:
                                        message.reply("Sorry bud, I don't know anything about you. Try '/on' first.")
                                else:
                                        wikiwatch.username = message.arg
                                        wikiwatch.put()
                                        message.reply("I've updated your data.")
                        except Exception, e:
                                message.reply('There was a bit of an error. Sorry.')
                                message.reply(e.message)

                elif message.command == 'password':
                        try:
                                wikiwatch = WikipediaWatchlist.all().filter('recipient =', sender).get()
                                if wikiwatch == None:
                                        message.reply("Sorry bud, I don't know anything about you. Try '/on' first.")
                                else:
                                        wikiwatch.password = message.arg
                                        wikiwatch.put()
                                        message.reply("I've updated your data.")
                        except Exception, e:
                                message.reply('There was a bit of an error. Sorry.')
                                message.reply(e.message)                                

                elif message.command == 'help':
                        message.reply("Wikipedia Watchlist Bot")
                        message.reply("/on - I'll start watching your watch list.")
                        message.reply("/off - I'll shut up for a while.")
                        message.reply("/show - I'll let ya know a little bit about the information I have on you.")
                        message.reply("/username [username] - Set your wikipedia username to [username].")
                        message.reply("/password [password] - Set your wikipedia password to [password]. (Yep, unfortunately I have to store this in my database.)")
                        message.reply("/help - Show this screen.")

                elif message.command <> None:
                        message.reply("Sorry bud, but I don't understand that command. Try '/help' for commands I do understand.")

                else:
                        message.reply("Yeah, I'm not exactly cognizant, so I don't know what's going on. Try '/help' to see what I do understand.")

class TestBot(ChatBot):
        def chat(self, message):
                logging.info(message.sender)
                logging.info(message.to)
                logging.info(message.body)
                                                
application = webapp.WSGIApplication(
	[
                ('/_ah/bot/wikipedia/cron/', WikipediaCronHandler),
                ('/_ah/bot/wikipedia/login/(.*)', WikipediaLoginHandler),
                ('/_ah/bot/wikipedia/watchlist/(.*)', WikipediaWatchlistHandler),
                ('/_ah/xmpp/message/reminders/', Remind),
		('/_ah/xmpp/message/chat/', Chat),
	],
	debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
