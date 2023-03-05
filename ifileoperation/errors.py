__all__ = [
    'IFileOperationError',
    'FileOperatorError',
    'UserCancelledError',
    'InterfaceNotImplementedError',
    # Backwards compatible exceptions:
    'IFO_NotADirectoryError',
]

import struct


def int32_to_uint32(value: int) -> int:
    """pythoncom defines its HRESULTs as signed integers for some reason."""
    return struct.unpack('I', struct.pack('i', value))[0]


class IFileOperationError(Exception):
    pass


class InterfaceNotImplementedError(IFileOperationError):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            'COM interface method not implemented.  This is likely a WINE bug, see: '
            'https://bugs.winehq.org/show_bug.cgi?id=50064.'
        )


class FileOperatorError(IFileOperationError):
    def __init__(
        self,
        hresult: int = 0,
        msg: str = '',
        excepinfo=None,
        argerror=None,
        *args,
        **kwargs,
    ) -> None:
        if hresult < 0:
            hresult = int32_to_uint32(hresult)
        self.hresult = hresult
        if excepinfo or argerror:
            msg = f'{hex(hresult)}: {msg}, {excepinfo}, {argerror}'
        else:
            msg = f'{hex(hresult)}: {msg}'
        super().__init__(msg)


class UserCancelledError(IFileOperationError):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__('User cancelled the operation')


class UnexpectedError(IFileOperationError):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(f'An unexpected error occurred: {args}, {kwargs}')


# Backward Campatible exceptions: remove these in the next major version (2.0)
# These are for backwards campatibility when replacing specific HRESULT
# based exceptions with standard library exceptions
class IFO_NotADirectoryError(FileOperatorError, NotADirectoryError):
    """FileOperatorError with HRESULT E_DRIVE_NOT_FOUND"""
