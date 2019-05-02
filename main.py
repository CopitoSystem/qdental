"""
this is the "secret sauce" -- a single entry-point that resolves the
import dependencies.  If you're using blueprints, you can import your
blueprints here too.

then when you want to run your app, you point to main.py or `main.app`
"""
from app import app, db

from auth import *
#from admin import admin
#from api import api
from models import *
from views import *

# Print all queries to stderr.
#import logging
#logger = logging.getLogger('peewee')
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())

#admin.setup()
#api.setup()


def create_tables():
    # Create table for each model if it does not exist.
    # Use the underlying peewee database object instead of the
    # flask-peewee database wrapper:
    db.create_tables([User,Post,Comment,FailedLogin], safe=True)


def populate_database():
    # INSERT new row
    password_string = hash_password('123')
    User.create(username='Eugenia',email='aaa@gmail.com',password=password_string,description='Sin descripcion',user_level=1)
    Post.create(title='Prueba',slug='prueba',content='heheh este es el post',published=1,owner_id=1)
    #Comment.create(commented_in_id='1',description='Primer comentario',reply_to=0)
    #Comment.create(commented_in_id='1',description='Segundo comentario 2',reply_to=0)
    #Comment.create(commented_in_id='1',description='Respuesta 1',reply_to=1)
    #Comment.create(commented_in_id='1',description='Tercer comentario 3',reply_to=0)
    #Comment.create(commented_in_id='2',description='Quinto comentario 5',reply_to=0)  
    '''
    # We can INSERT tuples as well...
    data = [('val1-1', 'val1-2'),
            ('val2-1', 'val2-2'),
            ('val3-1', 'val3-2')]

    # But we need to indicate which fields the values correspond to.
    MyModel.insert_many(data, fields=[MyModel.field1, MyModel.field2]).execute()
    '''

if __name__ == '__main__':
    create_tables()
    try:
        populate_database()
    except:
        pass
    app.run()
