import json
import requests
import pandas as pd


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

df = pd.read_csv("GNI_data.csv")

income_levels = {
    "High income": 1,
    "Upper middle income": 2,
    "Lower middle income": 4,
    "Low income": 4

}

disaster_status = {"current": 2, "past": 1}


@app.get("/affectedCountries")
async def affectedCountries():
    """
    Get a list of countries affected by natural disasters and find countries which need the most help
    """
    countries = {}

    API_URL = "https://api.reliefweb.int/v1/disasters?appname=mag-disaster-api&profile=list&preset=latest&slim=1"
    disaster_data = requests.get(API_URL).content
    disaster_data = json.loads(disaster_data)

    for disaster in disaster_data['data'][::-1]:
        if(disaster['fields']['status'] != "alert"):
            for country in disaster['fields']['country']:
                country = country['name']
                if(country in countries):
                    information = countries[country] 
                    information['number_of_disasters'] += 1
                    information['status'] = disaster['fields']['status']
                else:
                    information = countries[country] = {}
                    information['number_of_disasters'] = 1
                    information['income_category'] = income_category(country)
                    information['status'] = disaster['fields']['status']
                countries[country]['severity_score'] = calculate_score(countries[country])

    return countries


@app.get("/fundAllocations")
async def allocations():
    """
    Get a list of countries affected by natural disasters and find countries which need the most help
    """

    return rank_countries(await affectedCountries())


def calculate_score(country_data):
    info = country_data
    score = 0.4 * info['number_of_disasters'] + 0.4 * income_levels[info['income_category']] + 0.2 * disaster_status[info['status']]
    return score


def rank_countries(countries):
    """Rank countries affected by disasters based on a weighted sum of all criteria"""
    total_score = 0
    ranked_allocation = {"countries": []}
    for country, info in countries.items():
        total_score += info['severity_score']

    for country, info in countries.items():
        weightage = info['severity_score'] / total_score
        ranked_allocation['countries'].append({"name": country, "weightage": weightage})

    return ranked_allocation


def income_category(country):
    """Finds the income category thr country belongs to based on GNI per capita from World Bank Data"""
    data = query_df(country)
    return data


def query_df(country):
    """Function to query a dataframe with the given pararmeters"""
    try:
        return df.query("TableName == @country")['IncomeGroup'].values[0]
    except:
        return "Low income"
