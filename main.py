import pandas as pd
import os
import requests, json
from geopy.distance import geodesic
from operator import itemgetter

df_demographic = pd.read_csv('acs2017_county_data.csv')
df_income = pd.read_csv('kaggle_income.csv',encoding = "ISO-8859-1")
california_income = df_income[df_income.State_Name == "California"]
api_key_walkscore = 'b268b8ca8e79828b9d3d43eb99375200'
api_key = 'AIzaSyABaPaAeZXhRLax3OJ9TvYhtK-QGCDuikM'

# return: TotalPop,	Men	,Women,	Hispanic,	White	,Black,	Native,	Asian,	Pacific
def demographic_county(County, State):
    demographic = df_demographic[df_demographic.State == State]
    demographic = demographic[demographic.County == County]
    print(demographic)

    demo_dict = {}
    demo_dict['total_pop'] = str(demographic.TotalPop.values[0])
    demo_dict['men'] =  str(demographic.Men.values[0])
    demo_dict['women'] = str(demographic.Women.values[0])
    demo_dict['hispanic'] = str(demographic.Hispanic.values[0])
    demo_dict['white'] = str(demographic.White.values[0])
    demo_dict['black'] = str(demographic.Black.values[0])
    demo_dict['native'] = str(demographic.Native.values[0])
    demo_dict['asian'] = str(demographic.Asian.values[0])
    demo_dict['pacific'] = str(demographic.Pacific.values[0])

    return demo_dict


def income_zip_code(Zip):
    income_zip = df_income[df_income.Zip_Code == Zip]

    return str(income_zip.Median.median())


def income_county(county):
    income_county = df_income[df_income.County == county]
    return str(income_county.Median.median())


def poverty_county(county):
    poverty_county = df_demographic[df_demographic.County == county]
    return str(poverty_county.Poverty.values[0])

def place_search(query):
    # url variable store url
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

    # get method of requests module
    # return response object
    r = requests.get(url + 'query=' + query +
                   '&key=' + api_key)

    # json method of response object convert
    # json format data into python format data
    x = r.json()

    # now x contains list of nested dictionaries
    # we know dictionary contain key value pair
    # store the value of result key in variable y
    y = x['results']
    # print(y)
    ans = []
    # keep looping upto length of y
    for i in range(len(y)):
        place = y[i]['geometry']['location']
        place['name'] = y[i]['name']
        place['address'] = y[i]['formatted_address']
        ans.append(place)
    return ans

def get_distance(coord1, coord2):
    return str(geodesic(coord1, coord2).miles)

def nearby_place_search(source_place, place_type, distance='4828', keyword=''):
    # url variable store url
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"

    # get method of requests module
    # return response object
    r = requests.get(url + 'location=' + str(source_place[0]['lat']) + ',' + str(source_place[0]['lng']) + '&radius=' + distance + '&type=' + place_type + '&keyword=' + keyword + '&key=' + api_key)

    # json method of response object convert to json format data into python format data
    x = r.json()
    # now x contains list of nested dictionaries
    # we know dictionary contain key value pair
    # store the value of result key in variable y
    y = x['results']

    ans = []
    # keep looping upto length of y
    for place in y:
        coord1 = (source_place[0]['lat'], source_place[0]['lng'])
        coord2 = (place['geometry']['location']['lat'], place['geometry']['location']['lng'])
        temp = {}
        temp['name'] = place['name']
        temp['address'] = place['vicinity']
        temp['distance'] = str(get_distance(coord1, coord2))
        temp['lat'] = place['geometry']['location']['lat']
        temp['lng'] = place['geometry']['location']['lng']
        ans.append(temp)

    ans = sorted(ans, key=itemgetter('distance'))

    return ans

def getScore(places, address):

    r = requests.get(url="https://api.walkscore.com/score?format=json&address="+address+"&lat="+str(places[0]['lat'])+"&lon="+str(places[0]['lng'])+"&transit=1&bike=1&wsapikey="+api_key_walkscore,)
    # extracting data in json format
    data = r.json()
    keys_to_extract = ['walkscore', 'description']
    result = {key: data[key] for key in keys_to_extract}
    if 'bike' in data:
        result['bikescore'] = data['bike']['score']
        result['bikeDescription'] = data['bike']['description']
    else:
        result['bikescore'] = 'None'
        result['bikeDescription'] = 'None'
    if 'transit' in data:
        result['transitscore'] = data['transit']['score']
        result['transitDescription'] = data['transit']['score']
        result['transitSummary'] = data['transit']['summary']
    else:
        result['transitscore'] = 'None'
        result['transitDescription'] = 'None'
        result['transitSummary'] = 'None'

    return result

def get_bus_stop(places):
    return str(nearby_place_search(places,'bus', keyword='stop'))

def get_info(address, county, state, zip_code, business_type):
    places = place_search(address + ", " +  zip_code)
    result = {}
    result['demographic'] = demographic_county(county, state)
    result['income_zip_code'] = income_zip_code(int(zip_code))
    result['income_county'] = income_county(county)
    result['poverty_county'] = poverty_county(county)
    result['near_by_place'] = nearby_place_search(places, business_type)
    result['parkings'] = nearby_place_search(places, "parking")
    result['latitude'] = places[0]['lat']
    result['longitude'] = places[0]['lng']
    result.update(getScore(places, address))
    print(result)
    return result

def getCounties(state):
    demographic = df_demographic[df_demographic.State == state]
    return list(demographic['County'].values)

def getStates():
    states = sorted(set(df_demographic['State']))
    states = list(states)
    return states