import requests
import json
import PySimpleGUI as sg 
from datetime import date
from datetime import datetime
write = open("history.txt", 'a+')

today = date.today()
now = datetime.now()


api_key = ''
desc = ""
temperature = ""
wind = ""
temp_max = ""
temp_min = ""
location = ""
isCelsius = True
isRateLimited = False
history = """
"""
read = open('history.txt', 'r')
for each in read:
    splitted = each.split('|')
    history += "Location: {} Date: {}\n".format(splitted[0] ,splitted[6])
    history += "Description: {}\n".format(splitted[1])
    history += 'Temperature: {}\n'.format(splitted[2])
    history += 'Wind: {}\n'.format(splitted[3])
    history += 'Max Temperature: {}\n'.format(splitted[4])
    history += 'Min Temperature: {}\n\n'.format(splitted[5])
read.close()

place1_temp = ""
place2_temp = ""



sg.theme('Dark Grey 6')

def convert_celsius(temperature):
    fahrenheit = temperature * 1.8 + 32
    return fahrenheit
def convert_fahrenheit(temperature):
    celsius = temperature-32
    celsius = celsius / 1.8
    return celsius

def get_location(place, state_code):
    state_code.upper()
    place = place.replace(" ", "+")
    req = requests.get('https://api.opencagedata.com/geocode/v1/json?key=f5d91c278d2f4128af880b8bd008aa82&q={}&pretty=1'.format(place)).content
    reqjson = json.loads(req)
    total_results = reqjson['total_results']
    try:
        for x in range(0,total_results):
            if reqjson['results'][x]['components']['state_code'] == state_code:
                lat = reqjson['results'][x]['geometry']['lat']
                long = reqjson['results'][x]['geometry']['lng']
    except IndexError:
        pass
    return lat, long

def get_weather(lat, long):
    global desc, wind, temperature, temp_min, temp_max, isRateLimited, location
    link = 'https://fcc-weather-api.glitch.me/api/current?lat={}&lon={}'.format(lat, long)
    req = requests.get(link).content
    reqjson = json.loads(req)
    if reqjson["sys"]["country"] == "JP":
        isRateLimited = True
    try:
        description = reqjson['weather'][0]['description']
        desc += description
    except KeyError:
        desc += "Couldn't Fetch Description"
        pass
    try:
        temp = reqjson['main']['temp']
        temperature += str(temp)
    except KeyError:
        temperature += "Couldn't Fetch Temperature"
        pass
    try:
        windchill = reqjson['main']['feels_like']
        wind += str(windchill)
    except KeyError:
        wind += "Couldn't Fetch Windchill"
        pass
    try:
        tempmax = reqjson['main']['temp_max']
        temp_max += str(tempmax)
    except KeyError:
        temp_max += "Couldn't Fetch Max Temperature"
    try:
        tempmin = reqjson['main']['temp_min']
        temp_min += str(tempmin)
    except KeyError:
        temp_min += "Couldn't Fetch Min Temperature"
    try:
        loc = reqjson['name']
        location += loc
    except KeyError:
        location += "Couldn't Fetch Location"

def compare_temperatures(place1, state1, place2, state2):
    global place1_temp, place2_temp
    link = 'https://fcc-weather-api.glitch.me/api/current?lat={}&lon={}'.format(place1, state1)
    req = requests.get(link).content
    reqjson = json.loads(req)
    place1_temp = reqjson['main']['temp']
    place1_temp = convert_celsius(place1_temp)
    link = 'https://fcc-weather-api.glitch.me/api/current?lat={}&lon={}'.format(place2, state2)
    req = requests.get(link).content
    reqjson = json.loads(req)
    place2_temp = reqjson['main']['temp']
    place2_temp = convert_celsius(place2_temp)
    bigger = place2_temp - place1_temp
    smaller = place1_temp - place2_temp
    if place2_temp > place1_temp:
        return str(bigger)[0:4]
    else:
        return str(smaller)[0:4]

def average_temperatures(lat, long, amount):
    link = 'https://api.openweathermap.org/data/2.5/find?lat={}&lon={}&cnt={}&appid=afc6ea7d660627de1cc6f6c5f591f4cc'.format(lat, long, amount)
    req = requests.get(link).content
    reqjson = json.loads(req)
    total = reqjson['count']
    numList = []
    numbers = 0
    for x in range(0, int(amount)):
        temp = reqjson['list'][x]['main']['temp']
        converted = temp * 1.8
        converted = converted - 459.67
        numList.append(converted)
    for each in numList:
        numbers = numbers + each
    avg = numbers / len(numList)
    return str(avg)[0:4]
tab1_layout = [
    [sg.Text("Get Weather Data for a City")],
    [sg.InputText('City', key='city_text'), sg.InputText('State Code', key='state_text', size=(44,1))],
    [sg.Text("Weather Description: ", size=(40,1), key="description_key")],
    [sg.Text("Temperature: ", size=(20,1), key="temperature")],
    [sg.Text("WindChill: ", size=(20,1), key="windchill")],
    [sg.Text("Max Temp: ", size=(20,1) ,key="max_temp")],
    [sg.Text("Min Temp: ", size=(20,1) ,key="min_temp")],
    [sg.Button('Get Data', size=(25,1)), sg.Button("Convert Units", size=(25, 1)), sg.Button('Quit', size=(25, 1))] 
]

tab2_layout = [
    [sg.Text("Compare Temperatures between City's")],
    [sg.InputText('City1', key='city1_text'), sg.InputText('State Code1', key='state1_text', size=(44,1))],
    [sg.InputText('City2', key='city2_text'), sg.InputText('State Code2', key='state2_text', size=(44,1))],
    [sg.Text("Temperature Difference: ", size=(25,1), key='temp_diff')],
    [sg.Text("", size=(25,1), key='place1_text')],
    [sg.Text("", size=(25,1), key='place2_text')],
    [sg.Button("Get Data", key='compare_button'), sg.Button('Quit', key='tab2_quit')]
]

tab3_layout = [
	[sg.InputText('City', key='tab3_city'), sg.InputText('State', key='tab3_state')],
	[sg.Slider(range=(1, 50), default_value=10, size=(50, 10), orientation='horizontal', key='slider')],
	[sg.Text("Average Temperature: ", key='average_temp', size=(25,1))],
  	[sg.Button('Get Data', key='average_button'), sg.Button('Quit', key='tab3_quit')]
]

tab4_layout = [
    [sg.Text("History:")],
    [sg.Multiline(size=(70,10), key='multi_text', disabled=True)],
    [sg.Button("Load History", key='load_history'), sg.Button('Quit', key='tab4_quit')]
]

layout = [
    [sg.TabGroup([[sg.Tab('Weather Data', tab1_layout), sg.Tab('Compare', tab2_layout), sg.Tab('Average Temps', tab3_layout) ,sg.Tab('History', tab4_layout)]])],
]

window = sg.Window('Weather', layout, icon='weather.ico')
while True:
    event, values = window.read()
    if event == 'Quit':
        break
    elif event == 'tab2_quit':
        break
    elif event == 'tab3_quit':
        break
    elif event == 'tab4_quit':
      break
    elif event == 'compare_button':
        place1_lat = get_location(values['city1_text'], values['state1_text'])[0]
        place1_long = get_location(values['city1_text'], values['state1_text'])[1]
        place2_lat = get_location(values['city1_text'], values['state1_text'])[0]
        place2_long = get_location(values['city2_text'], values['state2_text'])[1]
        diff = compare_temperatures(place1_lat, place1_long, place2_lat, place2_long)
        window.FindElement('temp_diff').Update('Temperature Difference: ' + diff)
        window.FindElement('place1_text').Update(values['city1_text'] + ' Temp: ' + str(place1_temp))
        window.FindElement('place2_text').Update(values['city2_text'] + ' Temp: ' + str(place2_temp))
    elif event == 'Get Data':
        lat = get_location(values['city_text'], values['state_text'])[0]
        long = get_location(values['city_text'], values['state_text'])[1]
        get_weather(lat, long)
        if isRateLimited:
            sg.Popup("Currently Being Ratelimited please try again later.", keep_on_top=True, icon='error.ico', title="Error")
            desc = ""
            wind = ""
            temperature = ""
            temp_min = ""
            temp_max = ""
            isRateLimited = False
        else:
            window.FindElement('description_key').Update('Weather Description: ' + desc)
            window.FindElement('temperature').Update("Temperature: " + str(temperature)[0:4])
            window.FindElement('windchill').Update("WindChill: " + str(wind)[0:4])
            window.FindElement('max_temp').Update("Max Temp: " + str(temp_max)[0:4])
            window.FindElement('min_temp').Update("Min Temp: " + str(temp_min)[0:4])
            write.write('{}|{}|{}|{}|{}|{}|{}\n'.format(location ,desc, temperature, wind, temp_max, temp_min, now.strftime("%d/%m/%Y %H:%M:%S")))
            write.close()
    elif event == 'Convert Units':
        if isCelsius:
            temperature = convert_celsius(float(temperature))
            wind = convert_celsius(float(wind))
            temp_max = convert_celsius(float(temp_max))
            temp_min = convert_celsius(float(temp_min))
            window.FindElement('temperature').Update("Temperature: " + str(temperature)[0:4])
            window.FindElement('windchill').Update("WindChill: " + str(wind)[0:4])
            window.FindElement('max_temp').Update("Max Temp: " + str(temp_max)[0:4])
            window.FindElement('min_temp').Update("Min Temp: " + str(temp_min)[0:4])
            isCelsius = False
        elif not isCelsius:
            temperature = convert_fahrenheit(float(temperature))
            wind = convert_fahrenheit(float(wind))
            temp_max = convert_fahrenheit(float(temp_max))
            temp_min = convert_fahrenheit(float(temp_min))
            window.FindElement('temperature').Update("Temperature: " + str(temperature)[0:4])
            window.FindElement('windchill').Update("WindChill: " + str(wind)[0:4])
            window.FindElement('max_temp').Update("Max Temp: " + str(temp_max)[0:4])
            window.FindElement('min_temp').Update("Min Temp: " + str(temp_min)[0:4])
            isCelsius = True
    elif event == 'load_history':
        window.FindElement('multi_text').Update(history)
    elif event == 'average_button':
        amount = values['slider']
        splitted = str(amount).split('.')
        amount = splitted[0]
        lat = get_location(values['tab3_city'], values['tab3_state'])[0]
        long = get_location(values['tab3_city'], values['tab3_state'])[1]
        window.FindElement('average_temp').Update('Average Temperatures: ' + average_temperatures(lat, long, amount))
window.close()
