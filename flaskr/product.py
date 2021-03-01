from flask import Blueprint, flash, g, redirect, render_template, \
    request, session, url_for

from flaskr.db import get_db

from core import entities
from core.errors import ValidationException, MessageException

bp = Blueprint('product', __name__, url_prefix='/product/')


@bp.route('/', methods=('GET',))
def product_list():
    db = get_db()
    context = {}

    products = db.execute(
        'SELECT * FROM product'
    ).fetchall()

    context['products'] = []
    for product in products:
        user = db.execute(
            'SELECT * FROM user WHERE id = ?',
            (product['owner_id'],)
        ).fetchone()
        user = entities.User(**user)
        product = entities.Product(**product, owner=user)
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

    product = db.execute(
        'SELECT * FROM product WHERE id = ?',
        (product_id,)
    ).fetchone()

    user = db.execute(
        'SELECT * FROM user WHERE id = ?',
        (product['owner_id'],)
    ).fetchone()

    if not product or not user:
        return render_template(url_for('product.product_list'))

    user = entities.User(**user)

    product = entities.Product(**product, owner=user)

    if request.method == 'POST':
        user_id = session.get('user_id')
        editor = None
        if user_id:
            editor = db.execute(
                'SELECT * FROM user WHERE id = ?',
                (user_id,)
            ).fetchone()
            editor = entities.User(**editor)

        if user_id == product.owner.id:
            try:
                product.edit(editor=editor, **request.form)
            except MessageException as err:
                for m in err.messages:
                    flash(m)

            db.execute(
                'UPDATE product SET title = ?, price = ?, owner_id = ?',
                (product.title, product.price, product.owner.id)
            )
        else:
            cart = db.execute(
                'SELECT * FROM cart WHERE owner_id = ?',
                (user_id,)
            ).fetchone()
            products = list()
            if cart:
                cart_products = db.execute(
                    'SELECT * FROM product WHERE id IN \
                    (SELECT product_id FROM cart_products WHERE cart_id = ?)',
                    (cart['id'],)
                ).fetchall()
                for product in cart_products:
                    products.append(entities.Product(**product))
            try:
                cart = entities.Cart(owner=editor, products=products)
            except MessageException as err:
                for e in err.messages:
                    flash(e)
                    errors.append(e)

            if not errors:
                cart.products.append(product)

            if not hasattr(cart, 'id'):
                new_cart = db.execute(
                    'INSERT INTO cart (owner_id, hash) VALUES (?, ?)',
                    (cart.owner.id, cart.hash)
                ).fetchone()
                cart(**new_cart)
            # db.execute(
            #     'DELETE FROM cart_products WHERE cart_id = ?',
            #     (cart.)
            # )
            # for prod in cart.products:


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
