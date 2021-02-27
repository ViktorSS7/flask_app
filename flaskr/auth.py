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
            errors = err.messages
            for err in err.messages:
                flash(err)

        if errors is None and user is not None:
            db.execute(
                'INSERT INTO user (username, password, coins) VALUES (?, ?, ?)',
                (user.username, user.password, user.coins)
            )
            db.commit()
            return redirect(url_for('auth.login'))

    return render_template('register.html')


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
            return redirect(url_for('user.get_me'))

    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@bp.before_app_request
def load_logged_user():
    user_id = session.get('user_id')
    user = None

    if user_id:
        user = get_db().execute(
            'SELECT * FROM user WHERE id = ?',
            (user_id,)
        ).fetchone()
        if user:
            user = entities.User(**user)
    g.user = user
