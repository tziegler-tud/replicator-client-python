from enum import Enum
class ApiResponse:

    apiStatus = {
        'OK': 200,
        'UNAUTHORIZED': 401,
        'FORBIDDEN': 403,
        'ERROR': 500,
    }

    apiResponse = {
        'CONNECTION': {
            'SUCCESSFUL': {
                'status': apiStatus['OK'],
                'code': 0,
                'message': 'Connection successful',
            },
            'FAILED': {
                'status': apiStatus['ERROR'],
                'code': 1,
                'message': 'Connection failed',
            },
        },
        'ARGUMENTS': {
            'MISSING': {
                'status': apiStatus['ERROR'],
                'code': 11,
                'message': 'Arguments missing',
            },
            'TYPEMISMATCH': {
                'status': apiStatus['ERROR'],
                'code': 12,
                'message': 'Arguments type mismatch',
            },
            'INVALIDCLIENTID': {
                'status': apiStatus['ERROR'],
                'code': 13,
                'message': 'ClientId does not match connection authorization',
            },
        },
        'REGISTRATION': {
            'SUCCESSFUL': {
                'status': apiStatus['OK'],
                'code': 0,
                'message': 'Registration Successful',
            },
            'NOTREGISTERED': {
                'status': apiStatus['UNAUTHORIZED'],
                'code': 21,
                'message': 'Not registered',
            },
            'INVALID': {
                'status': apiStatus['ERROR'],
                'code': 22,
                'message': 'Registration invalid',
            },
            'EXPIRED': {
                'status': apiStatus['UNAUTHORIZED'],
                'code': 23,
                'message': 'Registration expired',
            },
            'INCOMPLETE': {
                'status': apiStatus['ERROR'],
                'code': 24,
                'message': 'Registration incomplete',
            },
            'ALREADYREGISTERED': {
                'status': apiStatus['OK'],
                'code': 25,
                'message': 'Client already registered',
            },
            'NOTALLOWED': {
                'status': apiStatus['ERROR'],
                'code': 26,
                'message': 'Registration not allowed',
            },
            'RENEWED': {
                'status': apiStatus['OK'],
                'code': 27,
                'message': 'Registration renewed',
            },
            'FAILED': {
                'status': apiStatus['ERROR'],
                'code': 28,
                'message': 'Registration failed',
            },
        },
    }

    def __init__(self, response):
        self.status = response['status']
        self.message = response['message']
        self.code = response['code']
        self.response = response

class ReponseTypes(Enum):
    class CONNECTION(Enum):
        SUCCESSFUL = ApiResponse.apiResponse["CONNECTION"]["SUCCESSFUL"]
        FAILED = ApiResponse.apiResponse["CONNECTION"]["FAILED"]
    class REGISTRATION(Enum):
        NOTREGISTERED = ApiResponse.apiResponse["REGISTRATION"]["NOTREGISTERED"]
        INVALID = ApiResponse.apiResponse["REGISTRATION"]["INVALID"]
        EXPIRED = ApiResponse.apiResponse["REGISTRATION"]["EXPIRED"]
        INCOMPLETE = ApiResponse.apiResponse["REGISTRATION"]["INCOMPLETE"]
        ALREADYREGISTERED = ApiResponse.apiResponse["REGISTRATION"]["ALREADYREGISTERED"]
        NOTALLOWED = ApiResponse.apiResponse["REGISTRATION"]["NOTALLOWED"]
        RENEWED = ApiResponse.apiResponse["REGISTRATION"]["RENEWED"]
        SUCCESSFUL = ApiResponse.apiResponse["REGISTRATION"]["SUCCESSFUL"]
        FAILED = ApiResponse.apiResponse["REGISTRATION"]["FAILED"]

    class ARGUMENTS(Enum):
        MISSING = ApiResponse.apiResponse["ARGUMENTS"]["MISSING"]
        TYPEMISMATCH = ApiResponse.apiResponse["ARGUMENTS"]["TYPEMISMATCH"]
        INVALIDCLIENTID = ApiResponse.apiResponse["ARGUMENTS"]["INVALIDCLIENTID"]
