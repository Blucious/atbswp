# coding:utf8

"""quickWeather.py - Prints the weather for a location from the command line.
Usage:quickWeather.py <location>"""

import sys
import json
import requests

# Fill in APPID, an APPID is requried for API call.
APPID = ''
# -------------------------------------------------

# Compute location from command line arguments.
if len(sys.argv) < 2:
    print(__doc__)
    sys.exit()
location = ' '.join(sys.argv[1:])

# Download the JSON data from OpenWearherMap.org's API.
url = ('http://api.openweathermap.org/data/2.5/forecast/'
       'daily?q={city_name_and_country_code}&cnt={cnt}&appid={appid}').format(
    city_name_and_country_code=location, cnt=3, appid=APPID)
response = requests.get(url)
response.raise_for_status()

# Load JSON data into a Python variable.
weatherData = json.loads(response.text)

# Print weather description
w = weatherData['list']
for i, prompt in zip(range(3), ['Current weather in %s:' % location,
                                'Tomorrow:',
                                'Day after tomorrow:']):
    print(prompt)
    print(w[i]['weather'][0]['main'], '-', w[i]['weather'][0]['description'])
    print()
