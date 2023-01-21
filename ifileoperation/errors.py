__all__ = [
    'IFileOperationError',
    'FileOperatorError',
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
