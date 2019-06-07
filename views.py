"""
views imports app, auth, and models, but none of these import views
"""
import urllib

from flask import (flash, redirect, render_template, request,
                   Response, session, url_for, abort)

from playhouse.flask_utils import get_object_or_404, object_list
from playhouse.shortcuts import model_to_dict

# I18n translationa
from flask_babel import Babel, _


from app import app
from auth import *
from models import *#User, Post, Comment
import config

# Translation I18n
babel = Babel(app)

###########################################################
@babel.localeselector
def get_locale():
    # return request.accept_languages.best_match(app.config['LANGUAGES'])
    return 'es'

# Command used for translations 
# 1st create babel.cfg, 
# 2nd run: pybabel extract -F babel.cfg -o messages.pot .
# 3rd run: pybabel init -i messages.pot -d translations -l es
# To update the file with new sentences:
# 1st run: pybabel extract -F babel.cfg -o messages.pot .
# 2nd run: pybabel update -i messages.pot -d translations 
#############################################################


@app.route('/login/', methods=['GET', 'POST'])
def login():
    #ip=request.environ['REMOTE_ADDR']
    #ip=request.headers.get('X-Forwarded-For', request.remote_addr) 
    ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    #flash(ip,'danger')
    failed_attemps = FailedLogin.get_count_by_ip_minutes(ip,15)
    if failed_attemps >= 3:
        abort(404)
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password') and request.form.get('username'):
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            user = User.get_user_by_username(username).get()
            # TODO: If using a one-way hash, you would also hash the user-submitted
            # password and do the comparison on the hashed versions.
            #if password == app.config['ADMIN_PASSWORD']:
            if verify_password(user.password,password):
                session['logged_in'] = True
                session['username'] = username
                user_level = User.get_user_level_by_username(username).get()
                session['user_level'] = model_to_dict(user_level)['user_level']
                session.permanent = True  # Use cookie to store session.
                return redirect(next_url or url_for('blog'))
            else:
                #failed_attemps = FailedLogin.get_count_by_ip_minutes('192.168.1.1',15)
                flash(('Credenciales incorrectas. Has fallado {0} veces.').format(failed_attemps), 'danger')
                FailedLogin.create(user_ip=ip)
        except Exception as e: # User doesn't exist
            failed_attemps = FailedLogin.get_count_by_ip_minutes(ip,15)
            flash(('Credenciales incorrectas. Has fallado {0} veces.').format(failed_attemps), 'danger')
            FailedLogin.create(user_ip=ip)
    return render_template('login.html', next_url=next_url)


@app.route('/logout/', methods=['GET'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('blog'))

########################################################################

@app.route('/blog/', methods=['GET','POST'])
def blog():
    query = Post.get_public_with_authors().order_by(Post.created_date.desc())
    admin = User.select().where(User.id==1).get()
    return object_list('blog/index.html', query, paginate_by=20, admin=admin)


@app.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
    # We'll use this template filter in the pagination include. This filter
    # will take the current URL and allow us to preserve the arguments in the
    # querystring while replacing any that we need to overwrite. For instance
    # if your URL is /?q=search+query&page=2 and we want to preserve the search
    # term but make a link to page 3, this filter will allow us to do that.
    querystring = dict((key, value) for key, value in request_args.items())
    for key in keys_to_remove:
        querystring.pop(key, None)
    querystring.update(new_values)
    return urllib.parse.urlencode(querystring)


@app.route('/blog/<slug>/')
def detail(slug):
    query = Post.get_post_public_with_author_by_slug(slug)
    post = get_object_or_404(query)
    return render_template('blog/detail.html', post=query.get())


def _create_or_edit(post, template):
    if request.method == 'POST':
        post.title = request.form.get('title') or ''
        post.content = request.form.get('content') or ''
        post.published = request.form.get('published') or False
        # Keep post owner when editing
        post.owner = request.form.get('owner')
        if not (post.title and post.content):
            flash(_('Title and Content are required.'), 'danger')
        else:
            # Wrap the call to save in a transaction so we can roll it back
            # cleanly in the event of an integrity error.
            try:
                with db.atomic():
                    post.save()
            except AssertionError: # Prohibited title
                flash(_('Choose another title'), 'danger')  
            except IntegrityError:
                flash(_('Error: this title is already in use.'), 'danger')
            else:
                flash(_('Post created successfully.'), 'success')
                if post.published:
                    return redirect(url_for('all_posts'))
                else:
                    return redirect(url_for('all_posts')+'?p=0')
    try:
        assert(post.owner)
    except:
        #post.owner = User.id#model_to_dict(User.get_id_by_username(session.get('username')).get())['id']
        post.owner = User.get_id_by_username(session.get('username')).get().id
    return render_template(template, post=post)


@app.route('/blog/admin/all-posts/', methods=['GET'])
@moderator_required
def all_posts():
    userid = User.get_id_by_username(session.get('username'))
    if request.args.get('p') == '0': # Drafts
        published = False
        query = Post.posts_by_user_id(userid,published)
    elif request.args.get('p') == '2' and session.get('user_level') == 1: # All published posts
        published = True
        query = Post.get_public_with_authors().order_by(Post.created_date.desc())
        return render_template ('blog/all_posts_admin.html', posts=query, published=published)
    else:
        published = True
        query = Post.posts_by_user_id(userid,published)
    return render_template ('blog/all_posts.html', posts=query, published=published)


@app.route('/blog/admin/create/', methods=['GET', 'POST'])
@moderator_required
def create():
    return _create_or_edit(Post(title='', content=''), 'blog/create.html')


@app.route('/blog/admin/<slug>/edit/', methods=['GET', 'POST'])
@moderator_required
def edit(slug):
    post = get_object_or_404(Post, Post.slug == slug)
    if session.get('user_level') == 1:
        return _create_or_edit(post, 'blog/edit.html')
    elif session.get('user_level') == 2 and post.owner.id > 1:
        return _create_or_edit(post, 'blog/edit.html')
    else:
        abort(404)


@app.route('/blog/admin/<slug>/delete/', methods=['GET'])
@moderator_required
def delete_post(slug):
    post = get_object_or_404(Post, Post.slug == slug)
    if session.get('user_level') == 1:
        Post.delete_post_by_slug(slug).execute()
        flash('Post deleted successfully', 'success')
        return redirect(url_for('all_posts'))
    elif session.get('user_level') == 2 and post.owner.id > 1:
        Post.delete_post_by_slug(slug).execute()
        flash('Post deleted successfully', 'success')
        return redirect(url_for('all_posts'))
    else:
        abort(404)

#####################################################################

# Landing page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/eugenia-quiroga-odera/', methods=['GET'])
def eugenia_quiroga_odera():
    return render_template('eugenia-quiroga-odera.html')



#############################################################################




@app.errorhandler(404)
def not_found(exc):
    return render_template('404.html'), 404

