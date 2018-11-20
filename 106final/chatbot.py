import aiml
import os
import requests
import json
import time

# kernel is responsible for responding to suers
kernel = aiml.Kernel()

GOOGLE = 'AIzaSyAnZB058_QPL-KECBFUBbV1J9zdQPc-Yp4'
dark = '113a35b4747ff89bbffbf9980a8e2464'

# load every aiml file in the 'standard' directory
dirname = 'aiml_data'
filenames = [os.path.join(dirname, f) for f in os.listdir(dirname)]
aiml_filenames = [f for f in filenames if os.path.splitext(f)[1]=='.aiml']

kernel = aiml.Kernel()
for filename in aiml_filenames:
    kernel.learn(filename)

# add a new response for when the user says "example * and *"
# note that the ARGUMENT NAMES (first and second) must match up with
# the names in kernel.addPattern
def exampleResponse(first, second):
    return 'first arg is {}, second arg is {}'.format(first, second)
kernel.addPattern("example {first} and {second}", exampleResponse)

# my code starts here:
cache_name = 'cache.json'
try:
    cache_file = open(cache_name, 'r')
    cache_diction = json.loads(cache_file.read())
    cache_file.close()
except:
    cache_diction = {}

def getLatLng(city):
    try:
        req = requests.Request(method = "GET", url = 'https://maps.googleapis.com/maps/api/geocode/json', params = {'key': GOOGLE, 'address': city})
        prepped = req.prepare() #finds the URL value
        fullURL = prepped.url
        if fullURL not in cache_diction: #if it is not in our cache dictionary, add it. If it is, you can return the cache dictionary because it's already in it
            #response = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params = {'key': 'AIzaSyAnZB058_QPL-KECBFUBbV1J9zdQPc-Yp4', 'address': city})
            result = requests.Session().send(prepped)
            d = json.loads(result.text)
            cache_diction[fullURL] = d

            cache_file = open(cache_name, 'w')
            cache_file.write(json.dumps(cache_diction))
            cache_file.close()

        lat = cache_diction[fullURL]['results'][0]['geometry']['location']['lat']
        lng = cache_diction[fullURL]['results'][0]['geometry']['location']['lng']
        return lat,lng
    except:
        return "Is {} a city?".format(city)

def weatherinfo(city):
    try:
        lat,lng = getLatLng(city)
        key = "{},{}".format(lat,lng)
        timenow = int(time.time())
        if key in cache_diction and cache_diction[key]["currently"]["time"] + 300 >= timenow:
            return cache_diction[key]
        else:
            data = requests.get('https://api.darksky.net/forecast/{}/{},{}'.format(dark,lat,lng)).json()
            cache_diction[key] = data
            file = open('cache.json', 'w')
            file.write(json.dumps(cache_diction))
            file.close()
            return data
    except:
        "Sorry, I don't know"
print(weatherinfo("Ann Arbor"))

#What's the weather like in (city)?
def cityweather(city):
    try:
        data= weatherinfo(city)
        temp= data["currently"]["temperature"]
        summ = data["currently"]["summary"]
        return "In {}, it is {} and {}".format(city, temp, summ)
    except:
        return "Is {} a city?".format(city)
kernel.addPattern("What's the weather like in {city}?", cityweather)
#print(cityweather("Ann Arbor"))

#How hot will it get in (city) today?
def hightemp(city):
    try:
        d = weatherinfo(city)
        temp = d["daily"]["data"][0]["temperatureMax"]
        # temp = []
        # for x in d["hourly"]["data"]:
        #     temp = temp + [x["temperature"]]
        # daytemp = temp[0:24]
        # highest = daytemp[0]
        # for t in daytemp:
        #     if t > highest:
        #         highest = t
        return "In {} it will reach {}".format(city, temp)
    except:
        return "Is {} a city?".format(city)
kernel.addPattern("How hot will it get in {city} today?", hightemp)
#print(hightemp("Ann Arbor"))

#How cold will it get in (city) today?
def lowtemp(city):
    try:
        d = weatherinfo(city)
        temp = d["daily"]["data"][0]["temperatureMin"]
        # temp = []
        # for x in d["hourly"]["data"]:
        #     temp = temp + [x["temperature"]]
        # daytemp = temp[0:24]
        # lowest = daytemp[0]
        # for t in daytemp:
        #     if t < lowest:
        #         lowest = t
        return "In {} it will reach {}".format(city, temp)
    except:
        return "Is {} a city?".format(city)
kernel.addPattern("How cold will it get in {city} today?", lowtemp)
#print(lowtemp("Ann Arbor"))

#how hot will it get in (city) this week?
def weekhigh(city):
    try:
        d = weatherinfo(city)
        temp = []
        for x in d["daily"]["data"]:
            temp = temp + [x["temperatureMax"]]
        weektemp = temp[0:7]
        highest = weektemp[0]
        for t in weektemp:
            if t > highest:
                highest = t
        return "In {} it will reach {}".format(city, highest)
    except:
        return "Is {} a city?".format(city)
kernel.addPattern("How hot will it get in {city} this week?", weekhigh)
#print(weekhigh("Ann Arbor"))

#How cold will it get in (city) this week?
def weeklow(city):
    try:
        d = weatherinfo(city)
        temp = []
        for x in d["daily"]["data"]:
            temp = temp + [x["temperatureMin"]]
        weektemp = temp[0:7]
        lowest = weektemp[0]
        for t in weektemp:
            if t < lowest:
                lowest = t
        return "In {} it will reach {}".format(city, lowest)
    except:
        return "Is {} a city?".format(city)
kernel.addPattern("How cold will it get in {city} this week?", weeklow)
#print(weeklow("New York City"))

def raintoday(city):
    try:
        d = weatherinfo(city)
        rainprob = d["daily"]["data"][0]["precipProbability"]
        if rainprob < 0.1:
            return "It almost definitely will not rain in {}".format(city)
        if rainprob  >= 0.1 and  rainprob < 0.5:
            return "It probably will not rain in {}".format(city)
        if rainprob >= 0.5 and rainprob < 0.9:
            return "It probably will rain in {}".format(city)
        if rainprob >= 0.9:
            return "It will almost definitely rain in {}".format(city)
    except:
        return "Is {} a city?".format(city)
kernel.addPattern("Is it going to rain in {city} today?", raintoday)
#print(raintoday("Ann Arbor"))

def rainweek(city):
    try:
        d = weatherinfo(city)
        no_rain = []
        for x in d["daily"]["data"]:
            no_rain = no_rain + [1 - x["precipProbability"]]
        new = no_rain[0:7]
        number = 1
        for x in new:
            number = number * x
        rainprob = 1 - number
        if rainprob < 0.1:
            return "It almost definitely will not rain in {}".format(city)
        if rainprob  >= 0.1 and  rainprob < 0.5:
            return "It probably will not rain in {}".format(city)
        if rainprob >= 0.5 and rainprob < 0.9:
            return "It probably will rain in {}".format(city)
        if rainprob >= 0.9:
            return "It will almost definitely rain in {}".format(city)
    except:
        return "Is {} a city?".format(city)
kernel.addPattern("Is it going to rain in {city} this week?", rainweek)
#print(rainweek("Ann Arbor"))

input_ = ''
while input_ != "exit":
    input_ = input("Type Here: ")
    print(kernel.respond(input_))
