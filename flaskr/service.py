from flaskr.db import get_db
from core import entities


def db_execute(sql, params=None):
    db = get_db()
    if params:
        return db.execute(sql, params)
    return db.execute(sql)


def db_update(sql, params=None):
    db = get_db()
    db_execute(sql, params)
    db.commit()


def db_execute_one(sql, params=None):
    return db_execute(sql, params).fetchone()


def db_execute_all(sql, params=None):
    return db_execute(sql, params).fetchall()


def store_product(product: entities.Product):
    column_list = ('id', 'owner_id', 'created', 'title', 'price')
    attributes_list = product.attributes.keys()
    set_section = list()
    query_args = list()

    for attr in attributes_list:
        if attr in column_list:
            set_section.append(attr)

    for attr in set_section:
        query_args.append(getattr(product, attr))

    set_string = ', '.join(set_section)
    values_string = '(' + ', '.join(['?'] * len(set_section)) + ')'

    sql = 'REPLACE INTO product (%s) VALUES %s' % \
          (set_string, values_string)

    query_args = tuple(query_args)

    db_update(sql, query_args)


def build_user_by_id(user_id):
    user_data = db_execute_one(
        'SELECT * FROM user WHERE id = ?',
        (user_id,)
    )
    if user_data:
        return entities.User(**user_data)
    return None


def build_products_list_by_ids_list(ids_list=None):
    products = list()
    if not ids_list:
        products_set = db_execute_all('SELECT * FROM product')
    else:
        products_set = db_execute_all(
            'SELECT * FROM product WHERE id IN (?)',
            (','.join(ids_list),)
        )

    for prod in products_set:
        owner = build_user_by_id(prod['owner_id'])
        products.append(entities.Product(**prod, owner=owner))
    return products


def build_product_by_id(product_id):
    product = None
    product_data = db_execute_one(
        'SELECT * FROM product WHERE id = ?',
        (product_id,)
    )
    if product_data:
        owner = build_user_by_id(product_data['owner_id'])
        product = entities.Product(**product_data, owner=owner)
    return product


def build_cart_by_owner(owner):
    cart_owner = None
    cart = None
    if type(owner) is not int:
        owner_id = owner.id
        cart_owner = owner
    else:
        owner_id = owner

    cart_data = db_execute_one(
        'SELECT * FROM cart WHERE owner_id = ?',
        (owner_id,)
    )

    if cart_data:
        if not cart_owner:
            cart_owner = build_user_by_id(cart_data['owner_id'])

        cart_products_data = db_execute_all(
            'SELECT * FROM cart_products WHERE cart_id = ?',
            (2,)
            # TODO TODO TODO
        )

        products = list()
        if cart_products_data:
            products_ids_list = set()
            for prod in cart_products_data:
                products_ids_list.add(str(prod['product_id']))
            products = build_products_list_by_ids_list(products_ids_list)

        cart = entities.Cart(**cart_data, products=products, owner=cart_owner)
    return cart
