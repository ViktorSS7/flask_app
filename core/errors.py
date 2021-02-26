from core.localization import _


class MessageException(Exception):
    def __init__(self, *args, **kwargs):
        self.messages = args
        self.obj = kwargs


class ValidationException(MessageException):
    pass
