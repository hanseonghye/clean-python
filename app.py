from flask import Flask
from sqlalchemy import create_engine

from model.tweet_dao import TweetDao
from model.user_dao import UserDao
from service.tweet_service import TweetService
from service.user_service import UserService
from view import create_endpoints


class Services:
    pass


def create_arr(test_config = None):
    app = Flask(__name__)

    CORS(app)

    if test_config is None
        app.config.from_pyfile("config.py")
    else :
        app.config.update(test_config)


    database = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)

    user_dao = UserDao(database)
    tweet_dao = TweetDao(database)


    services = Services
    services.user_service = UserService(user_dao, app.config)
    services.tweet_service = TweetService(tweet_dao)

    create_endpoints(app, services)

    return app