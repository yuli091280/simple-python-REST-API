import cherrypy

import string
import datetime

import user_database

ADDR = 'localhost'
PORT = 8000

class my_app(object):
	@cherrypy.expose
	def index(self):
		return open('index.html')
	
	@cherrypy.expose
	def mood_page(self):
		if 'name' in cherrypy.session:
			return open('mood_page.html')
		else:
			raise cherrypy.HTTPError(401)
	
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
		if not hasattr(cherrypy.request,'json'):
			raise cherrypy.HTTPError(400)
		data = cherrypy.request.json
		if 'username' not in data or 'password' not in data:
			raise cherrypy.HTTPError(400)
		username = data['username']
		password = data['password']
		if username in database.users and database.users[username].check_password(password):
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

	@cherrypy.tools.accept(media='application/json')
	@cherrypy.tools.json_out()
	def GET(self):
		username = self.check_name()
		if username is None:
			raise cherrypy.HTTPError(401)
		return database.users[username].get_all_moods()
			
	@cherrypy.tools.accept(media='application/json')
	@cherrypy.tools.json_in()
	def POST(self):
		if not hasattr(cherrypy.request,'json'):
			raise cherrypy.HTTPError(400)
		data = cherrypy.request.json
		username = self.check_name()
		if username is None:
			raise cherrypy.HTTPError(401)
		if 'mood' not in data:
			raise cherrypy.HTTPError(400)
		date = datetime.datetime.now()
		print(data)
		try:
			tokens = data['date'].split('-')
			y = int(tokens[0])
			m = int(tokens[1])
			d = int(tokens[2])
			date = datetime.datetime(y,m,d)
		except:
			pass
		database.users[username].add_mood(date, data['mood'])

if __name__ == '__main__':
	database = user_database.make_mock_database()
	cherrypy.config.update({
		'server.socket_port': PORT,
		'server._socket_host': ADDR
	})
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
	app = my_app()
	my_app.mood = mood()
	my_app.login = login()
	cherrypy.quickstart(app, '/', conf)
