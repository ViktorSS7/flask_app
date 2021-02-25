from core.localization import _

REQUIRED = 'required'
TYPES = {
    'int': int,
    'str': str,
    'float': float
}


def validate_model(entity):
    errors = []
    for key in entity.rules:
        required = False
        value_type = ''

        for rule in entity.rules[key]:
            if rule == REQUIRED:
                required = True
            if rule in TYPES:
                value_type = rule

        value = getattr(entity, key)

        if not value and required:
            errors.append(_('%s is required.' % key))

        try:
            setattr(entity, key, TYPES[value_type](value))
        except TypeError:
            errors.append(_('Can\'t convert %s to %s' % (key, value_type)))

    return errors
