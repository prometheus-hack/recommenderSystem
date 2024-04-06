import chromadb
from pydantic import BaseModel


class Location(BaseModel):
    location_id: int
    category_id: int
    latitude: float
    longitude: float


class ChromaDB:
    def __init__(self, *args, **kwargs):
        self.client = chromadb.HttpClient(*args, **kwargs)
        self.loc_collection = self.client.get_or_create_collection(
            name="locations",
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_location(self, location: Location):
        self.loc_collection.upsert(
            ids=[str(location.location_id)],
            metadatas=[dict(location)],
            embeddings=[location.category_id, location.latitude, location.longitude]
        )

    def get_locations(self, embeddings, exclude_ids=None, n_results=10):
        query = None
        if exclude_ids:
            query = {
                "location_id": {
                    "$nin": exclude_ids
                }
            }
        return self.loc_collection.query(
            query_embeddings=embeddings,
            where=query,
            n_results=n_results,
            include=["distances", "metadatas"]
        )
