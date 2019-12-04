# -*- coding:utf-8 -*-

import json
import sqlite3
from time import gmtime, strftime
from flask import Flask
from flask import jsonify, request, abort
from flask import make_response, render_template


app = Flask(__name__)


@app.errorhandler(404)
def resource_not_found(error):
    return make_response(jsonify({'error': 'Resource not found'}, 404))


@app.errorhandler(400)
def invalid_request(error):
    return make_response(jsonify({'error': 'Bad Request'}, 400))


@app.route('/adduser')
def adduser():
    return render_template('adduser.html')

@app.route('/api/v1/users', methods=['POST'])
def create_user():
    data = request.json
    if not data or not 'username' in data:
        abort(400)
    user = {
        'username': data['username'],
        'email': data['email'],
        'full_name': data['name'],
        'password': data['password']
    }
    return jsonify({'status': add_user(user)}, 201)


@app.route('/api/v1/users', methods=['GET'])
def get_users():
    data = list_users()
    return jsonify({'user_list': data}), 200


@app.route('/api/v1/info')
def home_index():
    conn = sqlite3.connect('mydb.db')
    print('Opened dateabse')
    api_list = []
    cursor = conn.execute('SELECT buildtime, version, methods, link from apirelease')
    for row in cursor:
        api = {}
        api['version'], api['buildtime'], api['methods'], api['link'] = row
        api_list.append(api)
    conn.close()

    return jsonify({'api_version': api_list}), 200


@app.route('/api/v1/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    data = list_user(user_id)
    return jsonify(data), 200


@app.route('/addtweets')
def addtweets():
    return render_template('addtweets.html')


@app.route('/api/v1/tweets', methods=['GET'])
def get_tweets():
    return jsonify({'tweets_list': list_tweets()}), 200


@app.route('/api/v1/tweets', methods=['POST'])
def add_tweets():
    user_tweet = {}
    data = request.json
    if not data or not 'username' in data or not 'body' in data:
        abort(400)
    user_tweet['username'] = data['username']
    user_tweet['body'] = data['body']
    user_tweet['created_at']=strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())
    return  jsonify({'status': add_tweet(user_tweet)}), 201


@app.route('/api/v1/tweets/<int:id>', methods=['GET'])
def get_tweet(id):
    return list_tweet(id)


def list_tweets():
    conn = sqlite3.connect('mydb.db')
    api_list = []
    cursor = conn.cursor()
    cursor.execute('SELECT username, body, pub_time, id from tweets')
    data = cursor.fetchall()
    if len(data) != 0:
        for row in data:
            tweets = {}
            tweets['tweetedby'], tweets['body'], tweets['timestamp'], tweets['id'] = row
            api_list.append(tweets)
    conn.close()
    return api_list


def add_tweet(user_tweet):
    conn = sqlite3.connect('mydb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * from users where username=? ",(user_tweet['username'],))
    data = cursor.fetchall()

    if len(data) != 0:
        abort(409)
    else:
       cursor.execute("INSERT into tweets (username, body, pub_time) values(?,?,?)",
                        (user_tweet['username'], user_tweet['body'], user_tweet['created_at']))
       conn.commit()
       return "Success"


def list_tweet(user_id):
    print (user_id)
    conn = sqlite3.connect('mydb.db')
    cursor=conn.cursor()
    cursor.execute("SELECT * from tweets  where id=?",(user_id,))
    data = cursor.fetchone()
    if len(data) == 0:
        abort(404)
    else:

        user = {}
        user['id'], user['username'], user['body'], user['pub_time'] = data

    conn.close()
    return user

def add_user(user):
    conn = sqlite3.connect('mydb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * from users where username=? or email=?", (user['username'], user['email']))
    data = cursor.fetchall()
    if len(data) != 0:
        abort(409)
    else:
        cursor.execute('Insert into users (username, email, password, full_name) values(?, ?, ?, ?)',
                        (user['username'], user['email'], user['password'], user['full_name']))
        conn.commit()
        return 'Success'


def list_users():
    conn = sqlite3.connect('mydb.db')
    api_list = []
    cursor = conn.execute('SELECT username, full_name, email, password, id from users')
    for row in cursor:
        api = {}
        api['username'], api['name'], api['email'], api['password'], api['id'] = row
        api_list.append(api)
    conn.close()

    return api_list


def list_user(user_id):
    conn = sqlite3.connect('mydb.db')
    user = {}
    cursor = conn.execute('SELECT username, full_name, email, password, id from users where id=?', (user_id,))
    data = cursor.fetchone()
    if data:
        user['username'], user['name'], user['email'], user['password'], user['id'] = data
    conn.close()

    return user
    

@app.route('/')
def hello():
    return 'Hello_world'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
