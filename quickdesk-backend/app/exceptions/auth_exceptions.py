class AuthException(Exception):
    pass

class InvalidCredentialsException(AuthException):
    pass

class UserAlreadyExistsException(AuthException):
    pass

class UserNotFoundException(AuthException):
    pass

class UnauthorizedException(AuthException):
    pass

class InvalidTokenException(UnauthorizedException):
    pass

class InvalidUserIDException(UnauthorizedException):
    pass


class TokenMissingException(UnauthorizedException):
    pass

