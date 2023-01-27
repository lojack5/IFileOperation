__all__ = [
    'IFileOperationError',
    'FileOperatorError',
    'UserCancelledError',
    # Backwards compatible exceptions:
    'IFO_NotADirectoryError',
]

import struct


def int32_to_uint32(value: int) -> int:
    """pythoncom defines its HRESULTs as signed integers for some reason."""
    return struct.unpack('I', struct.pack('i', value))[0]


class IFileOperationError(Exception):
    pass


class FileOperatorError(IFileOperationError):
    def __init__(self, hresult: int, msg: str, excepinfo=None, argerror=None) -> None:
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


# Backward Campatible exceptions: remove these in the next major version (2.0)
# These are for backwards campatibility when replacing specific HRESULT
# based exceptions with standard library exceptions
class IFO_NotADirectoryError(FileOperatorError, NotADirectoryError):
    """FileOperatorError with HRESULT E_DRIVE_NOT_FOUND"""

    pass
