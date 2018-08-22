
class LibError(Exception):
    pass


class ObjectNotFound(LibError):
    pass


class LibWarning(Warning):
    pass


class RedundancyAction(LibWarning):
    pass
