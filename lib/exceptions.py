
class LibError(Exception):
    pass


class AccessError(LibError):
    pass


class UpdateError(LibError):
    pass


class CreateError(LibError):
    pass


class ObjectNotFound(LibError):
    pass


class DuplicateRelation(UpdateError):
    pass


class TimeError(LibError):
    pass
