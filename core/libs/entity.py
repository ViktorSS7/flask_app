from core.validate import TYPES, validate_model
from core.errors import ValidationException


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
        if key == 'attributes':
            super().__setattr__(key, value)
            return
        if hasattr(self, self._get_key_mutator(key)):
            value = getattr(self, self._get_key_mutator(key))(value)
        self.attributes[key] = value

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


