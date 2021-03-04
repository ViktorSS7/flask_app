from flask import Blueprint, flash, g, redirect, render_template, \
    request, session, url_for

from flaskr.service import service, product as s_product, user as s_user, \
    cart as s_cart

from core import entities
from core.errors import ValidationException, MessageException

bp = Blueprint('cart', __name__, url_prefix='/cart/')


@bp.route('/', methods=('GET',))
def cart():
    context = {}
    user_id = session.get('user_id')

    cart = s_cart.build_cart_by_owner(user_id)

    context['cart'] = cart.serialize()

    return render_template('cart/list.html', **context)


@bp.route('/remove/<int:product_id>', methods=('GET', 'POST'))
def remove_product(product_id):
    cart = s_cart.build_cart_by_owner(session.get('user_id'))
    if cart:
        cart.products = list(filter(
            lambda prod: prod.id != product_id,
            cart.products
        ))
        s_cart.store_cart(cart)
    return redirect(url_for('cart.cart'))


@bp.route('/buy')
def buy():
    errors = []
    cart = s_cart.build_cart_by_owner(session.get('user_id'))
    try:
        cart.owner.buy_cart(cart)
    except MessageException as err:
        for e in err.messages:
            errors.append(e)
            flash(e)
    if errors:
        return redirect(url_for('cart.cart'))
    cart.products = list()
    s_user.store_user(cart.owner)
    s_cart.store_cart(cart)
    return redirect(url_for('product.product_list'))
