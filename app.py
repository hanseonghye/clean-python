from json import JSONEncoder

from flask import Flask, request, jsonify


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return list(o)

        return JSONEncoder.default(self, o)


app = Flask(__name__)
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
    new_user['id'] = app.id_count
    app.users[app.id_count] = new_user
    app.id_count = app.id_count + 1

    return jsonify(new_user)


@app.route('/tweet', methods=['POST'])
def tweet():
    payload = request.json
    user_id = int(payload['id'])
    tweet = payload['tweet']

    if user_id not in app.users:
        return '사용자가 존재하지 않습니다', 400

    if len(tweet) > 300:
        return '300자를 초과했습니다', 400

    user_id = int(payload['id'])

    app.tweets.append({
        'use_id' : user_id,
        'tweet' : tweet
    })

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
    user.setdefault('follow', set()).discard(user_id_to_follow) # 값이 없어도 에러를 발생시키지 않음

    return jsonify(user)


@app.route('/timeline/<int:user_id>', methods=['GET'])
def timeline(user_id):
    if user_id not in app.users:
        return '사용자가 존재하지 않습니다', 400


    follow_list = app.users[user_id].get('follow', set())
    follow_list.add(user_id)
    timeline = [tweet for tweet in app.tweets if tweet['user_id'] in follow_list]

    return jsonify({
        'user_id' : user_id,
        'timeline' : timeline
    })


if __name__ == '__main__':
    app.run()
