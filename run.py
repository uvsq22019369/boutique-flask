import os
from app import create_app

# Utiliser la config de production sur Render
config_name = 'production' if os.environ.get('RENDER') else 'development'
app = create_app(config_name)

if __name__ == '__main__':
    app.run()