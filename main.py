"""
this is the "secret sauce" -- a single entry-point that resolves the
import dependencies.  If you're using blueprints, you can import your
blueprints here too.

then when you want to run your app, you point to main.py or `main.app`
"""
from app import app, db

from auth import *

from models import *
from views import *

# Print all queries to stderr.
#import logging
#logger = logging.getLogger('peewee')
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())



def create_tables():
    # Create table for each model if it does not exist.
    # Use the underlying peewee database object instead of the
    # flask-peewee database wrapper:
    db.create_tables([User,Post,Comment,FailedLogin], safe=True)


def populate_database():
    # INSERT new row
    password_string = hash_password('123')
    User.create(username='Eugenia',email='aaa@gmail.com',password=password_string,description='Soy odontóloga platense 👩‍⚕️ - Actualmente trabajando en La Plata y Ushuaia - @EugeniaQuiroga',user_level=1)
    Post.create(title='Prueba',slug='prueba',content='heheh este es el post',published=1,owner_id=1)
    

if __name__ == '__main__':
    create_tables()
    try:
        populate_database()
    except:
        pass
    app.run()
