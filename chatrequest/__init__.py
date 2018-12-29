from flask import Flask
from praw import Reddit
from config import Config
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


app = Flask(__name__)
app.config.from_object(Config)
sentry_sdk.init(
    dsn=app.config['SENTRY_DSN'],
    integrations=[FlaskIntegration()],
    environment=app.config['ENV']
)
Session(app)
login = LoginManager(app)
db = SQLAlchemy(app)
reddit = Reddit(client_id=app.config['REDDIT_CLIENT_ID'],
                    client_secret=app.config['REDDIT_CLIENT_SECRET'],
                    redirect_uri=app.config['REDDIT_REDIRECT_URL'],
                    user_agent=app.config['REDDIT_USER_AGENT'])

from chatrequest.views import *
from chatrequest.models import *
