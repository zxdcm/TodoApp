
class BaseLibError(Exception):
    pass


class AccessError(BaseLibError):
    pass


class UpdateError(BaseLibError):
    pass


class CreateError(BaseLibError):
    pass


class ObjectNotFound(BaseLibError):
    pass


class DuplicateRelation(UpdateError):
    pass
