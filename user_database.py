'''
This entire database is bad. Don't do this in production, ever.
'''
import datetime

class user:
	def __init__(self, name, password):
		self._name = name
		self._password = password	# storing pw in plaintext is bad
		self._mood_record = {}
		
	def add_mood(self, date, mood):
		yesterday = date - datetime.timedelta(days=1)
		yesterday_str = yesterday.strftime("%Y-%m-%d")
		date_str = date.strftime("%Y-%m-%d")
		if yesterday_str in self._mood_record:
			streak = self._mood_record[yesterday_str]['streak']+1
		else:
			streak = 1
		self._update_streak(date, streak)
		if date_str in self._mood_record:
			today = self._mood_record[date_str]
			try:
				today['mood'].index(mood)
			except:
				today['mood'].append(mood)
			today['streak'] = streak
		else:
			self._mood_record[date_str] = {'mood': [mood], 'streak':streak}
			
	def get_mood(self, date):
		date_str = date.strftime("%Y-%m-%d")
		return self._mood_record[date_str]
		
	def check_password(self, password):
		return self._password == password
		
	def get_moods_record(self):
		return self._mood_record
		
	def _update_streak(self, date, streak):
		tomorrow = date + datetime.timedelta(days=1)
		tomorrow_str = tomorrow.strftime("%Y-%m-%d")
		while tomorrow_str in self._mood_record:
			streak += 1
			self._mood_record[tomorrow_str]['streak'] = streak
			tomorrow = tomorrow + datetime.timedelta(days=1)
			tomorrow_str = tomorrow.strftime("%Y-%m-%d")

class database:
	def __init__(self):
		self._users = {}
		
	def add_user(self,username,password):
		self._users[username] = user(username, password)
		
	def get_user(self, username):
		if username in self._users:
			return self._users[username]
		else:
			return None
		
def make_mock_database():
	my_database = database()
	my_database.add_user("user1","password")
	my_database.add_user("user2","abc123")
	my_database.add_user("user3","qwerty")
	return my_database
	