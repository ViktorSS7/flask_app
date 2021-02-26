# from werkzeug.security import generate_password_hash, check_password_hash

from core.errors import MessageException, ValidationException
from core.validate import validate_model, TYPES, REQUIRED
from core.localization import _


class Entity:
    """Model interface"""
    rules = {}
    __validation_mode = False

    def serialize(self):
        result = {}
        for attribute in self.attributes:
            value = self.attributes[attribute]

            if attribute in self.rules:
                rules = self.rules[attribute]
                # Не добавлять в сериализированый объект, если скрыт
                if 'hidden' in rules:
                    continue

                for rule in rules:
                    # Приветсти к типу, который указан в rules
                    if rule in TYPES:
                        value = TYPES[rule](value)
                        break

            if isinstance(value, Entity):
                value = value.serialize()

            result[attribute] = value
        return result

    def __init__(self, **kwargs):
        self.attributes = {}

        for key in kwargs:
            setattr(self, key, kwargs[key])

        self.validate()

    def __setattr__(self, key, value):
        if key in self.rules:
            if hasattr(self, self._get_key_mutator(key)):
                value = getattr(self, self._get_key_mutator(key))(value)
            self.attributes[key] = value
        else:
            super().__setattr__(key, value)

    def __getattr__(self, item):
        if item in self.attributes:
            return self.attributes[item]
        else:
            super().__getattribute__(item)

    def validate(self):
        errors = validate_model(self)
        if errors:
            raise ValidationException(*errors)

    def _get_key_mutator(self, key):
        return 'set_%s' % key


class User(Entity):
    """User instance"""

    rules = {
        'username': (REQUIRED, 'str'),
        'password': (REQUIRED, 'str', 'hidden'),
        'coins': ('int', )
    }

    def set_password(self, value):
        return value
        # todo: нормальное хеширование
        # return generate_password_hash(value)

    def password_validate(self, password):
        return self.password == password
        # todo: нормальное хеширование
        # return check_password_hash(self.password, password)

    def change_password(self, old_password, new_password, repeat_password):
        if self.password_validate(old_password) and\
           new_password == repeat_password:
            self.password = new_password

    def buy_product(self, product):
        if not self.coins or self.coins < product.price:
            raise MessageException(_('User have not enough coins'))

        price = product.price
        product.owner.coins += price
        self.coins -= price
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

    def __str__(self):
        return self.title