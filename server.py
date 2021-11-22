import cherrypy

import string
import datetime

import user_database

ADDR = 'localhost'
PORT = 8000

class my_api(object):
	# uncomment these to use index and mood_page for testing
	# some test will fail if these are uncommented, that's expected
	# the api should still function normally
	'''
	@cherrypy.expose
	def index(self):
		return open('index.html','r')
		
	@cherrypy.expose
	def mood_page(self):
		return open('mood_page.html', 'r')
	'''

	@cherrypy.expose
	def logout(self):
		if 'name' in cherrypy.session:
			cherrypy.session.pop('name')
		else:
			raise cherrypy.HTTPError(401)

@cherrypy.expose
class login(object):
	@cherrypy.tools.accept(media='application/json')
	@cherrypy.tools.json_in()
	def POST(self):
		data = cherrypy.request.json
		if 'username' not in data or 'password' not in data:
			cherrypy.response.status = 400
			return
		username = data['username']
		password = data['password']
		user = database.get_user(username)
		if user is not None and user.check_password(password):
			cherrypy.session['name'] = username
		else:
			cherrypy.response.status = 401

@cherrypy.expose
class mood(object):
	def check_name(self):
		if 'name' in cherrypy.session:
			return cherrypy.session['name']
		else:
			return None

	def parse_date(self, date_str):
		tokens = date_str.split('-')
		y = int(tokens[0])
		m = int(tokens[1])
		d = int(tokens[2])
		return datetime.datetime(y,m,d)

	def _cp_dispatch(self, vpath):
		if len(vpath) == 1:
			date = vpath.pop()
			cherrypy.request.params['date_str'] = date
		elif len(vpath) > 1:
			cherrypy.request.params['date_str'] = 'a'
		return self

	@cherrypy.tools.accept(media='application/json')
	@cherrypy.tools.json_out()
	def GET(self, date_str="", other=None):
		username = self.check_name()
		if username is None:
			cherrypy.response.status = 401
			return
		user = database.get_user(username)
		if date_str == "":
			return user.get_moods_record()
		try:
			date = self.parse_date(date_str)
		except:
			cherrypy.response.status = 404
			return
		moods = user.get_mood(date)
		if moods is None:
			cherrypy.response.status = 404
			return
		return moods
			
	@cherrypy.tools.accept(media='application/json')
	@cherrypy.tools.json_in()
	def POST(self, date_str=""):
		data = cherrypy.request.json
		username = self.check_name()
		if username is None:
			cherrypy.response.status = 401
			return
		if 'mood' not in data:
			cherrypy.response.status = 400
			return
		if date_str == '':
			date = datetime.datetime.now()
		else:
			try:
				date = self.parse_date(date_str)
			except:
				cherrypy.response.status = 404
				return
		user = database.get_user(username)
		user.add_mood(date, data['mood'])

def bind_to_socket(addr = ADDR, port=PORT): # pragma: no cover
	cherrypy.config.update({
		'server.socket_port': port,
		'server._socket_host': addr
	})

def server_setup():
	global database 
	database = user_database.make_mock_database()
	conf = {
		'/': {
			'tools.sessions.on': True,
		},
		'/mood': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.response_headers.on': True,
			'tools.response_headers.headers': [('Content-Type', 'application/json')]
		},
		'/login': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.response_headers.on': True,
			'tools.response_headers.headers': [('Content-Type', 'application/json')]
		}
	}
	api = my_api()
	my_api.mood = mood()
	my_api.login = login()
	return api, conf
	
def main(): # pragma: no cover
	bind_to_socket()
	api, conf = server_setup()
	cherrypy.quickstart(api, '/', conf)

if __name__ == '__main__': # pragma: no cover
	main()
