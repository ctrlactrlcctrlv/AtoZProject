# Import config and application factory
from main import create_app
from config import get_config_class, get_config_name
import os
env_name = get_config_name()
config_class = get_config_class(env_name)
app = create_app(config_class)
if __name__ == '__main__' :
    app.run(debug=env_name.lower() != "production")