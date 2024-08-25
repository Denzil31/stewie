class BaseException(Exception):
    def __init__(self, message, code=None, *args, **kwargs):
        self.message = message
        self.code = code
        self.args = args
        self.kwargs = kwargs
        super().__init__(message, *args, **kwargs)

    def __str__(self):
        return self.message

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.code}: {self.message}, args={self.args}, kwargs={self.kwargs}>'


class ConfigError(BaseException):
    """
    Raised when there is a configuration error.
    """

    def __init__(self, message='Configuration error.', code=400, *args, **kwargs):
        super().__init__(message, code, *args, **kwargs)


class ShortCodeNotFoundError(BaseException):
    """
    Raised when a short code is not found in the database.
    """

    def __init__(self, message='Short code not found.', code=404, *args, **kwargs):
        super().__init__(message, code, *args, **kwargs)


class ShortCodeAlreadyExistsError(BaseException):
    """
    Raised when a short code already exists in the database.
    """

    def __init__(self, message='Short code already exists.', code=400, *args, **kwargs):
        super().__init__(message, code, *args, **kwargs)


class InvalidShortCodeError(BaseException):
    """
    Raised when a short code is invalid.
    """

    def __init__(
        self, message='Invalid characters in the short code.', code=400, *args, **kwargs
    ):
        super().__init__(message, code, *args, **kwargs)


class ExpiryTooHighError(BaseException):
    """
    Raised when the expiration is too high.
    """

    def __init__(
        self,
        message='Expiration cannot be greater than 1 year.',
        code=400,
        *args,
        **kwargs,
    ):
        super().__init__(message, code, *args, **kwargs)


class MaxRetriesExceededError(BaseException):
    """
    Raised when the maximum number of retries is exceeded.
    """

    def __init__(self, message='Max retries exceeded.', code=400, *args, **kwargs):
        super().__init__(message, code, *args, **kwargs)


class InvalidLongUrlError(BaseException):
    """
    Raised when a long URL is invalid.
    """

    def __init__(self, message='Long URL is invalid.', code=400, *args, **kwargs):
        super().__init__(message, code, *args, **kwargs)


class DatabaseError(BaseException):
    """
    Raised when there is a database error.
    """

    def __init__(self, message='Database error.', code=424, *args, **kwargs):
        super().__init__(message, code, *args, **kwargs)


class LinkExpiredError(BaseException):
    """
    Raised when a short link has expired.
    """

    def __init__(self, message='Short link has expired.', code=410, *args, **kwargs):
        super().__init__(message, code, *args, **kwargs)
