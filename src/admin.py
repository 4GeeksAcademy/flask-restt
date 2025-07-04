import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from src.models import db, User

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    # Añadimos el modelo User para administración
    admin.add_view(ModelView(User, db.session))

    # Aquí puedes añadir más modelos si tienes, por ejemplo:
    # from src.models import AnotherModel
    # admin.add_view(ModelView(AnotherModel, db.session))
