import pytest
from vigobusapi.services.google_maps import GoogleMapRequest
from vigobusapi.utils import new_hash_values


@pytest.mark.parametrize("obj", [
    GoogleMapRequest(location_x=1, location_y=2, size_x=1, size_y=2, zoom=1),
    GoogleMapRequest(location_x=1, location_y=2, size_x=1, size_y=2, zoom=2),
    GoogleMapRequest(location_x=1, location_y=2, size_x=1, size_y=2, zoom=2,
                     map_type=GoogleMapRequest.MapTypes.hybrid),
    GoogleMapRequest(location_x=1, location_y=2, size_x=1, size_y=2, zoom=2,
                     map_type=GoogleMapRequest.MapTypes.satellite,
                     tags=[GoogleMapRequest.Tag(label="A", location_x=10, location_y=20),
                           GoogleMapRequest.Tag(label="B", location_x=30, location_y=40)])
])
def test_google_map_request(obj: GoogleMapRequest):
    tags_hash_value = "NoTags"
    if obj.tags:
        tags_hash_value = sorted([tag.checksum_value for tag in obj.tags])

    _hash = new_hash_values(
        obj.location_x,
        obj.location_y,
        obj.size_x,
        obj.size_y,
        obj.zoom,
        obj.map_type,
        tags_hash_value,
        algorithm="sha256"
    )

    expected_checksum = _hash.hexdigest()
    obj_checksum = obj.checksum_value
    assert obj_checksum == expected_checksum
