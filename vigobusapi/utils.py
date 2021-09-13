"""UTILS
Misc functions
"""

# # Native # #
import abc
import hashlib

__all__ = ("ChecksumableClass", "new_hash_values", "update_hash_values")


class ChecksumableClass(abc.ABC):
    """Abstract class where inheritors can use methods for acquiring a checksum/hash, based on fields from the class."""

    @property
    @abc.abstractmethod
    def checksum_hash(self):
        """Returns a SHA256 checksum of all the fields in the request.
        As an abstract method, must be completed returning a new hash object, from the hashlib library. The hash
        shall be updated with the values from the object that will be used for calculating checksum, on a given order.
        The methods new_hash_values() and update_hash_values() from utils module may be used for this purpose."""
        pass

    @property
    def checksum_value(self) -> str:
        """Returns the str value (hexdigest) from the checksum_hash output."""
        return self.checksum_hash.hexdigest()


def update_hash_values(*args, _hash):
    """Update the given hash_obj (_Hash object created with the hashlib library) with the values given as *args,
    in the given order. The values must be strings, or objects parseable to string using str().
    Returns the given object."""
    for value in args:
        _hash.update(str(value).encode())
    return _hash


def new_hash_values(*args, algorithm: str):
    """Create a new hash, using the given algorithm, and update it with the values given as *args, in the given order.
    The values must be strings, or objects parseable to string using str().
    Returns the hash object (the hash/checksum value can be acquired by using str(output))."""
    _hash = hashlib.new(algorithm)
    return update_hash_values(*args, _hash=_hash)
