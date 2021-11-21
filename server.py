import cherrypy

import string
import datetime

import user_database

ADDR = 'localhost'
PORT = 8000

class my_api(object):
	@cherrypy.expose
	def index(self):
		return open('index.html')
	
	@cherrypy.expose
	def mood_page(self):
		return open('mood_page.html')
	
	@cherrypy.expose
	def logout(self):
		if 'name' in cherrypy.session:
			cherrypy.session.pop('name')
			return 'logged out'
		else:
			raise cherrypy.HTTPError(401)

@cherrypy.expose
class login(object):
	@cherrypy.tools.accept(media='application/json')
	@cherrypy.tools.json_in()
	def POST(self):
		data = cherrypy.request.json
		print(data)
		if 'username' not in data or 'password' not in data:
			raise cherrypy.HTTPError(400)
		username = data['username']
		password = data['password']
		user = database.get_user(username)
		if user is not None and user.check_password(password):
			cherrypy.session['name'] = username
		else:
			raise cherrypy.HTTPError(
				401,
				'invalid username or password'
			)

@cherrypy.expose
class mood(object):
	def check_name(self):
		if 'name' in cherrypy.session:
			return cherrypy.session['name']
		else:
			return None

	def _cp_dispatch(self, vpath):
		print(vpath)
		if len(vpath) == 1:
			date = vpath.pop()
		cherrypy.request.params['date_str'] = date
		return self

	@cherrypy.tools.accept(media='application/json')
	@cherrypy.tools.json_out()
	def GET(self, date_str=""):
		username = self.check_name()
		if username is None:
			raise cherrypy.HTTPError(401)
		user = database.get_user(username)
		date = None
		try:
			tokens = date_str.split('-')
			y = int(tokens[0])
			m = int(tokens[1])
			d = int(tokens[2])
			date = datetime.datetime(y,m,d)
		except:
			return user.get_moods_record()
		moods = user.get_mood(date)
		if moods is None:
			raise cherrypy.HTTPError(404)
		return moods
			
	@cherrypy.tools.accept(media='application/json')
	@cherrypy.tools.json_in()
	def POST(self, date_str=""):
		data = cherrypy.request.json
		username = self.check_name()
		if username is None:
			raise cherrypy.HTTPError(401)
		if 'mood' not in data:
			raise cherrypy.HTTPError(400)
		date = datetime.datetime.now()
		try:
			tokens = date_str.split('-')
			y = int(tokens[0])
			m = int(tokens[1])
			d = int(tokens[2])
			date = datetime.datetime(y,m,d)
		except:
			pass
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
