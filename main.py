from uuid import uuid4
from flask import Flask
from flask_restful import Api, Resource, reqparse
from sqlalchemy.exc import IntegrityError
from models import User, Activation, session


app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('email', required=True, help="Email is missing")
parser.add_argument('password', required=True, help="Password is missing")


class UserResource(Resource):
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
    def get(self, code):
        activation = session.query(Activation).filter_by(code=code).first()
        if activation:
            if activation.user.is_active:
                return {'error': 'Already activated'}, 400
            activation.user.is_active = True
            session.add(activation)
            session.commit()
            return {'success': "User activated"}
        else:
            return {'error': 'Invalid code, checkout the url'}, 400

api.add_resource(UserResource, '/users')
api.add_resource(ActivationResource, '/activation/<code>')

if __name__ == '__main__':
    app.run(debug=True)