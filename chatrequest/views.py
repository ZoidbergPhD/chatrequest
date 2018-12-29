from chatrequest import app, db, reddit
from flask import render_template, session, redirect, request, url_for, flash
from flask_login import current_user, login_user, logout_user
from utils import validate_rsn, signup_eligible, append_to_sheet
import datetime
from werkzeug import security
from .models import User, Request
from .forms import SignUpForm
from sentry_sdk import capture_message


@app.route('/', methods=['GET', 'POST'])
def index():
    signupform = SignUpForm()
    if signupform.validate_on_submit():
        if not validate_rsn(signupform.rsn.data):
            flash('Unable to validate RSN.', 'danger')
            return redirect(url_for('index'))
        if not signup_eligible(current_user):
            flash("Signup already recorded for this calendar month.", 'warning')
            return redirect(url_for('index'))
        new_request = Request()
        new_request.request_date = datetime.datetime.utcnow()
        new_request.rs_username = signupform.rsn.data
        new_request.request_ip = request.environ['REMOTE_ADDR']
        new_request.user_id = current_user.id
        db.session.add(new_request)
        db.session.commit()
        append_to_sheet(new_request)
        flash('RSN added to clan chat queue.', 'success')
        return redirect(url_for('index'))
    elif signupform.errors:
        for field, errors in signupform.errors.items():
            for error in errors:
                if field == 'recaptcha':
                    flash('Recaptcha error.', 'danger')
                else:
                    flash(error, 'danger')
    return render_template('index.html', form=signupform)


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    state = security.gen_salt(10)
    session['state'] = state
    return redirect(reddit.auth.url(['identity'], state))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/auth')
def auth():
    receivedState = request.args.get('state')
    receivedCode = request.args.get('code')
    if receivedState == session.get('state'):
        session.pop('state')
        if reddit.auth.authorize(receivedCode):
            reddit_name = reddit.user.me().name
            user = User.query.filter_by(username=reddit_name).first()
            if user is not None:
                login_user(user)
                return redirect(url_for('index'))
            else:
                new_user = User()
                new_user.username = reddit.user.me().name
                new_user.created_date = datetime.datetime.utcnow()
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('index'))
        else:
            capture_message('Unable to authorize')
    else:
        capture_message(
        '''
        DISCREPANCY:
        Received state: {0}
        Session state: {1}
        '''.format(receivedState, session.get('state')))
        session.pop('state')
        return redirect(url_for('index'))
