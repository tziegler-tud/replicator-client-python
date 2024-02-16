from enum import Enum

class ApiStatus(Enum):
    OK = 200
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    ERROR = 500

class ApiResponse:

    # /**
    #      * tcp response protocol prototype:
    #      * response codes:
    #      * 200: OK
    #      * 500: Error
    #      *
    #      * Error codes:
    #      * 1-10 connection errors:
    #      *  1: connection failed
    #      *
    #      *
    #      * 11-20 argument errors:
    #      *  11: missing required argument
    #      *  12: wrong argument type
    #      *  13: invalid clientId
    #      *
    #      * 21-30 client registration related errors:
    #      *  21: not registered
    #      *  22: registration invalid
    #      *  23: registration expired
    #      *  24: registration incomplete
    #      *  25: already registered
    #      *  26: registration not allowed
    #      */
    
    def __init__(self, response):
        self.status = response.status
        self.result =  response

