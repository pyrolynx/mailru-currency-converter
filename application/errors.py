class APIError(Exception):
    pass

class EntityNotFound(APIError):
    pass