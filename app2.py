from functools import wraps

import jwt
from flask import request, current_app, Response
from flask.json import JSONEncoder


def create_endpoints(app, services):
    user_service = services.user_service

    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json
        new_user_id = user_service.create_new_user(new_user)
        new_user = user_service.get_user(new_user_id)


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return list(o)

        return JSONEncoder.default(self, o)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token is not None:
            try:
                payload = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], 'HS256')
            except jwt.InvalidTokenError:
                payload = None

            if payload is None: return Response(status = 401)

            user_id = payload['user_id']
            g.user_id = user_id
        else :
            return Response(status=401)
        return f(*args, **kwargs)

    return decorated_function


def create_endpoints(app, services):
    app.json_encoder = CustomJSONEncoder

    user_service = services.user_service
    tweet_service = services.tweet_Service
