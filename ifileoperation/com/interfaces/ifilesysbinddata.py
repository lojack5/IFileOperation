__all__ = [
    'IFileSysBindData',
]

from ctypes import POINTER
from ctypes.wintypes import PWIN32_FIND_DATAW

from comtypes import COMMETHOD, GUID, HRESULT, IUnknown


class IFileSysBindData(IUnknown):
    """Define the IFileSysBindData interface using comtypes, see
    https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-ifilesystembinddata
    https://github.com/tpn/winsdk-10/blob/9b69fd26ac0c7d0b83d378dba01080e93349c2ed/Include/10.0.16299.0/um/ShObjIdl_core.h#L24285
    """

    _iid_ = GUID('{01e18d10-4d8b-11d2-855d-006008059367}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'SetFindData', (['in'], PWIN32_FIND_DATAW, 'pfd')),
        COMMETHOD(
            [], HRESULT, 'GetFindData', (['out'], POINTER(PWIN32_FIND_DATAW), 'ppfd')
        ),
    ]
