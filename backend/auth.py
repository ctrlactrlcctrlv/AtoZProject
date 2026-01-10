from flask_restx import Resource, Namespace, fields
from flask import request, Flask
from models import User
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash

auth_ns = Namespace('auth', description='Authentication related operations')

signup_model = auth_ns.model(
    'SignUp',
    {
        'username': fields.String(required=True, description="The user's username"),
        'email': fields.String(required=True, description="The user's email"),
        'password': fields.String(required=True, description="The user's password"),
    }
)

login_model = auth_ns.model(
    'Login',
    {
        'username': fields.String(required=True, description="The user's username"),
        'password': fields.String(required=True, description="The user's password"),
    }
)

@auth_ns.route('/signup')
class SignUp(Resource):
    @auth_ns.expect(signup_model)
    def post(self):
        data=request.get_json()
        if not data:
            return {"message": "Request body is required"}, 400

        username=data.get('username')
        email=data.get('email')
        if not username or not email or not data.get('password'):
            return {"message": "username, email, and password are required"}, 400

        db_user = User.query.filter_by(username=username).first()
        if db_user:
            return {"message":"Username already exists"}, 409
        db_email = User.query.filter_by(email=email).first()
        if db_email:
            return {"message":"Email already exists"}, 409

        new_user=User(
            username=data.get('username'),
            email=email,
            password=generate_password_hash(data.get('password'))
        )
        new_user.save()
        return {"message":"User created successfully"}, 201
    

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data=request.get_json()
        if not data:
            return {"message": "Request body is required"}, 400

        username=data.get("username")
        password=data.get("password")
        if not username or not password:
            return {"message": "username and password are required"}, 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            return {"message":"Invalid credentials"}, 401
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return {"access_token": access_token, "refresh_token": refresh_token}, 200   

