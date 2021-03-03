from flaskr.service.service import db_execute_one, db_execute_all, \
    store_entity
from flaskr.service.user import build_user_by_id
from flaskr.service.product import build_products_list_by_ids_list

from core import entities


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
