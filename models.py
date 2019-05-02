"""
models imports app, but app does not import models so we haven't created
any loops.
"""
import datetime
import re

from peewee import *

from app import *

from flask import Markup

from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import parse_html
#from micawber.cache import Cache as OEmbedCache


################################################################

class User(flask_db.Model):
    """
    Creates table "USER"
    """
    #user_id = IntegerField(primary_key=True)
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()
    description = TextField()
    user_level = IntegerField() #user_level == 1: Admin
    ip = CharField(null=True) #request.headers['X-Real-IP']
    registered = DateTimeField(default=datetime.datetime.now)
    last_login = DateTimeField(default=datetime.datetime.now, index=True)
    avatar_file = CharField(default='default.jpg')
    #temp_pass = CharField(null=True)
    #temp_pass_expire = DateTimeField(default=datetime.datetime.now()+datetime.timedelta(minutes=30),null=True)

    @classmethod
    def users_list(cls):
        """
        Selects all published posts
        """
        return User.select()

    @classmethod
    def get_id_by_username(cls,username):
        """
        Returns the userid given its username
        """
        return User.select(User.id).where(User.username == username)

    @classmethod
    def get_user_level_by_username(cls,username):
        """
        Returns the user_level given its username
        """
        return User.select(User.user_level).where(User.username == username)

    @classmethod
    def get_user_by_username(cls,username):
        return User.select().where(User.username == username)


#################################################################

class Post(flask_db.Model):
    """
    Creates table "POST"
    """
    #post_id = IntegerField(primary_key=True)
    title = CharField()
    slug = CharField(unique=True)
    content = TextField()
    published = BooleanField(index=True)
    owner = ForeignKeyField(User,backref='posts')
    created_date = DateTimeField(default=datetime.datetime.now, index=True)
    comments_count = IntegerField(default=0)


    @property
    def html_content(self):
        """
        Generate HTML representation of the markdown-formatted blog entry,
        and also convert any media URLs into rich media objects such as video
        players or images.
        """
        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.content, extensions=[hilite, extras])
        oembed_content = parse_html(
            markdown_content,
            oembed_providers,
            urlize_all=True,
            maxwidth=app.config['SITE_WIDTH'])
        return Markup(oembed_content)

    @property
    def html_user_description(self):
        """
        Allows markdown in admin user description.
        """
        markdown_content = markdown(self.owner.description)
        oembed_content = parse_html(
            markdown_content,
            oembed_providers,
            urlize_all=True)
        return Markup(oembed_content)
        

    def save(self, *args, **kwargs):
        # Generate a URL-friendly representation of the entry's title.
        if not self.slug:
            self.slug = re.sub('[^\w]+', '-', self.title.lower()).strip('-')
        # Reserved slug words
        assert(self.slug not in ["admin","login","logout","index"])
        ret = super(Post, self).save(*args, **kwargs)
        return ret

    @classmethod
    def public(cls):
        """
        Selects all published posts
        """
        return Post.select().where(Post.published == True)

    @classmethod
    def drafts(cls):
        """
        Selects all drafts
        """
        return Post.select().where(Post.published == False)

    @classmethod
    def get_public_with_authors(cls):
        """
        Selects all published posts
        """
        #return Post.select(Tweet.content, User.username).join(User).dicts():
        return Post.select(Post, User.username, User.description, User.user_level, User.avatar_file).join(User).where(Post.published == True)

    @classmethod
    def posts_by_user_id(cls,userid,published=True):
        return Post.select(Post.title,Post.slug,Post.created_date).where((Post.published == published) & (Post.owner == userid)).order_by(Post.created_date.desc())

    @classmethod
    def post_public_by_slug(cls,slug):
        """Returns specific public post by slug"""
        return Post.select().where((Post.published == True) & (Post.slug == slug))

    @classmethod
    def get_post_public_with_author_by_slug(cls,slug):
        """
        Selects all published posts
        """
        return Post.select(Post, User.username, User.description ,User.avatar_file).join(User).where((Post.slug == slug) & (Post.published == True))


    @classmethod
    def delete_post_by_slug(cls,slug):
        """Deletes specific post by slug"""
        return Post.delete().where(Post.slug == slug)


################################################################

class Comment(flask_db.Model):
    """
    Creates table "USER"
    """
    #comment_id = IntegerField(primary_key=True)
    commented_in_id = ForeignKeyField(Post,backref='comments')
    description = TextField()
    reply_to = IntegerField()
    comment_date = DateTimeField(default=datetime.datetime.now, index=True)

    @classmethod
    def comment_list(cls, post_id):
        """
        Selects all comments in certain post
        """
        return Comment.select().where(Comment.commented_in_id == post_id and Comment.reply_to == 0)

    @classmethod
    def reply_list(cls, post_id):
        """
        Selects all comments in certain post
        """
        return Comment.select().where(
            (Comment.commented_in_id == post_id) &
            (Comment.reply_to > 0)
        )

#################################################################

class FailedLogin(flask_db.Model):
    """Tracks failed login attemps"""
    user_ip = TextField(index=True)
    fail_date = DateTimeField(default=datetime.datetime.now, index=True)

    @classmethod
    def get_count_by_ip_minutes(cls,ip,minutes):
        # Count the number of failes by ip in the last x minutes
        # Get the current time.
        now = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
        #return FailedLogin.select().where((FailedLogin.user_ip == ip) & (FailedLogin.fail_date <= datetime.datetime.now )).count()
        return FailedLogin.select().where(
            (FailedLogin.user_ip == ip) &
            (FailedLogin.fail_date.year >= now.year) &
            (FailedLogin.fail_date.month >= now.month) &
            (FailedLogin.fail_date.day >= now.day) &
            (FailedLogin.fail_date.hour >= now.hour) &
            (FailedLogin.fail_date.minute >= now.minute)
            ).count()

#################################################################

class Infographic(flask_db.Model):
    """Saves created infographics"""
    title1 = CharField()
    text1 = TextField()
    title2 = CharField()
    text2 = TextField()
    title3 = CharField()
    text3 = TextField()
    title4 = CharField()
    text4 = TextField()
    image1 = CharField()
    image2 = CharField()
    image3 = CharField()
    image4 = CharField()
    slug = CharField(unique=True)
    owner = ForeignKeyField(User,backref='infographics')
    created_date = DateTimeField(default=datetime.datetime.now, index=True)
    
    @classmethod
    def get_count_by_owner_minutes(cls,owner,minutes):
        # Count the number of infographics by owner in the last x minutes
        # Get the current time.
        now = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
        return Infographic.select().where(
            (Infographic.owner == owner) &
            (Infographic.created_date.year >= now.year) &
            (Infographic.created_date.month >= now.month) &
            (Infographic.created_date.day >= now.day) &
            (Infographic.created_date.hour >= now.hour) &
            (Infographic.created_date.minute >= now.minute)
            ).count()