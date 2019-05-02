"""
auth imports app and models, but none of those import auth
so we're OK
"""
import functools
import json
import hashlib, binascii, os
from flask import session, redirect, url_for, abort

def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        try:
            return redirect(url_for('login', next=request.path))
        except:
            return redirect(url_for('login'))        
    return inner

def debugger2(text):
    with open("debug.txt","a") as f:
        f.write(json.dumps(text))

def moderator_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in') and session.get('user_level') <= 2:
            return fn(*args, **kwargs)
        abort(404)
    return inner

def admin_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in') and session.get('user_level') == 1:
            return fn(*args, **kwargs)
        abort(404)
    return inner


# Login security

def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


#pas=hash_password('123')
#print(pas)
#print(verify_password(pas,'123'))