import hashlib
import pytest
from vigobusapi.utils import new_hash_values, update_hash_values


@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_new_hash_values(algorithm: str):
    hashes = {
        "md5": hashlib.md5,
        "sha256": hashlib.sha256
    }
    data = ["a string", 1, True, None, [1, "other string", False, None]]

    _hash = hashes[algorithm]()
    for chunk in data:
        _hash.update(str(chunk).encode())

    expected_hexdigest = _hash.hexdigest()
    result_hexdigest = new_hash_values(*data, algorithm=algorithm).hexdigest()

    assert result_hexdigest == expected_hexdigest


@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_update_hash_values(algorithm: str):
    hashes = {
        "md5": hashlib.md5,
        "sha256": hashlib.sha256
    }
    full_hash = hashes[algorithm]()
    original_hash = hashes[algorithm]()

    original_data = ["initial string", 0.0]
    for chunk in original_data:
        original_hash.update(str(chunk).encode())
        full_hash.update(str(chunk).encode())

    new_data = ["a string", 1, True, None, [1, "other string", False, None]]
    for chunk in new_data:
        full_hash.update(str(chunk).encode())

    expected_hexdigest = full_hash.hexdigest()
    result_hexdigest = update_hash_values(*new_data, _hash=original_hash).hexdigest()

    assert result_hexdigest == expected_hexdigest
