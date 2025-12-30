from flask import Flask
from flask_restx import Api, Resource

from config import get_config_class, get_config_name
from models import Recipe
from exts import db

app = Flask(__name__)
env_name = get_config_name()
config_class = get_config_class(env_name)
app.config.from_object(config_class)
db.init_app(app)
api = Api(app, doc="/docs")

@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {'message': 'Hello, World !'}

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Recipe': Recipe}

if __name__ == '__main__' :
    app.run(debug=env_name.lower() != "production")
