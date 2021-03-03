from flask import Blueprint, flash, g, redirect, render_template,\
                  request, session, url_for

from flaskr.service import service, user as s_user

from core import entities
from core.errors import ValidationException

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        user = None
        username = request.form['username']
        password = request.form['password']
        errors = None

        try:
            user = entities.User(username=username, password=password)
        except ValidationException as err:
            errors = err.messages
            for err in err.messages:
                flash(err)

        if errors is None and user is not None:
            s_user.store_user(user)

            return redirect(url_for('auth.login'))

    return render_template('register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        errors = []
        user = service.db_execute_one(
            'SELECT * FROM user WHERE username = ?', (username,)
        )

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
        user = s_user.build_user_by_id(user_id)
    g.user = user
