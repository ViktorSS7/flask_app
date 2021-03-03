from flaskr.service.service import db_execute_one, db_execute_all, \
    store_entity
from flaskr.service.user import build_user_by_id, store_user

from core import entities


def store_product(product: entities.Product):
    column_list = ('id', 'owner_id', 'created', 'title', 'price')
    if hasattr(product.owner, 'id'):
        product.owner_id = product.owner.id
    else:
        product.owner_id = store_user(product.owner)
    return store_entity('product', column_list, product)


def build_products_list_by_ids_list(ids_list=None):
    products = list()
    if not ids_list:
        products_set = db_execute_all('SELECT * FROM product')
    else:
        products_set = db_execute_all(
            'SELECT * FROM product WHERE id IN (%s)'
            % ', '.join(['?'] * len(ids_list)),
            tuple(ids_list)
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
