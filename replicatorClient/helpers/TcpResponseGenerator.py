class TcpResponseGenerator:
    def __init__(self):
        self.tcpStatus = {
            'OK': 200,
            'UNAUTHORIZED': 401,
            'FORBIDDEN': 403,
            'ERROR': 500,
        }

        self.tpcResponse = {
            'CONNECTION': {
                'SUCCESSFUL': {
                    'status': self.tcpStatus['OK'],
                    'code': 0,
                    'message': 'Connection successful'
                },
                'FAIL': {
                    'status': self.tcpStatus['ERROR'],
                    'code': 1,
                    'message': 'Connection failed'
                },
            },
            'ARGUMENTS': {
                'MISSING': {
                    'status': self.tcpStatus['ERROR'],
                    'code': 11,
                    'message': 'Arguments missing',
                },
                'TYPEMISMATCH': {
                    'status': self.tcpStatus['ERROR'],
                    'code': 12,
                    'message': 'Arguments type mismatch',
                },
                'INVALIDCLIENTID': {
                    'status': self.tcpStatus['ERROR'],
                    'code': 13,
                    'message': 'ClientId does not match connection authorization',
                }
            },
            'REGISTRATION': {
                'SUCCESSFUL': {
                    'status': self.tcpStatus['OK'],
                    'code': 0,
                    'message': 'Registration successful'
                },
                'NOTREGISTERED': {
                    'status': self.tcpStatus['UNAUTHORIZED'],
                    'code': 21,
                    'message': 'Not registered',
                },
                'INVALID': {
                    'status': self.tcpStatus['ERROR'],
                    'code': 22,
                    'message': 'Registration invalid',
                },
                'EXPIRED': {
                    'status': self.tcpStatus['UNAUTHORIZED'],
                    'code': 23,
                    'message': 'Registration expired',
                },
                'INCOMPLETE': {
                    'status': self.tcpStatus['ERROR'],
                    'code': 24,
                    'message': 'Registration incomplete',
                },
                'ALREADYREGISTERED': {
                    'status': self.tcpStatus['ERROR'],
                    'code': 25,
                    'message': 'Client already registered.',
                },
                'NOTALLOWED': {
                    'status': self.tcpStatus['ERROR'],
                    'code': 26,
                    'message': 'Registration not allowed.',
                }
            },
            'COMMAND': {
                'SUCCESSFUL': {
                    'status': self.tcpStatus['OK'],
                    'code': 0,
                    'message': 'Command execution successful.'
                },
                'INVALID': {
                    'status': self.tcpStatus['UNAUTHORIZED'],
                    'code': 21,
                    'message': 'Invalid command received.',
                },
                'INVALID_ARGUMENT': {
                    'status': self.tcpStatus['ERROR'],
                    'code': 22,
                    'message': 'Invalid argument received.',
                },
                'INTERNAL_ERROR': {
                    'status': self.tcpStatus['UNAUTHORIZED'],
                    'code': 23,
                    'message': 'Internal error while executing command.',
                },
                'NOTALLOWED': {
                    'status': self.tcpStatus['ERROR'],
                    'code': 26,
                    'message': 'Command not allowed.',
                }
            }
        }

tcp_response_generator = TcpResponseGenerator()