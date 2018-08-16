
class BaseLibError(Exception):
    pass


class AccessError(BaseLibError):
    pass


class FolderExist(BaseLibError):
    pass


class UpdateError(BaseLibError):
    pass


class ObjectNotFound(BaseLibError):
    pass
