from flaskr.service.service import db_execute_one, db_execute_all, \
    store_entity, db_update
from flaskr.service.user import build_user_by_id
from flaskr.service.product import build_products_list_by_ids_list,\
    store_product

from core import entities


def store_cart(cart: entities.Cart):
    column_list = ('id', 'owner_id', 'hash')
    cart_id = store_entity('cart', column_list, cart)
    db_update('DELETE FROM cart_products WHERE cart_id = ?', (cart_id,))
    for product in cart.products:
        db_update('INSERT INTO cart_products (cart_id, product_id) \
                   VALUES (?, ?)', (cart_id, product.id))
        store_product(product)
    return cart_id


def build_products_list_by_cart_id(cart_id):
    cart_products_data = db_execute_all(
        'SELECT * FROM cart_products WHERE cart_id = ?',
        (cart_id,)
    )
    products = list()
    if cart_products_data:
        products_ids_list = set()
        for prod in cart_products_data:
            products_ids_list.add(str(prod['product_id']))
        products = build_products_list_by_ids_list(products_ids_list)
    return products


def build_cart_by_id(cart_id):
    cart = None
    cart_data = db_execute_one(
        'SELECT * FROM cart WHERE id = ?',
        (cart_id,)
    )

    if cart_data:
        cart_owner = build_user_by_id(cart_data['owner_id'])

        products = build_products_list_by_cart_id(cart_id)

        cart = entities.Cart(**cart_data, products=products, owner=cart_owner)
    return cart


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
        cart_id = cart_data['id']
        if not cart_owner:
            cart_owner = build_user_by_id(cart_data['owner_id'])

        products = build_products_list_by_cart_id(cart_id)

        cart = entities.Cart(**cart_data, products=products, owner=cart_owner)
    return cart
