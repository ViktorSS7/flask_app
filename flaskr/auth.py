import functools

from flask import Blueprint, flash, g, redirect, render_template,\
                  request, session, url_for

from flaskr.db import get_db

from core import entities
from core.errors import ValidationException

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        user = None
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        errors = None

        try:
            user = entities.User(username=username, password=password)
        except ValidationException as err:
            errors = err.message
            flash(err.message)

        if errors is None and user is not None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (user.username, user.password)
            )
            db.commit()
            return str(user)

        return str(errors)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        errors = []
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            errors.append('Incorrect username.')
        else:
            user = entities.User(**user)

        if not errors and user.password_validate(password):
            session.clear()
            session['user_id'] = user.id
            return str(user)

        return str(errors)


@bp.route('/me', methods=['GET'])
def get_me():
    db = get_db()

    if session['user_id']:
        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (session['user_id'],)
        ).fetchone()

        if user is not None:
            user = entities.User(**user)

            return str({
                'username': user.username,
            })
