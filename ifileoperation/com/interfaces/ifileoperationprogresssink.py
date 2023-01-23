__all__ = [
    'IFileOperationProgressSink',
]

from ctypes import c_long
from ctypes.wintypes import DWORD, LPCWSTR, UINT

from comtypes import COMMETHOD, GUID, HRESULT, IUnknown

from .ishellitem import PIShellItem


class IFileOperationProgressSink(IUnknown):
    """Define the IFileOperationSink interface using comtypes, see
    https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-ifileoperationprogresssink
    https://github.com/tpn/winsdk-10/blob/9b69fd26ac0c7d0b83d378dba01080e93349c2ed/Include/10.0.16299.0/um/ShObjIdl_core.h#L9652
    """

    _iid_ = GUID('{04b0f1a7-9490-44bc-96e1-4296a31252e2}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'StartOperations'),
        COMMETHOD([], HRESULT, 'FinishOperations', (['in'], c_long, 'hrResult')),
        COMMETHOD(
            [],
            HRESULT,
            'PreRenameItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['string', 'unique', 'in'], LPCWSTR, 'pszNewName'),
        ),
        COMMETHOD(
            [],
            HRESULT,
            'PostRenameItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['string', 'in'], LPCWSTR, 'pszNewName'),
            (['in'], HRESULT, 'hrRename'),
            (['in'], PIShellItem, 'psiNewlyCreated'),
        ),
        COMMETHOD(
            [],
            HRESULT,
            'PreMoveItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['in'], PIShellItem, 'psiDestinationFolder'),
            (['string', 'unique', 'in'], LPCWSTR, 'pszNewName'),
        ),
        COMMETHOD(
            [],
            HRESULT,
            'PostMoveItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['in'], PIShellItem, 'psiDestinationFolder'),
            (['string', 'unique', 'in'], LPCWSTR, 'pszNewName'),
            (['in'], c_long, 'hrMove'),
            (['in'], PIShellItem, 'psiNewlyCreated'),
        ),
        COMMETHOD(
            [],
            HRESULT,
            'PreCopyItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['in'], PIShellItem, 'psiDestinationFolder'),
            (['string', 'unique', 'in'], LPCWSTR, 'pszNewName'),
        ),
        COMMETHOD(
            [],
            HRESULT,
            'PostCopyItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['in'], PIShellItem, 'psiDestinationFolder'),
            (['string', 'unique', 'in'], LPCWSTR, 'pszNewName'),
            (['in'], HRESULT, 'hrCopy'),
            (['in'], PIShellItem, 'psiNewlyCreated'),
        ),
        COMMETHOD(
            [],
            HRESULT,
            'PreDeleteItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
        ),
        COMMETHOD(
            [],
            HRESULT,
            'PostDeleteItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['in'], HRESULT, 'hrDelete'),
            (['in'], PIShellItem, 'psiNewlyCreated'),
        ),
        COMMETHOD(
            [],
            HRESULT,
            'PreNewItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiDestinationFolder'),
            (['string', 'unique', 'in'], LPCWSTR, 'pszNewName'),
        ),
        COMMETHOD(
            [],
            HRESULT,
            'PostNewItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiDestinationFolder'),
            (['string', 'unique', 'in'], LPCWSTR, 'pszNewName'),
            (['string', 'unique', 'in'], LPCWSTR, 'pszTemplateName'),
            (['in'], DWORD, 'dwFileAttributes'),
            (['in'], HRESULT, 'hrNew'),
            (['in'], PIShellItem, 'psiNewItem'),
        ),
        COMMETHOD(
            [],
            HRESULT,
            'UpdateProgress',
            (['in'], UINT, 'iWorkTotal'),
            (['in'], UINT, 'iWorkSoFar'),
        ),
        COMMETHOD([], HRESULT, 'ResetTimer'),
        COMMETHOD([], HRESULT, 'PauseTimer'),
        COMMETHOD([], HRESULT, 'ResumeTimer'),
    ]
