from uuid import uuid4
from flask import Flask
from flask_login import LoginManager, login_required, login_user, \
    logout_user
from flask_restful import Api, Resource, reqparse
from sqlalchemy.exc import IntegrityError

from models import User, Activation, session

app = Flask(__name__)
api = Api(app)

# Session management
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user

# Parameter requirements
parser = reqparse.RequestParser()
parser.add_argument('email', required=True, help="Email is missing")
parser.add_argument('password', required=True, help="Password is missing")


# Routing Resources

class UserResource(Resource):
    """
    User management endpoint
    """
    def post(self):
        args = parser.parse_args()
        email, pw = args['email'], args['password']
        user = User(email=email)
        user.set_password(pw)
        activation = Activation(code=uuid4().hex)
        user.activation = activation
        session.add(user)
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            return {'error': 'This e-mail is already in database.'}, 400
        return {'id': user.id, 'email': user.email, 'code': activation.code}


class ActivationResource(Resource):
    """
    Activation management endpoint
    """
    def get(self, code):
        activation = session.query(Activation).filter_by(code=code).first()
        if activation:
            if activation.user.is_active:
                return {'error': 'Already activated'}, 400
            activation.user.active = True
            session.add(activation)
            session.commit()
            return {'success': "User activated"}
        else:
            return {'error': 'Invalid code, checkout the url'}, 400


class ProtectedResource(Resource):
    """
    Protected url management endpoint
    """
    @login_required
    def get(self):
        return {'success': 'If you can see this, you are lucky!'}


class LoginResource(Resource):
    """
    Login endpoint
    """
    def post(self):
        args = parser.parse_args()
        email, pw = args['email'], args['password']
        user = session.query(User).filter_by(email=email).first()
        if user and user.is_valid_password(pw):
            if not user.active:
                return {'error': 'Activate your user'}, 400
            login_user(user)
            return {'success': 'You logged in as %s' % email}
        else:
            return {'error': 'The credentials you provided are not valid.'}, 400


class LogoutResource(Resource):
    """
    Logout endpoint
    """
    @login_required
    def get(self):
        logout_user()
        return {'success': 'Logged out'}


# Routing
api.add_resource(UserResource, '/users')
api.add_resource(ActivationResource, '/activation/<code>')
api.add_resource(ProtectedResource, '/protected')
api.add_resource(LoginResource, '/login')
api.add_resource(LogoutResource, '/logout')


# Main
if __name__ == '__main__':
    app.secret_key = 'ASIDUIEHTUASDOIGIH1@1joKOOAdkj' # Random for session
    app.run(host='0.0.0.0')
