import logging
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import os

from db import Location, ChromaDB

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)
database = ChromaDB(host=os.environ.get("CHROMA_HOST", "localhost"), port=int(os.environ.get("CHROMA_PORT", 7689)))
app = FastAPI()


class CLIPResponse(BaseModel):
    similarity: List[List[float]]


@app.post("/add_location", tags=["Locations"])
def add_location(location: Location) -> dict[str, Location | str]:
    try:
        database.upsert_location(location)
    except Exception as e:
        return {
            "status": "error",
            "error": e
        }
    return {
        "status": "ok",
        "location": location
    }


@app.get("/recommendations", tags=["Locations"])
def get_locations(selected_locations: List[Location]) -> dict[str, Location | str]:
    embeddings = []
    selected_location_ids = []
    for location in selected_locations:
        embeddings.append([
            location.category_id,
            location.latitude,
            location.longitude,
        ])
        selected_location_ids.append(location.location_id)

    return database.get_locations(embeddings, selected_location_ids)


@app.get("/ping", tags=["TEST"])
def ping():
    return "pong"
