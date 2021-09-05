import pandas as pd
import os

# importing required modules
import requests, json
from geopy.distance import geodesic
from operator import itemgetter
from walkscore import WalkScoreAPI

df_demographic = pd.read_csv('acs2017_county_data.csv')

df_income = pd.read_csv('kaggle_income.csv',encoding = "ISO-8859-1")
california_income = df_income[df_income.State_Name == "California"]


# return: TotalPop,	Men	,Women,	Hispanic,	White	,Black,	Native,	Asian,	Pacific
def demographic_county(County, State):
  demographic = df_demographic[df_demographic.State == State]
  demographic = demographic[demographic.County == County]

  demo_dict = {}
  demo_dict['total_pop'] = demographic.TotalPop.values[0]
  demo_dict['men'] =  demographic.Men.values[0]
  demo_dict['women'] = demographic.Women.values[0]
  demo_dict['hispanic'] = 	demographic.Hispanic.values[0]
  demo_dict['white']=	demographic.White.values[0]
  demo_dict['black']=	demographic.Black.values[0]
  demo_dict['native'] = 	demographic.Native.values[0]
  demo_dict['asian']	= demographic.Asian.values[0]
  demo_dict['pacific'] =	demographic.Pacific.values[0]

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


# Python program to get a set of
# places according to your search
# query using Google Places API


api_key = 'AIzaSyABaPaAeZXhRLax3OJ9TvYhtK-QGCDuikM'


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
    # Print value corresponding to the
    # 'name' key at the ith index of y
    place = y[i]['geometry']['location']
    place['name'] = y[i]['name']
    place['address'] = y[i]['formatted_address']
    ans.append(place)
  return str(ans)


def get_distance(coord1, coord2):
  return str(geodesic(coord1, coord2).miles)


# coord1 = (34.0991491, -118.1099605)
# coord2 = (34.0949198, -118.1270041)

# print(get_distance(coord1, coord2))

def nearby_place_search(source_place, place_type, distance='4828', keyword=''):
  # print(place_type)
  # source_place = place_search(place)
  # print(source_place)
  # url variable store url
  url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"

  # get method of requests module
  # return response object
  # r = requests.get(url + 'location=' + str(ans[0][2]['lat']) +str(ans[0][2]['lng'])+'&radius=3200'+ place_type+'&key=' + api_key)
  r = requests.get(url + 'location=' + str(source_place[0]['lat']) + ',' + str(
    source_place[0]['lng']) + '&radius=' + distance + '&type=' + place_type + '&keyword=' + keyword + '&key=' + api_key)

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
  for place in y:
    # Print value corresponding to the
    # 'name' key at the ith index of y
    coord1 = (source_place[0]['lat'], source_place[0]['lng'])
    coord2 = (place['geometry']['location']['lat'], place['geometry']['location']['lng'])
    temp = {}
    temp['name'] = place['name']
    temp['address'] = place['vicinity']
    temp['distance'] = get_distance(coord1, coord2)

    ans.append(temp)

  ans = sorted(ans, key=itemgetter('distance'))

  return str(ans)

# nearby = nearby_place_search('6 W Main St,  91801','parking')
# print(nearby, len(nearby))

# nearby = nearby_place_search('6 W Main St,  91801','restaurant', keyword='seafood,chinese')
# print(nearby, len(nearby))



#source: https://pypi.org/project/walkscore-api/

api_key_walkscore = 'b268b8ca8e79828b9d3d43eb99375200'
walkscore_api = WalkScoreAPI(api_key = api_key_walkscore)

def getScore(places, address):
  # address = '419 W Adams Ave, alhambra'

  result = walkscore_api.get_score(latitude = places[0]['lat'], longitude = places[0]['lng'], address = address)

  # the WalkScore for the location
  return str(result.walk_score)

  # the TransitScore for the location
  # print(result.transit_score)

  # the BikeScore for the location
  # print(result.bike_score)



def get_bus_stop(places):
  return str(nearby_place_search(places,'bus', keyword='stop'))

def get_info(address, county, state, zip_code, business_type):
  places = place_search(str(address) + ", " +  str(zip_code))
  print( getScore(places, address))

  return {'demographic' : demographic_county(county, state),
          'income_zip_code': income_zip_code(zip_code),
          'income_county' : income_county(county),
          'poverty_county': poverty_county(county),
          'near_by_place' : nearby_place_search(places, business_type),
          'walk_score' : getScore(places, address)
          }

# address = '419 W Adams Ave, alhambra'
# places = main.place_search(address)
# print('places: ', places)
# nearby = main.nearby_place_search(places,'restaurant', keyword='seafood,chinese')
# print('nearby places:' , nearby)
# print('score: ', main.getScore(places, address))


