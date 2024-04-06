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
database = ChromaDB(host=os.environ.get("CHROMA_HOST", "localhost"), port=int(os.environ.get("CHROMA_PORT", 8000)))
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


@app.post("/recommendations", tags=["Locations"])
def get_locations(selected_locations: List[Location], n_results: int = 10) -> list[int]:
    embeddings = []
    selected_location_ids = []
    for location in selected_locations:
        embeddings.append([
            location.category_id,
            location.latitude,
            location.longitude,
        ])
        selected_location_ids.append(location.location_id)

    locations = database.get_locations(embeddings, selected_location_ids)
    print(locations)
    ids = locations.get("ids", [])
    dists = locations.get("distances", [])
    counts = dict()
    distances = dict()
    for i, arr in enumerate(ids):
        for j, item in enumerate(arr):
            counts[item] = counts.get(item, 0) + 1
            distances[item] = max(distances.get(item, -2000000), dists[i][j])
    items = [(counts.get(key, 0), -dist, key) for key, dist in distances.items()]
    sorted_items = sorted(items, reverse=True)
    print(sorted_items)
    return [int(x[-1]) for x in sorted_items[:n_results]]


@app.get("/ping", tags=["TEST"])
def ping():
    return "pong"
