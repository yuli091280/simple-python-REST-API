import requests
import json

TARGET = "http://localhost:8000"

def post_to_server(jsonStr, target=TARGET, s=requests ):
	length = len(jsonStr.encode('utf-8'))
	r = s.post(target, jsonStr,headers={'Content-type':'application/json', 'Content-length': bytes(length)})
	return r

def main():
	# login test
	print("testing bad credentials")
	jsonStr = json.dumps({'username':'user','password':1})
	print(post_to_server(jsonStr, TARGET+"/login"))
	jsonStr = json.dumps({'username':'user1','password':1})
	print(post_to_server(jsonStr, TARGET+"/login"))
	jsonStr = json.dumps({'username':'user','password':'password'})
	print(post_to_server(jsonStr, TARGET+"/login"))
	print("making new session")
	s = requests.Session()
	print("logging in with proper credential")
	jsonStr = json.dumps({'username':'user1','password':'password'})
	print(post_to_server(jsonStr, TARGET+"/login", s))
	print("attempt to logout twice")
	print(s.get(TARGET + "/logout"))
	print(s.get(TARGET + "/logout"))
	print("login and get /mood")
	jsonStr = json.dumps({'username':'user1','password':'password'})
	print(post_to_server(jsonStr, TARGET+"/login",s))
	print(s.get(TARGET + "/mood").text)
	print("post /mood with bad json")
	jsonStr = json.dumps({'stuff':'bad mood'})
	print("json body:\n%s" %jsonStr)
	print(post_to_server(jsonStr, TARGET+"/mood",s))
	print("post /mood with a json without date")
	jsonStr = json.dumps({'mood': 'good enough'})
	print("json body:\n%s" %jsonStr)
	print(post_to_server(jsonStr, TARGET+"/mood",s))
	print("check mood record with get /mood")
	print(s.get(TARGET+"/mood").text)
	
if __name__ == "__main__":
	main()