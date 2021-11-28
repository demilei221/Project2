import pandas as pd
import requests, json
from geopy.distance import geodesic
from operator import itemgetter

#Michael presenting this

df_demographic = pd.read_csv('acs2017_county_data.csv')
df_demZip = pd.read_csv('ACSDP5Y2019.DP05_data_with_overlays_2021-11-04T120142.csv')
df_incomeZip = pd.read_csv('ACSST5Y2019.S1901_data_with_overlays_2021-11-05T101234.csv')
df_incomeCounty = pd.read_csv('ACSST1Y2019.S1901_data_with_overlays_2021-11-04T144153.csv')
# california_income = df_incomeZip[df_incomeZip.State_Name == "California"]
api_key_walkscore = 'b268b8ca8e79828b9d3d43eb99375200'
api_key = 'AIzaSyABaPaAeZXhRLax3OJ9TvYhtK-QGCDuikM'

def zipToZcta(zipCode):
    df = pd.read_excel("ZiptoZcta_Crosswalk_2021.xlsx")
    data = (df[df["ZIP_CODE"] == int(zipCode)].ZCTA).values[0]
    return data

# return: TotalPop,	Men	,Women,	Hispanic,	White	,Black,	Native,	Asian,	Pacific
def demographic(zipCode):
    ZCTA = zipToZcta(zipCode)
    race_dict = {}
    data = df_demZip[df_demZip.NAME == f'ZCTA5 {ZCTA}']
    race_dict['asian'] = (data.DP05_0044PE).values[0]
    race_dict['white'] = (data.DP05_0037PE).values[0]
    race_dict['black'] = (data.DP05_0038PE).values[0]
    race_dict['native'] = (data.DP05_0039PE).values[0]
    race_dict['hispanic'] = (data.DP05_0071PE).values[0]
    race_dict['pacific'] = (data.DP05_0052PE).values[0]
    return race_dict


print(demographic("92614"))



def income_zip_code(Zip):
    ZCTA = zipToZcta(Zip)
    # race_dict = {}
    data = df_incomeZip[df_incomeZip.NAME == f'ZCTA5 {ZCTA}']
    return str((data.S1901_C01_012E).values[0])


def income_county(county):
    data = df_incomeCounty[df_incomeCounty.NAME.apply(lambda x : f'{county}' in x)]
    return str((data.S1901_C01_012E).values[0])


def poverty_county(county):
    poverty_county = df_demographic[df_demographic.County == county]
    return str(poverty_county.Poverty.values[0])

#using google api, search for the given place
def place_search(query):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    r = requests.get(url + 'query=' + query + '&key=' + api_key)
    x = r.json()
    y = x['results']

    temp = []
    for i in range(len(y)):
        place = y[i]['geometry']['location']
        place['name'] = y[i]['name']
        place['address'] = y[i]['formatted_address']
        temp.append(place)
    return temp

def get_distance(coord1, coord2):
    return str(geodesic(coord1, coord2).miles)

#search for place near the given place
def nearby_place_search(source_place, place_type, distance='4828', keyword=''):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    r = requests.get(url + 'location=' + str(source_place[0]['lat']) + ',' +
                     str(source_place[0]['lng']) + '&radius=' + distance + '&type=' +
                     place_type + '&keyword=' + keyword + '&key=' + api_key)
    x = r.json()
    y = x['results']

    ans = [] #list of dictionaries
    for place in y:
        coord1 = (source_place[0]['lat'], source_place[0]['lng'])
        coord2 = (place['geometry']['location']['lat'], place['geometry']['location']['lng'])
        temp = {} #temp is the current dictionary
        temp['name'] = place['name']
        temp['address'] = place['vicinity']
        temp['distance'] = str(get_distance(coord1, coord2))
        temp['lat'] = place['geometry']['location']['lat']
        temp['lng'] = place['geometry']['location']['lng']
        ans.append(temp) #appending temp to the list
    ans = sorted(ans, key=itemgetter('distance'))
    return ans

def getScore(places, address): #from walk score api, walk, bike, and transit

    r = requests.get(url="https://api.walkscore.com/score?format=json&address="+address+
                         "&lat="+str(places[0]['lat'])+"&lon="+str(places[0]['lng'])+
                         "&transit=1&bike=1&wsapikey="+api_key_walkscore,)
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
    result['demographic'] = demographic(zip_code)
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

#drop down list
def getCounties(state):
    demographic = df_demographic[df_demographic.State == state]
    return list(demographic['County'].values)

def getStates():
    states = sorted(set(df_demographic['State']))
    states = list(states)
    return states


