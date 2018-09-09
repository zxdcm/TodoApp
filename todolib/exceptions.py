
class LibError(Exception):
    """Base lib error class"""
    pass


class ObjectNotFound(LibError):
    """Raises when trying to retrieve object that doesnt exist"""
    pass


class LibWarning(Warning):
    """Base lib warning class"""
    pass


class RedundancyAction(LibWarning):
    """Raises when trying to perform action that already has been applied"""
    pass
