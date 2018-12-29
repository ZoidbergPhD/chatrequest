import os
import json
from json.decoder import JSONDecodeError
import sys
from dotenv import load_dotenv


class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(basedir, '.env'))
    try:
        ENV = os.environ.get('FLASK_ENV')
        DEBUG = (ENV == 'development')
        SECRET_KEY = os.environ.get('SECRET_KEY')
        SESSION_TYPE = os.environ.get('SESSION_TYPE')
        REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
        REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
        REDDIT_REDIRECT_URL = os.environ.get('REDDIT_REDIRECT_URL')
        REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT')
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
        RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
        RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
        SENTRY_DSN = os.environ.get('SENTRY_DSN')
        OUTPUT_SHEET_ID = os.environ.get('OUTPUT_SHEET_ID')

        with open(os.path.join(basedir, 'credentials.json')) as f:
            GOOGLE_SERVICE_CREDENTIALS = json.load(f)

    except KeyError as e:
        sys.exit('Missing environment variable: {}'.format(e))
    except FileNotFoundError:
        sys.exit('Missing Google credentials JSON file.')
    except JSONDecodeError:
        sys.exit('Invalid Google credentials JSON file.')
