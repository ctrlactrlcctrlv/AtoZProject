from flask import Flask, request
from flask_restx import Api, Resource, fields

from config import get_config_class, get_config_name
from models import Recipe
from exts import db

app = Flask(__name__)
env_name = get_config_name()
config_class = get_config_class(env_name)
app.config.from_object(config_class)

db.init_app(app)

api = Api(app, doc="/docs")

# model serializer for Recipe 
recipe_model = api.model('Recipe',{
    "id": fields.Integer(),
    "title": fields.String(),
    "description": fields.String() 
})

@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {'message': 'Hello, World !'}

@api.route('/recipes')
class RecipesRessource(Resource):
    @api.marshal_list_with(recipe_model)
    def get(self):
        """Get all recipes"""
        recipes=Recipe.query.all()

        return recipes

    @api.marshal_list_with(recipe_model)
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
