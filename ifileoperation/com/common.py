__all__ = [
    'convert_exceptions',
    'com_ptr',
]

import struct
from ctypes import POINTER, PyDLL, byref, c_bool, c_void_p, py_object
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

import pythoncom
from comtypes import COMObject, IUnknown

from ..errors import FileOperatorError
from ..flags import FileOperationResult

PIUnknown = POINTER(IUnknown)  # type: ignore
P = ParamSpec('P')
T = TypeVar('T')


_PYCOM_PyObjectFromIUnknown = PyDLL(pythoncom.__file__).PyCom_PyObjectFromIUnknown
_PYCOM_PyObjectFromIUnknown.restype = py_object
_PYCOM_PyObjectFromIUnknown.argtypes = (PIUnknown, c_void_p, c_bool)


def com_ptr(com_object: COMObject):
    return _PYCOM_PyObjectFromIUnknown(com_object, byref(IUnknown._iid_), True)


_hresult_to_exception = {
    FileOperationResult.E_DESTINATION_IS_FILE: NotADirectoryError,
    FileOperationResult.E_DESTINATION_IS_FOLDER: IsADirectoryError,
    FileOperationResult.E_ACCESS_DENIED_DESTINATION: PermissionError,
    FileOperationResult.E_ACCESS_DENIED_SOURCE: PermissionError,
    FileOperationResult.E_REQUIRES_ELEVATION: PermissionError,
    FileOperationResult.E_ALREADY_EXISTS_FOLDER: FileExistsError,
    FileOperationResult.E_ALREADY_EXISTS_NORMAL: FileExistsError,
    FileOperationResult.E_ALREADY_EXISTS_READONLY: FileExistsError,
    FileOperationResult.E_ALREADY_EXISTS_SYSTEM: FileExistsError,
    # Note: FileNoteFound should be handled by parse_name already
}


def convert_exceptions(callable: Callable[P, T]) -> Callable[P, T]:
    """Wraps a method to automatically convert pythoncom.com_error exceptions
    into FileOperatorError exceptions.
    """
    # TODO: Implement mapping to builtin Python exceptions for common
    # HRESULTs, e.g. E_ACCESSDENIED, E_OUTOFMEMORY, etc.
    @wraps(callable)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return callable(*args, **kwargs)
        except pythoncom.com_error as e:
            # pywin32 defines it's HRESULTS using signed integers, but all the
            # definitions online use unsigned.
            hresult = e.hresult  # type: ignore
            if hresult < 0:
                hresult = struct.unpack('I', struct.pack('i', hresult))[0]
            if hresult in _hresult_to_exception:
                raise _hresult_to_exception[hresult](*e.args) from e
            else:
                raise FileOperatorError(*e.args) from e

    return wrapped
