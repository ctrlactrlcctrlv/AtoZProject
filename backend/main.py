from flask import Flask
from flask_restx import Api
from config import get_config_class, get_config_name
from models import Recipe, User
from exts import db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from recipes import recipe_ns
from auth import auth_ns

def create_app(config):
    app = Flask(__name__)

    jwt = JWTManager(app)

    # env_name = get_config_name()
    # config_class = get_config_class(env_name)
    # app.config.from_object(config_class)
    app.config.from_object(config)
    app.config['JWT_VERIFY_SUB'] = False # Disable the check of string. It solves the invalid crypto padding error. See https://www.reddit.com/r/flask/comments/1hedkxa/flaskjwtextended_and_invalid_crypto_padding/
    db.init_app(app)

    migrate=Migrate(app,db)

    api = Api(app, doc="/docs")

    api.add_namespace(recipe_ns)
    api.add_namespace(auth_ns)

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'Recipe': Recipe, 'User': User}
    
    return app

    # if __name__ == '__main__' :
    #     app.run(debug=env_name.lower() != "production")
