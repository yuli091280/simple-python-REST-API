import requests
import json

TARGET = "http://localhost:8000"

def post_to_server(jsonStr, target=TARGET):
	length = len(jsonStr.encode('utf-8'))
	r = requests.post(target, jsonStr,headers={'Content-type':'application/json', 'Content-length': bytes(length)})
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
	jsonStr = json.dumps({'username':'user1','password':'password'})
	print(post_to_server(jsonStr, TARGET+"/login"))
	print(requests.get(TARGET + "/logout"))
	print(requests.get(TARGET + "/logout"))
	jsonStr = json.dumps({'username':'user1','password':'password'})
	print(post_to_server(jsonStr, TARGET+"/login"))
	print(requests.get(TARGET + "/mood").text)
	
if __name__ == "__main__":
	main()