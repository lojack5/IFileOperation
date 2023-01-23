__all__ = [
    'convert_exceptions',
    'com_ptr',
]

from functools import wraps
from ctypes import PyDLL, py_object, c_void_p, c_bool, POINTER, byref
from typing import Callable, ParamSpec, TypeVar

import pythoncom

from comtypes import IUnknown, COMObject

from ..errors import FileOperatorError

PIUnknown = POINTER(IUnknown)   # type: ignore
P = ParamSpec('P')
T = TypeVar('T')


_PYCOM_PyObjectFromIUnknown = PyDLL(pythoncom.__file__).PyCom_PyObjectFromIUnknown
_PYCOM_PyObjectFromIUnknown.restype = py_object
_PYCOM_PyObjectFromIUnknown.argtypes = (PIUnknown, c_void_p, c_bool)


def com_ptr(com_object: COMObject):
    return _PYCOM_PyObjectFromIUnknown(com_object, byref(IUnknown._iid_), True)


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
            raise FileOperatorError(*e.args) from None

    return wrapped
