# Blog configuration values.
import os


class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = 'do-i-really-need-this'
    FLASK_SECRET = SECRET_KEY
    HOST = '127.0.0.1'
    PORT = 5000
    THREADED = True
    SITE_NAME = 'Qdental' # Name of the blog
    SITE_WIDTH = 700

class DevelopmentConfig(Config):
    # You may consider using a one-way hash to generate the password, and then
    # use the hash again in the login view to perform the comparison. This is just
    # for simplicity.
    APP_DIR = os.path.dirname(os.path.realpath(__file__))

    # The playhouse.flask_utils.FlaskDB object accepts database URL configuration.
    DATABASE = 'sqliteext:///{0}'.format(os.path.join(APP_DIR, 'blog.db'))
    
        
class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
    DB_HOST = 'my.production.database' # not a docker link
    #For mor info - http://docs.peewee-orm.com/en/latest/peewee/database.html
    DATABASE = 'mysql://sql10286321:AgDZpM5Eer@sql10.freemysqlhosting.net:3306/sql10286321'

