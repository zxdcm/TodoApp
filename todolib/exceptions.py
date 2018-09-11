"""
    Module contains exceptions and warnings used by library
"""

class LibError(Exception):
    """Base lib error class"""
    pass


class ObjectNotFoundError(LibError):
    """Raises on retrieve object that doesnt exist"""
    pass


class LibWarning(Warning):
    """Base lib warning class"""
    pass


class RedundancyActionWarning(LibWarning):
    """Raises when performs action that already has been applied"""
    pass
