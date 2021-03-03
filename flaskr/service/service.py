from flaskr.db import get_db
from core import entities


def db_execute(sql, params=None):
    db = get_db()
    if params:
        return db.execute(sql, params)
    return db.execute(sql)


def db_update(sql, params=None):
    db = get_db()
    last_rowid = db_execute(sql, params).lastrowid
    db.commit()
    return last_rowid


def db_execute_one(sql, params=None):
    return db_execute(sql, params).fetchone()


def db_execute_all(sql, params=None):
    return db_execute(sql, params).fetchall()


def store_entity(table_name, column_list, entity: entities.Entity):
    attributes_list = entity.attributes.keys()
    set_section = list()
    query_args = list()

    for attr in attributes_list:
        if attr in column_list:
            set_section.append(attr)

    for attr in set_section:
        query_args.append(getattr(entity, attr))

    set_string = ', '.join(set_section)
    values_string = '(' + ', '.join(['?'] * len(set_section)) + ')'

    sql = 'REPLACE INTO %s (%s) VALUES %s' % \
          (table_name, set_string, values_string)

    query_args = tuple(query_args)

    entity_id = db_update(sql, query_args)

    if not hasattr(entity, 'id'):
        entity.id = entity_id

    return entity_id
