from flask import Blueprint, flash, g, redirect, render_template, \
    request, session, url_for

from flaskr.db import get_db
from flaskr import service

from core import entities
from core.errors import ValidationException, MessageException

bp = Blueprint('product', __name__, url_prefix='/product/')


@bp.route('/', methods=('GET',))
def product_list():
    db = get_db()
    context = {}

    products = service.build_products_list_by_ids_list()
    context['products'] = list()
    for product in products:
        context['products'].append({
            **product.serialize(),
            'url': url_for('product.product', product_id=product.id)
        })

    return render_template('product/list.html', **context)


@bp.route('/<int:product_id>', methods=('GET', 'POST'))
def product(product_id):
    db = get_db()
    errors = []
    context = {}

    product = service.build_product_by_id(product_id)

    if not product:
        return render_template(url_for('product.product_list'))

    if request.method == 'POST':
        user_id = session.get('user_id')
        editor = None
        if user_id:
            editor = service.build_user_by_id(user_id)

        if user_id == product.owner.id:
            try:
                product.edit(editor=editor, **request.form)
            except MessageException as err:
                for m in err.messages:
                    flash(m)

            service.store_product(product)
        else:
            cart = service.build_cart_by_owner(editor)
            if not cart:
                cart = entities.Cart(owner=editor)
            cart.products.append(product)

            if not hasattr(cart, 'id'):
                new_cart_id = db.execute(
                    'INSERT INTO cart (owner_id, hash) VALUES (?, ?)',
                    (cart.owner.id, cart.hash)
                ).lastrowid
                cart(id=new_cart_id)

            db.execute(
                'DELETE FROM cart_products WHERE cart_id = ?',
                (cart.id,)
            )
            for prod in cart.products:
                db.execute(
                    'INSERT INTO cart_products (cart_id, product_id) VALUES (?, ?)',
                    (cart.id, prod.id)
                )

    db.commit()

    context['product'] = product.serialize()

    users_list = db.execute(
        'SELECT id, username FROM user'
    ).fetchall()

    context['users_list'] = list()
    for user in users_list:
        context['users_list'].append({
            'value': user['id'],
            'label': user['username']
        })

    return render_template('product/product.html', **context)


@bp.before_app_request
def load_user_cart():
    if g.user:
        user = g.user
    else:
        user = session.get('user_id')

    if user:
        g.cart = service.build_cart_by_owner(user)
