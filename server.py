import requests, json, sys
from flask import Flask, request, session, jsonify
from urllib import quote

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.secret_key = open('session_key', 'r').read()

app_key = '3125827369'
app_secret = open('app_secret', 'r').read()
redirect_uri = 'http://119.29.154.223:5011/api/auth_callback'

@app.route('/api/auth_callback', methods=['GET'])
def api_auth_callback():
	code = request.args['code']
	request_result = requests.post('https://api.weibo.com/oauth2/access_token', {
			'client_id' : app_key,
			'client_secret' : app_secret,
			'grant_type' : 'authorization_code',
			'code' : code,
			'redirect_uri' : redirect_uri
		})
	result_json = json.loads(request_result.content)
	access_token = result_json['access_token']
	session['access_token'] = access_token
	return jsonify({'status':200})

@app.route('/api/post_weibo', methods=['GET', 'POST'])
def api_post_weibo():
	if not 'access_token' in session:
		return jsonify({'status': 403})
	access_token = session['access_token']
	if not is_access_token_valid(access_token):
		return jsonify({'status':403})
	if 'text' in request.form:
		text = request.form['text']
	else:
		text = request.args['text']
	request_result = requests.post('https://api.weibo.com/2/statuses/update.json', {'access_token':access_token, 'status':text})
	result_json = json.loads(request_result.content)
	if 'id' in result_json:
		return jsonify({'status':200, 'weibo_id':result_json['id']})
	else:
		return jsonify({'status':500, 'error':request_result.text})

def is_access_token_valid(access_token):
	request_result = requests.post('https://api.weibo.com/oauth2/get_token_info', {'access_token': access_token})
	result_json = json.loads(request_result.content)
	if 'expire_in' in result_json and result_json['expire_in'] > 0:
		return True
	else:
		return False

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)
