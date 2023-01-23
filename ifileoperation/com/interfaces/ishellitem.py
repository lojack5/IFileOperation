__all__ = [
    'IShellItem',
    'PIShellItem',
]

from ctypes import POINTER
from ctypes.wintypes import DWORD, LPWSTR

from comtypes import COMMETHOD, GUID, HRESULT, IUnknown


class _IShellItem(IUnknown):
    """partially define the IShellItem interface using comtypes, only GetDisplayName
    is implemented, see
    https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-ishellitem
    https://github.com/tpn/winsdk-10/blob/9b69fd26ac0c7d0b83d378dba01080e93349c2ed/Include/10.0.16299.0/um/ShObjIdl_core.h#L7933
    """

    _iid_ = GUID('{43826d1e-e718-42ee-bc55-a1e261c37bfe}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'BindToHandler'),
        COMMETHOD([], HRESULT, 'GetParent'),
        COMMETHOD(
            [],
            HRESULT,
            'GetDisplayName',
            (['in'], DWORD, 'sigdnName'),
            (['annotation', 'string', 'out'], POINTER(LPWSTR), 'ppszName'),
        ),
        COMMETHOD([], HRESULT, 'GetAttributes'),
    ]


PIShellItem = POINTER(_IShellItem)  # type: ignore


class IShellItem:
    """IShellItem interface, for typehints only"""

    def GetDisplayName(self, sigdnName: int) -> str:
        ...
