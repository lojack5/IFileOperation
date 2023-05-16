from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from ifileoperation import FileOperator, IFileOperationError

def test_reentrance():
    # Reentrance is not allowed.
    op = FileOperator()
    with op:
        with pytest.raises(IFileOperationError):
            with op:
                pass

def test_reuse():
    # Re-use is OK
    op = FileOperator()
    with op:
        pass
    with op:
        pass

def test_threading():
    # Test the COM is initialized correctly in multi-threaded applications
    def worker(i: int) -> int:
        op = FileOperator()
        with op:
            return i
    executor = ThreadPoolExecutor(max_workers=10)
    futures = [executor.submit(worker, i) for i in range(50)]
    results = sorted(r.result() for r in as_completed(futures))
    assert results == list(range(50))
