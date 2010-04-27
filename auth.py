import base64
import cgi
import datetime
import random
import sha
import string

from google.appengine.ext import db

class User(db.Model):
	email      = db.StringProperty()
	password   = db.StringProperty()
	salt       = db.StringProperty()

def hash_password(password, salt):
	joined = password + '$1$' + salt
	hashed = sha.sha(joined).digest()
	encoded = base64.encodestring(hashed)
	trimmed = encoded.strip()
	return trimmed

def generate_salt(length=8):
	saltChars = './' + string.ascii_letters + string.digits
	saltCharsLength = len(saltChars)
	salt = ""
	for i in range(1,length):
		salt += saltChars[random.randint(0,saltCharsLength - 1)]
	return salt

def authorize_basic(self):
	if not self.request.headers.has_key("Authorization"):
		return None
	
	authorizeHeader = self.request.headers["Authorization"]

	if not authorizeHeader.startswith("Basic "):
		return None

	base64encoded = authorizeHeader.replace("Basic ", "", 1)
	decoded = base64.decodestring(base64encoded)
	if decoded.find(":") < 0:
		# If we don't have a colon, we can't split the user
		#   and the password, which means something is wrong.
		#   By default, when something is wrong, do not
		#   authorize.
		return None

	[email, password] = decoded.split(":", 1)

	query = db.GqlQuery("SELECT * FROM User WHERE email = :1", email)
	user = query.get()
	if user == None:
		return None

	if hash_password(password, user.salt) != user.password:
		return None

	return user

def authorize(self):
	user = authorize_basic(self)
	return user

def authorizationOptional(func):
	def wrapper(self, *args, **kw):
		user = authorize(self)
		self.request.authorized_user = user
		func(self, *args, **kw)
	return wrapper

def authorizationRequired(func):
	def wrapper(self, *args, **kw):
		user = authorize(self)
		if user == None:
			report_unauthorized(self.response)
		else:
			self.request.authorized_user = user
			func(self, *args, **kw)
	return wrapper

def report_unauthorized(response, status=401, message="Unauthorized", realm="league-manager"):
	response.set_status(status)
	response.headers['Content-Type'] = 'text/plain'
	response.headers['WWW-Authenticate'] = 'Basic realm="' + realm + '"'
	response.out.write("Unauthorized")
