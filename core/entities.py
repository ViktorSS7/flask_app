from werkzeug.security import generate_password_hash, check_password_hash

from core.errors import ValidationException
from core.validate import validate_model, TYPES


class Entity:
    """Model interface"""
    rules = {}
    __validation_mode = False
    attributes = {}

    def serialize(self):
        result = {}
        for attribute in self.attributes:
            value = self.attributes[attribute]

            if isinstance(value, Entity):
                value = value.serialize()

            if attribute in self.rules:
                rules = self.rules[attribute]
                # Не добавлять в сериализированый объект, если скрыт
                if 'hidden' in rules:
                    continue

                # Приветсти к типу, который указан в rules
                for rule in rules:
                    if rule in TYPES:
                        value = TYPES[rule](value)
                        break

            result[attribute] = value
        return result

    def __init__(self, **kwargs):
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
        'username': ('required', 'str'),
        'password': ('required', 'str', 'hidden')
    }

    def set_password(self, value):
        return value
        # return generate_password_hash(value)

    def password_validate(self, password):
        return self.password == password
        # return check_password_hash(self.password, password)

    def __str__(self):
        return self.username
