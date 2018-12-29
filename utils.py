import os
import datetime
import requests
import gspread
import re
from chatrequest import app
from chatrequest.models import Request
from sentry_sdk import capture_message
from oauth2client import service_account
from gspread.exceptions import WorksheetNotFound


def validate_rsn(rsn):
    """
    Validates RuneScape display name against the Old School RS High Scores.

    :param rsn: Old School RS display name
    :return: True if user appears on high scores, False otherwise
    """
    rsn_rule = '^(?=.{1,12}$)(?![ ])[a-zA-Z0-9 _-]+(?<![ ])$'
    if re.match(rsn_rule, rsn) is None:
        return False
    url = "http://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player={}".format(rsn)
    response = requests.get(url)
    code = response.status_code
    if code == 200:
        return True
    elif code == 404:
        return False
    else:
        capture_message('Unexpected response ({0}) when verifying RSN \'{1}\''.format(code, rsn))
        return False


def signup_eligible(user):
    """
    Checks user eligibility to sign up (once per calendar month).

    :param user: The User object
    :return: True if no request found in calendar month, False otherwise
    """
    req = Request.query.filter_by(user_id=user.id).order_by(Request.id.desc()).first()
    if req is not None:
        current_month = datetime.datetime.utcnow().month
        current_year = datetime.datetime.utcnow().year
        if req.request_date.month == current_month and req.request_date.year == current_year:
            return False
        else:
            return True
    else:
        #capture_message('checking eligibility failure for user /u/{}'.format(user.username))
        return True


def append_to_sheet(req):
    """
    Appends user-submitted request to Google Sheet

    :param req: The Request object to be appended to the sheet.
    :return: True if successful, False otherwise
    """
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    sheet_id = app.config['OUTPUT_SHEET_ID']
    creds = service_account.ServiceAccountCredentials.from_json_keyfile_dict(app.config['GOOGLE_SERVICE_CREDENTIALS'],
                                                                             scopes=scopes)

    sheet_title = '{0} {1}'.format(req.request_date.month, req.request_date.year)
    gc = gspread.authorize(creds)
    sheets = gc.open_by_key(sheet_id)

    try:
        sheet = sheets.worksheet(sheet_title)
        sheet.append_row([str(req.request_date), req.rs_username])
    except WorksheetNotFound:
        sheet = sheets.add_worksheet(title=sheet_title, rows='400', cols='2')
        sheet.append_row([str(req.request_date), req.rs_username])
    return True
