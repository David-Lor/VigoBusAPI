"""MONGO
MongoDB client class
"""

# # Installed # #
from motor import motor_asyncio
from pymongo import TEXT

# # Project # #
from vigobusapi.settings import settings
from vigobusapi.logger import logger


class MongoDB:
    """Class containing the async MongoDB "Motor" client, and methods to acquire the database and collections used.
    The class and Motor client are initialized and accessed in a Singleton way.

    First, the current class, the Motor client and other procedures for db/collection setup are initialized using the
    initialize() classmethod, which must be called when the API server starts.

    Then, whenever the MongoDB must be accessed, the get_mongo() method can be used to fetch the MongoDB class instance
    previously initialized, which lives as a class method.

    Database settings are acquired from the "settings" module and initialized class there.
    """
    _mongodb_instance = None  # Singleton instance of the class
    _client = motor_asyncio.AsyncIOMotorClient

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """MongoDB async "Motor" client."""
        if self._client is None:
            raise Exception("Mongo client not initialized")
        return self._client

    def get_database(self):
        return self.client[settings.mongo_stops_db]

    def get_stops_collection(self):
        return self.get_database()[settings.mongo_stops_collection]

    @classmethod
    async def initialize(cls):
        """Singleton initialization of MongoDB. Must run before the API server starts. Performs the following:
        - Create a new MongoDB() instance and assign it to class (can be acquired through get_mongo() class method).
        - Create and assign the AsyncIOMotorClient.
        - Perform initial actions required for setup of collection.
        """
        if cls._mongodb_instance is not None:
            return

        logger.info("Initializing MongoDB...")
        mongo = MongoDB()
        cls._mongodb_instance = mongo
        mongo._client = motor_asyncio.AsyncIOMotorClient(settings.mongo_uri)

        # Create a Text Index on stop name, for search
        # https://docs.mongodb.com/manual/core/index-text/#create-text-index
        await mongo.get_stops_collection().create_index(
            [("name", TEXT)],
            background=True,
            default_language="spanish"
        )

        logger.info("MongoDB initialized!")

    @classmethod
    def get_mongo(cls) -> "MongoDB":
        """Singleton acquisition of MongoDB.
        The class should be previously initialized by calling the initialize() class method."""
        if cls._mongodb_instance is None:
            raise Exception("Mongo class not initialized")
        return cls._mongodb_instance
