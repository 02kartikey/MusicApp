from flask import session, redirect, url_for, flash
from functools import wraps


def login_check(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login_page'))
        return func(*args, **kwargs)
    return wrap


def admin_check(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if session['user']['role'] != 'admin':
            flash("UNAUTHORIZED", "danger")
            return redirect(url_for('home_page'))
        return func(*args, **kwargs)
    return wrap
