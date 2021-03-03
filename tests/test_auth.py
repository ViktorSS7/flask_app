import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    assert client.get('auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert 'http://localhost/auth/login' ==\
           response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            'select * from user where username = "a"',
        ).fetchone() is not None


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] ==\
           'http://localhost/user/me'

    with client:
        client.get('/product')
        assert session['user_id'] == 1
        assert g.user.username == 'test'


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
