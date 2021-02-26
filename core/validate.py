from core.localization import _

REQUIRED = 'required'
TYPES = {
    'int': int,
    'str': str,
    'float': float
}


def validate_model(entity):
    from core.entities import Entity
    errors = []
    for key in entity.rules:

        required = False
        value_type = None
        value_instance = None

        for rule in entity.rules[key]:
            if rule == REQUIRED:
                required = True
            if rule in TYPES:
                value_type = rule
            if isinstance(rule, Entity):
                value_instance = rule

        if not hasattr(entity, key):
            if required:
                errors.append(_('%s is required.' % key))
            continue

        value = getattr(entity, key)

        if not hasattr(entity, key):
            errors.append(_('%s is required.' % key))

        if value_type:
            try:
                setattr(entity, key, TYPES[value_type](value))
            except TypeError:
                errors.append(_('Can\'t convert %s to %s' % (key, value_type)))

        if value_instance and\
           not isinstance(value, value_instance):
            errors.append(
                _('Can\'t convert %s to %s' % (key, str(value_instance)))
            )

    return errors
