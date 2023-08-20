from vigobusapi.utils import get_datetime, new_hash_values
from ._entities import GoogleStreetviewRequest
from ._cache import CachedMap, MapVendors, MapTypes


def test_cached_map_generates_id():
    request = GoogleStreetviewRequest(location_x=1, location_y=1, size_x=1, size_y=1)
    cache = CachedMap(
        key=request.checksum_value,
        vendor=MapVendors.google_maps,
        type=MapTypes.photo,
        data=request,
        saved=get_datetime()
    )

    expected_id = new_hash_values(
        cache.key,
        cache.vendor.value,
        cache.type.value,
        algorithm="sha256"
    ).hexdigest()

    assert cache.id == expected_id
    assert cache.dict()["id"] == expected_id
    assert cache.to_mongo()["_id"] == expected_id
