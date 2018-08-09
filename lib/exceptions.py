
class AccessError(Exception):
    pass


class FolderExist(Exception):
    pass


class ObjectNotFound(Exception):
    pass


def check_object_exist(obj, param, type):
    if obj is None:
        raise ObjectNotFound(f'type with {param} not found')
