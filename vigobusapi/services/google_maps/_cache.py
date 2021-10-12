"""GOOGLE MAPS - CACHE
Cache utils for reading/writing persistence of cached Maps & StreetView pictures
"""

# # Native # #
import enum
import datetime
import asyncio
from typing import Union, Optional

# # Installed # #
from pymongo.results import UpdateResult

# # Project # #
from vigobusapi.services.mongo import MongoDB
from vigobusapi.entities import BaseMongoModel
from vigobusapi.utils import get_datetime, new_hash_values, ChecksumableClass, without
from vigobusapi.logger import logger
from ._entities import *

__all__ = ("get_cached_metadata", "save_cached_metadata", "update_cached_metadata",
           "MapRequestModels", "MapVendors", "MapTypes", "CachedMap")

MapRequestModels = Union[GoogleMapRequest, GoogleStreetviewRequest]


class MapVendors(str, enum.Enum):
    # Currently only using Google Maps API, but this field provides future-proof when more vendors are featured
    google_maps = "google"


class MapTypes(str, enum.Enum):
    map = "map"
    photo = "streetview"


MAP_REQUESTS_TYPES = {
    GoogleMapRequest: MapTypes.map,
    GoogleStreetviewRequest: MapTypes.photo
}


class CachedMap(BaseMongoModel, ChecksumableClass):
    """Representation of the Mongo document used for caching different types of map pictures."""

    id: str = ""
    """Document id, generated as: "{vendor}:{key}."""
    key: str
    """Checksum generated from the "data" object, used as cache key.
    Not used as document _id because multiple cached images (from different vendors) would have the same checksum."""
    vendor: MapVendors
    """Remote source API/vendor the map was fetched from."""
    type: MapTypes
    """Type of map picture."""
    data: MapRequestModels
    """Original Request object used for fetching the object."""
    saved: datetime.datetime
    """When this document was saved. Used for TTL purposes."""
    image: Optional[bytes]
    """Image saved as-is. Optional because metadata can be fetched without the image, but should always be persisted."""
    telegram_file_id: Optional[str]
    """File ID in Telegram, set after sending the picture via Telegram."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = self.checksum_value

    def metadata_dict(self, **kwargs) -> dict:
        """Fetch the dict(), without the "image" field."""
        excludes = kwargs.pop("exclude", set())
        excludes.add("image")
        kwargs["exclude"] = excludes
        return self.dict(**kwargs)

    def metadata_json(self, **kwargs) -> str:
        """Fetch the json(), without the "image" field."""
        excludes = kwargs.pop("exclude", set())
        excludes.add("image")
        kwargs["exclude"] = excludes
        return self.json(**kwargs)

    @property
    def checksum_hash(self):
        return new_hash_values(
            self.key,
            self.vendor.value,
            self.type.value,
            algorithm="sha256"
        )

    class Config(BaseMongoModel.Config):
        id_field = "id"


def _get_mongo_filter_from_request(request: MapRequestModels):
    return dict(
        key=request.checksum_value,
        type=MAP_REQUESTS_TYPES[type(request)]
    )


async def get_cached_metadata(request: MapRequestModels, fetch_image: bool) -> Optional[CachedMap]:
    request_checksum = request.checksum_value
    with logger.contextualize(map_request_checksum=request_checksum):
        logger.bind(fetch_image=fetch_image).debug("Searching map cached metadata...")

        query_filter = _get_mongo_filter_from_request(request)
        query_fields = dict(_id=False)
        if not fetch_image:
            query_fields["image"] = False

        # NOTE Currently only the first found document is used.
        # If more API sources are included in the future, should support choosing vendor or having priorities.
        document = await MongoDB.get_mongo().get_cache_maps_collection().find_one(
            filter=query_filter,
            projection=query_fields
        )

        if not document:
            logger.debug("Map metadata not found in Mongo cache")
            return None

        parsed_metadata = CachedMap(**document)
        logger.bind(cached_metadata_document=without(document, "image"))\
            .debug("Read map cached metadata document from Mongo")
        return parsed_metadata


async def update_cached_metadata(cache_id: str, telegram_file_id: str) -> bool:
    """Update certain fields from a cached map metadata document. Currently only supports updating the Telegram File ID.
    The identifier used is the document id. Returns True/False depending on if the document was found."""
    with logger.contextualize(cache_id=cache_id):
        query_filter = dict(_id=cache_id)
        query_update = {
            "$set": {
                "telegram_file_id": telegram_file_id
            }
        }

        logger.bind(cache_document_update=query_update).debug("Updating map cached metadata...")
        r: dict = await MongoDB.get_mongo().get_cache_maps_collection().find_one_and_update(
            filter=query_filter,
            update=query_update
        )

        if r is None:
            logger.debug("No map cache document found for update")
            return False

        logger.debug("Updated map cache document")
        return True


async def save_cached_metadata(request: MapRequestModels, image: bytes, background: bool) -> CachedMap:
    """Save the given request object and image in cache.
    Return the CachedMap object. If background=True, return instantly and persist in background."""
    metadata = CachedMap(
        key=request.checksum_value,
        vendor=MapVendors.google_maps.value,
        type=MAP_REQUESTS_TYPES[type(request)],
        data=request,
        saved=get_datetime(),
        image=image
    )

    with logger.contextualize(map_cache_id=metadata.id):
        async def __save():
            logger.debug("Saving map cache in MongoDB...")
            r: UpdateResult = await MongoDB.get_mongo().get_cache_maps_collection().replace_one(
                filter=dict(_id=metadata.id),
                replacement=metadata.to_mongo(),
                upsert=True
            )

            if r.upserted_id:
                logger.debug("Inserted new map cache document")
            elif r.modified_count:
                logger.debug("Replaced existing map cache document")
            else:
                logger.error("No modified/inserted documents inserted in MongoDB")

        if background:
            logger.debug("Map cache will be saved as background task")
            asyncio.create_task(__save())
        else:
            await __save()

        return metadata
