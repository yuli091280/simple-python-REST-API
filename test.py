import cherrypy
from cherrypy.test import helper

import json
import datetime

import server

class test(helper.CPWebCase):
	@staticmethod
	def setup_server():
		api, conf = server.server_setup()
		cherrypy.tree.mount(api, '/', conf)
		
	def postJson(self, url, json='', session_id='0'):
		length = str(len(json))
		headers = [('content-type','application/json'),('content-length',length),('cookie','session_id={}'.format(session_id))]
		self.getPage(url, headers=headers, method='POST', body=json)
		
	def getPageWithSessionId(self, url, session_id):
		headers = [('cookie','session_id={}'.format(session_id))]
		self.getPage(url, headers=headers)
		
	def login(self,username='user1',pw='password'):
		jsonStr = json.dumps({'username':username,'password':pw})
		self.postJson('/login',jsonStr)
		return self.cookies[0][1].split(';')[0].split('=')[1]
		
	def login_user2(self):
		return self.login('user2','abc123')
		
	def login_user3(self):
		return self.login('user3','qwerty')
	
	def test_index(self):
		self.getPage("/")
		self.assertStatus(404)
		
	def test_login_bad_credential(self):
		jsonStr = json.dumps({'username':'user','password':1})
		self.postJson('/login',jsonStr)
		self.assertStatus(401)
		jsonStr = json.dumps({'username':'user1','password':1})
		self.postJson('/login',jsonStr)
		self.assertStatus(401)
		jsonStr = json.dumps({'username':'user','password':'password'})
		self.postJson('/login',jsonStr)
		self.assertStatus(401)
		
	def test_login_bad_format(self):
		jsonStr = json.dumps({'hahaha':'user','password':'password'})
		self.postJson('/login',jsonStr)
		self.assertStatus(400)
		jsonStr = json.dumps({'username':'user','drowssap':'password'})
		self.postJson('/login',jsonStr)
		self.assertStatus(400)
		jsonStr = json.dumps({'hahaha':'user','drowssap':'password'})
		self.postJson('/login',jsonStr)
		self.assertStatus(400)
		
	def test_login_proper(self):
		self.login()
		self.assertStatus(200)
		
	def test_login_get(self):
		self.getPage('/login')
		self.assertStatus(405)
		
	def test_login_no_body(self):
		self.postJson('/login')
		self.assertStatus(400)
		
	def test_logout_bad(self):
		self.getPage('/logout')
		self.assertStatus(401)
		
	def test_logout_proper(self):
		s_id = self.login()
		self.getPageWithSessionId('/logout', s_id)
		self.assertStatus(200)
		
	def test_mood_get_proper(self):
		s_id = self.login()
		self.getPageWithSessionId('/mood', s_id)
		self.assertStatus(200)
		self.assertBody('{}')
		
	def test_mood_get_no_session(self):
		self.getPage('/mood')
		self.assertStatus(401)
		
	def test_mood_get_specific_date(self):
		s_id= self.login_user2()
		jsonStr = json.dumps({'mood': 'good enough'})
		self.postJson('/mood/1970-1-1', jsonStr, s_id)
		jsonStr = json.dumps({'mood': 'horrible'})
		self.postJson('/mood/1970-1-10', jsonStr, s_id)
		self.getPageWithSessionId('/mood/1970-1-1', s_id)
		expected = json.dumps({
			'mood':['good enough'],
			'streak':1
		})
		self.assertBody(expected)
		self.getPageWithSessionId('/mood/1970-1-10', s_id)
		expected = json.dumps({
			'mood':['horrible'],
			'streak':1
		})
		self.assertBody(expected)
		self.getPageWithSessionId('/mood/1970-1-9', s_id)
		self.assertStatus(404)
		
	def test_mood_get_route_incorrect(self):
		s_id = self.login()
		self.getPageWithSessionId('/mood/1970-1-1/1', s_id)
		self.assertStatus(404)
		self.getPageWithSessionId('/mood/1970-1-', s_id)
		self.assertStatus(404)
		self.getPageWithSessionId('/mood/aaaaa', s_id)
		self.assertStatus(404)
		
	def test_mood_post_bad_format(self):
		s_id = self.login()
		jsonStr = json.dumps({'stuff':'bad mood'})
		self.postJson('/mood', jsonStr, s_id)
		self.assertStatus(400)
		
	def test_mood_post_no_session(self):
		jsonStr = json.dumps({'mood': 'good enough'})
		self.postJson('/mood/1970-1-1', jsonStr)
		self.assertStatus(401)
		
	def test_mood_post_good(self):
		s_id = self.login()
		jsonStr = json.dumps({'mood': 'good enough'})
		self.postJson('/mood/1970-1-1', jsonStr, s_id)
		self.getPageWithSessionId('/mood', s_id)
		expected = json.dumps({'1970-01-01':{'mood':['good enough'],'streak':1}})
		self.assertBody(expected)
		
	def test_mood_post_route_incorrect(self):
		s_id = self.login()
		jsonStr = json.dumps({'mood': 'good enough'})
		self.postJson('/mood/1970-1-1/1', jsonStr, s_id)
		self.assertStatus(404)
		self.postJson('/mood/1970-1-', jsonStr, s_id)
		self.assertStatus(404)
		self.postJson('/mood/aaaaa', jsonStr, s_id)
		self.assertStatus(404)
		
	def test_mood_no_date(self):
		s_id = self.login_user3()
		jsonStr = json.dumps({'mood': 'good enough'})
		self.postJson('/mood', jsonStr, s_id)
		self.getPageWithSessionId('/mood', s_id)
		today = datetime.datetime.now().strftime('%Y-%m-%d')
		expected = json.dumps({
			today: {
				'mood':['good enough'],
				'streak': 1
			}
		})
		self.assertBody(expected)
	
	def test_mood_multiple(self):
		s_id = self.login_user2()
		jsonStr = json.dumps({'mood': 'bad'})
		self.postJson('/mood/1970-1-1', jsonStr, s_id)
		jsonStr = json.dumps({'mood': 'meh'})
		self.postJson('/mood/1970-1-2', jsonStr, s_id)
		self.getPageWithSessionId('/mood', s_id)
		expected = json.dumps({
			'1970-01-01': {
				'mood':['good enough','bad'],
				'streak':1
			},
			'1970-01-10': {
				'mood':['horrible'],
				'streak':1
			},
			'1970-01-02': {
				'mood': ['meh'],
				'streak':2
			}
		})
		self.assertBody(expected)
		
	def test_mood_streak_broken(self):
		s_id = self.login()
		jsonStr = json.dumps({'mood': 'terrible'})
		self.postJson('/mood/1970-1-2', jsonStr, s_id)
		jsonStr = json.dumps({'mood': 'meh'})
		self.postJson('/mood/1970-1-3', jsonStr, s_id)
		jsonStr = json.dumps({'mood': 'terrific'})
		self.postJson('/mood/1970-1-5', jsonStr, s_id)
		self.getPageWithSessionId('/mood', s_id)
		expected = json.dumps({
			'1970-01-01': {
				'mood':['good enough'],
				'streak':1
			},
			'1970-01-02': {
				'mood': ['terrible'],
				'streak':2
			},
			'1970-01-03': {
				'mood':['meh'],
				'streak':3
			},
			'1970-01-05': {
				'mood':['terrific'],
				'streak':1
			}
		})
		self.assertBody(expected)
		
	def test_mood_streak_connect(self):
		s_id = self.login()
		jsonStr = json.dumps({'mood': 'fine'})
		self.postJson('/mood/1970-1-6', jsonStr, s_id)
		jsonStr = json.dumps({'mood': 'acceptable'})
		self.postJson('/mood/1970-1-4', jsonStr, s_id)
		self.getPageWithSessionId('/mood', s_id)
		expected = json.dumps({
			'1970-01-01': {
				'mood':['good enough'],
				'streak':1
			},
			'1970-01-02': {
				'mood': ['terrible'],
				'streak':2
			},
			'1970-01-03': {
				'mood':['meh'],
				'streak':3
			},
			'1970-01-05': {
				'mood':['terrific'],
				'streak':5
			},
			'1970-01-06': {
				'mood':['fine'],
				'streak':6
			},
			'1970-01-04': {
				'mood': ['acceptable'],
				'streak':4
			}
		})
		self.assertBody(expected)