from json import JSONEncoder

from flask import Flask, request, jsonify, current_app
from sqlalchemy import create_engine, text


def create_arr(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)

    database = create_engine(app.config['db_url'], encoding='utf-8', max_overflow=0)
    app.dataase = database

    return app


def get_user(user_id):
    user = current_app.database.execute(text("""
        SELECT
            id,
            name,
            email,
            profile
        FROM users
        WHERE id = :user_id
    """), {
        'user_id' : user_id
    }).fetchone()

    return {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'profile': user['profile']
    } if user else None


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return list(o)

        return JSONEncoder.default(self, o)


app = create_arr()
app.json_encoder = CustomJSONEncoder
app.users = {}
app.id_count = 1
app.tweet = []


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/sign-up', methods=['POST'])
def sign_up():
    new_user = request.json
    new_user_id = app.dataase.execute(text("""
    INSERT INTO users (
        name,
        email,
        profile,
        hashed_password
    )
    VALUES (
        :name,
        :email,
        :profile,
        :password
    )
    """), new_user).lastrowid

    row = current_app.database.execute(text("""
        SELECT
            id,
            name,
            email,
            profile
        FROM users
        WHERE id = :user_id
    """), {
        'user_id': new_user_id
    }).fetchone()

    created_user = {
        'id': row['id'],
        'name': row['name'],
        'email': row['email'],
        'profile': row['profile']
    } if row else None

    return jsonify(created_user)


@app.route('/tweet', methods=['POST'])
def tweet():
    user_tweet = request.json
    tweet = user_tweet['tweet']

    if len(tweet) > 300:
        return '300자를 초과했습니다', 400

    app.database.execute(text("""
        INSERT INTO tweets (
            user_id,
            tweet
        )
        VALUES (
            :id,
            :tweet
        )
    """), user_tweet)

    return '', 200


@app.route('/follow', methods=['POST'])
def follow():
    payload = request.json
    user_id = int(payload['id'])
    user_id_to_follow = int(payload['follow'])

    if user_id not in app.users or user_id_to_follow not in app.users:
        return '사용자가 존재하지 않습니다', 400

    user = app.users[user_id]
    user.setdefault('follow', set()).add(user_id_to_follow)

    return jsonify(user)


@app.route('/unfollow', methods=['POST'])
def follow():
    payload = request.json
    user_id = int(payload['id'])
    user_id_to_follow = int(payload['unfollow'])

    if user_id not in app.users or user_id_to_follow not in app.users:
        return '사용자가 존재하지 않습니다', 400

    user = app.users[user_id]
    user.setdefault('follow', set()).discard(user_id_to_follow)  # 값이 없어도 에러를 발생시키지 않음

    return jsonify(user)


@app.route('/timeline/<int:user_id>', methods=['GET'])
def timeline(user_id):
    if user_id not in app.users:
        return '사용자가 존재하지 않습니다', 400

    follow_list = app.users[user_id].get('follow', set())
    follow_list.add(user_id)
    timeline = [tweet for tweet in app.tweets if tweet['user_id'] in follow_list]

    return jsonify({
        'user_id': user_id,
        'timeline': timeline
    })


if __name__ == '__main__':
    app.run()
