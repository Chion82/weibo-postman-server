import requests, json, sys, os
from flask import Flask, request, session, jsonify
from urllib import quote

reload(sys)
sys.setdefaultencoding('utf8')

known_ship_ids = [1, 125, 153, 18, 27, 409, 442, 49, 68, 87, 10, 126, 154, 181, 28, 41, 443, 50, 69, 89, 100, 127, 155, 182, 29, 410, 445, 51, 7, 9, 101, 128, 16, 183, 30, 413, 446, 52, 70, 90, 102, 13, 161, 184, 31, 414, 448, 53, 71, 91, 103, 131, 163, 185, 32, 415, 45, 54, 72, 92, 11, 132, 164, 186, 33, 42, 451, 55, 74, 93, 110, 133, 165, 19, 331, 421, 452, 56, 75, 94, 111, 134, 167, 190, 332, 422, 453, 59, 76, 95, 113, 135, 168, 191, 34, 423, 454, 6, 77, 96, 114, 137, 169, 2, 35, 424, 455, 60, 78, 97, 115, 138, 17, 20, 36, 425, 458, 61, 79, 98, 116, 139, 170, 21, 37, 43, 459, 62, 80, 99, 12, 14, 171, 22, 38, 431, 46, 63, 81, 120, 140, 173, 23, 39, 432, 460, 64, 83, 122, 143, 174, 24, 40, 436, 465, 65, 84, 123, 147, 175, 25, 404, 44, 47, 66, 85, 124, 15, 176, 26, 405, 441, 48, 67, 86]

app = Flask(__name__)
app.secret_key = open('session_key', 'r').read().replace('\n', '')

app_key = '3125827369'
app_secret = open('app_secret', 'r').read().replace('\n', '')
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
	if not 'access_token' in request.args:
		if not 'access_token' in session:
			return jsonify({'status': 403})
		access_token = session['access_token']
		if not is_access_token_valid(access_token):
			return jsonify({'status':403})
	else:
		access_token = request.args['access_token']

	if 'text' in request.form:
		text = request.form['text']
	else:
		text = request.args['text']

	api_ship_id = None
	if 'api_ship_id' in request.form:
		api_ship_id = request.form['api_ship_id']
	if 'api_ship_id' in request.args:
		api_ship_id = request.args['api_ship_id']

	post_image_flag = False
	if api_ship_id != None and int(api_ship_id) in known_ship_ids:
		post_image_flag = True

	if post_image_flag:
		request_result = requests.post('https://api.weibo.com/2/statuses/upload_url_text.json', {
			'access_token':access_token,
			'status':text,
			'url':'http://blog.chionlab.moe/ship_images/%s.png' % api_ship_id
		})
	else:
		request_result = requests.post('https://api.weibo.com/2/statuses/update.json', {
			'access_token':access_token,
			'status':text
		})

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
	app.run(host='0.0.0.0', port=5011, debug=True)
