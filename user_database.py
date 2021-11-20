'''
This entire database is bad. Don't do this in production, ever.
'''

class user:
	def __init__(self, name, password):
		self._name = name
		self._password = password
		self._mood_record = {}
		
	def add_mood(self, date, mood):
		date_str = date.strftime("%Y-%m-%d")
		self._mood_record[date_str] = mood
		
	def get_mood(self, date):
		date_str = date.strftime("%Y-%m-%d")
		return self._mood_record[date_str]
		
	def check_password(self, password):
		return self._password == password
		
	def get_all_moods(self):
		return self._mood_record
		
class database:
	def __init__(self):
		self.users = {}
		
	def add_user(self,username,password):
		self.users[username] = user(username, password)
		
	def add_mood(self, username, date, mood):
		self.users[username].add_mood(date, mood)
		
def make_mock_database():
	my_database = database()
	my_database.add_user("user1","password")
	my_database.add_user("user2","abc123")
	return my_database
	