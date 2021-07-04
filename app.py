import json
import requests

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/affectedCountries")
async def affectedCountries():
    """
    Get a list of countries affected by natural disasters and find countries which need the most help
    """
    countries = {}

    API_URL = "https://api.reliefweb.int/v1/disasters?appname=mag-disaster-api&profile=list&preset=latest&slim=1"
    disaster_data = requests.get(API_URL).content
    disaster_data = json.loads(disaster_data)

    for disaster in disaster_data['data']:
        for country in disaster['fields']['country']:
            country = country['name']
            if(country in countries):
                countries[country] += 1
            else:
                countries[country] = 1

    return countries
