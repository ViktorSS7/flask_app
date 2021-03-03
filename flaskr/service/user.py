from flaskr.service.service import db_execute_one, db_execute_all,\
    store_entity

from core import entities


def store_user(user: entities.User):
    column_list = ('id', 'username', 'password', 'coins')
    return store_entity('user', column_list, user)


def build_user_by_id(user_id):
    user_data = db_execute_one(
        'SELECT * FROM user WHERE id = ?',
        (user_id,)
    )
    if user_data:
        return entities.User(**user_data)
    return None

