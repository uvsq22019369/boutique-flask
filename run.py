#!/usr/bin/env python
from app import create_app, db
from app.models.user import User

app = create_app('development')

@app.shell_context_processor
def make_shell_context():
    """Ajoute des objets au shell interactif"""
    return {'db': db, 'User': User}

if __name__ == '__main__':
    app.run(debug=True)




   
