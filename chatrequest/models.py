from chatrequest import app, db, login
from flask_login import UserMixin, login_manager, current_user
from flask_principal import UserNeed, RoleNeed, identity_loaded
from sqlalchemy_utils import IPAddressType


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    request = db.relationship('Request', backref='user')
    created_date = db.Column(db.DateTime())

    def __repr__(self):
        return '/u/{}'.format(self.username)


@identity_loaded.connect_via(app)
def load_identity(sender, identity):
    identity.user = current_user

    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Request(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    rs_username = db.Column(db.String(64))
    request_ip = db.Column(IPAddressType)
    request_date = db.Column(db.DateTime())
    granted = db.Column(db.Boolean())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '{0}: {1}/{2}'.format(self.rs_username, self.request_date.month, self.request_date.year)