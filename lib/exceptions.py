
class LibError(Exception):
    pass


class ObjectNotFound(LibError):
    pass


class LibWarning(Warning):
    pass


class ActionWarning(LibWarning):
    pass


class RedundancyAction(ActionWarning):
    pass
