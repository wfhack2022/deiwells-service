# importing the requests library
import os
import requests


# location given here
location = "delhi technological university"

# defining a params dict for the parameters to be sent to the API
PARAMS = {'address':location}

# sending get request and saving the response as response object
#r = requests.get(url = URL, params = PARAMS)
token=os.environ['TOKEN']
# reuters api-endpoint
reuters_endpoint="https://api-eit.refinitiv.com/permid/search?q=name:sunrun inc&num=1&access-token={TOKEN}&entitytype=organization&format=JSON"
URL = reuters_endpoint.format(TOKEN = token)
r = requests.get(url = URL)
data = r.json()
companyUrl=data['result']['organizations']['entities'][0]['hasURL']
ric=data['result']['quotes']['entities'][0]['hasRIC']
ticker=data['result']['quotes']['entities'][0]['hasExchangeTicker']

print(companyUrl)
print(ric)
print(ticker)


# extracting latitude, longitude and formatted address
# of the first matching location
# latitude = data['results'][0]['geometry']['location']['lat']
# longitude = data['results'][0]['geometry']['location']['lng']
# formatted_address = data['results'][0]['formatted_address']

# # printing the output
# print("Latitude:%s\nLongitude:%s\nFormatted Address:%s"
# 	%(latitude, longitude,formatted_address))
