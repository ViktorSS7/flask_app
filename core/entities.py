# from werkzeug.security import generate_password_hash, check_password_hash

from random import randint

from core.errors import MessageException
from core.validate import REQUIRED, COLLECTION
from core.localization import _

from core.libs.entity import Entity


class User(Entity):
    """User instance"""

    rules = {
        'username': (REQUIRED, 'str'),
        'password': (REQUIRED, 'str', 'hidden'),
        'coins': ('int', )
    }

    def __init__(self, **kwargs):
        if 'coins' not in kwargs:
            kwargs['coins'] = 0

        super().__init__(**kwargs)

    def set_password(self, value):
        return value
        # todo: нормальное хеширование
        # return generate_password_hash(value)

    def password_validate(self, password):
        return self.password == password
        # todo: нормальное хеширование
        # return check_password_hash(self.password, password)

    def change_password(self, old_password, new_password, repeat_password):
        if not self.password_validate(old_password):
            raise MessageException(_('Old password is invalid'))
        if not new_password == repeat_password:
            raise MessageException(
                _('New password is not equal with repeat password')
            )
        self.password = new_password

    def buy_cart(self, cart):
        if not cart.owner == self:
            raise MessageException(_('This cart not owner by user'))
        if not self.coins or self.coins < cart.cart_sum:
            raise MessageException(_('User have not enough coins'))

        price = cart.cart_sum
        self.coins -= price
        for product in cart.products:
            price = product.price
            product.owner.coins += price
            product.owner = self

    def __str__(self):
        return self.username


class Product(Entity):
    """Product instance"""

    rules = {
        'owner': ('required', User),
        'created': ('readonly', ),
        'title': ('required', 'str',),
        'price': ('required', 'int', )
    }

    def edit(self, editor, **kwargs):
        if not editor or not self.owner.id == editor.id:
            raise MessageException(
                _('User has not permission for edit this product'))
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.validate()

    def __str__(self):
        return self.title


class Cart(Entity):
    """Cart instance"""

    rules = {
        'hash': (REQUIRED, 'int', ),
        'owner': (REQUIRED, User, ),
        'products': (COLLECTION, Product, ),
        'cart_sum': ('int', )
    }

    def __init__(self, **kwargs):
        if 'hash' not in kwargs:
            kwargs['hash'] = randint(11111, 99999)

        super().__init__(**kwargs)

    def set_products(self, products):
        sum = 0
        for product in products:
            sum += product.price
        self.cart_sum = sum
        return products
