class BOAIException(Exception):
    """ Base Exception class for battleofai """
    pass


class ClientException(BOAIException):
    """
    Exception that's thrown when an operation in the :class: `Client` fails.

    These are usually for exceptions that happened due to user input.
    """
    pass


class HTTPException(BOAIException):
    """
    Exception that's thrown when an HTTP request operation fails.

    .. attribute:: response

        The response of the failed HTTP request. This is an
        instance of `aiohttp.ClientResponse`__.

        __ http://aiohttp.readthedocs.org/en/stable/client_reference.html#aiohttp.ClientResponse

    .. attribute:: message

        The text of the error. Could be an empty string.
    """

    def __init__(self, response, message: str=""):
        self.response = response
        self.message = message

        fmt = '{0.reason} (status code: {0.status})'
        if len(self.message):
            fmt = fmt + ': {1}'

        super().__init__(fmt.format(self.response, self.message))


class Unauthorized(HTTPException):
    """
    Exception that's thrown for when status code 401 occurs.

    Subclass of :exc:`HTTPException`
    """
    pass


class Forbidden(HTTPException):
    """
    Exception that's thrown for when status code 403 occurs.

    Subclass of :exc:`HTTPException`
    """
    pass


class NotFound(HTTPException):
    """
    Exception that's thrown for when status code 404 occurs.

    Subclass of :exc:`HTTPException`
    """
    pass


class LoginFailure(ClientException):
    """
    Exception that's thrown when the :meth:`IAMClient.login` function
    fails to log you in from improper credentials or some other misc.
    failure.
    """
    pass
