from flask import Blueprint, flash, g, redirect, render_template, \
    request, session, url_for

from flaskr.db import get_db

from core import entities
from core.errors import ValidationException
from core.localization import _

bp = Blueprint('user', __name__, url_prefix='/user/')


@bp.route('/me', methods=['GET', 'POST'])
def get_me():
    db = get_db()
    context = {}

    if session['user_id']:
        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (session['user_id'],)
        ).fetchone()

        if user is not None:
            user = entities.User(**user)
            context['user'] = user.serialize()

            if request.method == 'POST':
                try:
                    user.change_password(**request.form)
                    flash(_('Your password has been changed'))
                except ValidationException as err:
                    for err in err.messages:
                        flash(err)

                db.execute(
                    'UPDATE user SET password = ? WHERE id = ?',
                    (user.password, user.id)
                )
                db.commit()

    if not context:
        return redirect(url_for('auth.login'))

    return render_template('user/me.html', **context)


@bp.route('/list', methods=['GET'])
def get_users_list():
    db = get_db()

    users = db.execute(
        'SELECT * FROM user'
    ).fetchall()

    context = list()
    for user in users:
        user = entities.User(**user)
        context.append(user.serialize())

    return {'result': context}
