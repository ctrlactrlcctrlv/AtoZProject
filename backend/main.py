from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields

from config import get_config_class, get_config_name
from models import Recipe, User
from exts import db
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required

app = Flask(__name__)

jwt = JWTManager(app)

env_name = get_config_name()
config_class = get_config_class(env_name)
app.config.from_object(config_class)
app.config['JWT_VERIFY_SUB'] = False # Disable the check of string. It solves the invalid crypto padding error. See https://www.reddit.com/r/flask/comments/1hedkxa/flaskjwtextended_and_invalid_crypto_padding/
db.init_app(app)

migrate=Migrate(app,db)

api = Api(app, doc="/docs")

# model serializer for Recipe 
recipe_model = api.model('Recipe',{
    "id": fields.Integer(),
    "title": fields.String(),
    "description": fields.String() 
})

signup_model = api.model(
    'SignUp',
    {
        'username': fields.String(required=True, description="The user's username"),
        'email': fields.String(required=True, description="The user's email"),
        'password': fields.String(required=True, description="The user's password"),
    }
)

login_model = api.model(
    'Login',
    {
        'username': fields.String(required=True, description="The user's username"),
        'password': fields.String(required=True, description="The user's password"),
    }
)

@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {'message': 'Hello, World !'}
    
@api.route('/signup')
class SignUp(Resource):
    @api.expect(signup_model)
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


@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
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



@api.route('/recipes')
class RecipesRessource(Resource):
    @api.marshal_list_with(recipe_model)
    def get(self):
        """Get all recipes"""
        recipes=Recipe.query.all()

        return recipes

    @api.marshal_list_with(recipe_model)
    @api.expect(recipe_model)
    @jwt_required()
    def post(self):
        """Create a new recipe"""

        data = request.get_json()
        new_recipe=Recipe(
            title=data.get('title'),
            description=data.get('description')
        )
        new_recipe.save()
        return new_recipe,201

@api.route('/recipe/<int:id>')
class RecipeRessource(Resource):
    @api.marshal_list_with(recipe_model)
    def get(self,id):
        """Get a recipe by id"""
        recipe=Recipe.query.get_or_404(id)
        return recipe


    @api.marshal_list_with(recipe_model)
    @jwt_required()
    def put(self,id):
        """Update a recipe by id"""
        recipe_to_update=Recipe.query.get_or_404(id)
        data=request.get_json()
        recipe_to_update.update(
            title=data.get('title'),
            description=data.get('description')
        )
        return recipe_to_update

    @api.marshal_list_with(recipe_model)
    @jwt_required()
    def delete(self,id):
        """Delete a recipe by id"""
        recipe_to_delete=Recipe.query.get_or_404(id)

        recipe_to_delete.delete()
        return recipe_to_delete,204

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Recipe': Recipe}

if __name__ == '__main__' :
    app.run(debug=env_name.lower() != "production")
