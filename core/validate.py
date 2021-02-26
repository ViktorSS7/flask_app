from core.localization import _

REQUIRED = 'required'
COLLECTION = 'collection'
TYPES = {
    'int': int,
    'str': str,
    'float': float
}


def get_base_entity_instance():
    from core.entities import Entity
    return Entity


class FieldValidator:
    def __init__(self, filed_key, entity, rules):
        # input data
        self.field_key = filed_key
        self.entity = entity
        self.field_rules = rules

        # field flags
        self.required = False
        self.collection = False
        self.value_type = None
        self.value_instance = None

        # base entity instance
        self.ENTITY = get_base_entity_instance()

        # error list
        self.errors = list()

        # field value
        self.value = None

    def __call__(self):
        self.set_flags()

        if self.entity_has_attr():
            self.value = getattr(self.entity, self.field_key)
            if self.collection:
                for item in self.value:
                    self.type_validate(item)
            else:
                self.type_validate(self.value)
        return self.errors

    def set_flags(self):
        for rule in self.field_rules:
            if rule == REQUIRED:
                self.required = True
            if rule == COLLECTION:
                self.collection = True
            if rule in TYPES:
                self.value_type = rule
            if isinstance(rule, self.ENTITY):
                self.value_instance = rule

    def entity_has_attr(self):
        if not hasattr(self.entity, self.field_key):
            if self.required:
                self.errors.append(_('%s is required.' % self.field_key))
            return False
        return True

    def type_validate(self, value):
        if self.value_type:
            try:
                TYPES[self.value_type](value)
            except TypeError:
                self.errors.append(
                    _('Can\'t convert %s to %s' %
                      (self.field_key, self.value_type))
                )
                return False
        elif self.value_instance and\
                not isinstance(value, self.value_instance):
            self.errors.append(
                _('Can\'t convert %s to %s' %
                  (self.field_key, str(self.value_instance)))
            )
            return False
        return True


def validate_model(entity):
    errors = []
    for key in entity.rules:
        field_errors = FieldValidator(key, entity, entity.rules[key])()
        errors += field_errors
    return errors
