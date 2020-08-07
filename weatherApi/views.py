from bs4 import BeautifulSoup
from django.shortcuts import render
import requests


def getHtmlContent(city):
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE

    # making considerations for places with spaces in between 
    city = city.replace(' ', '+')
    html_content = session.get(f'https://www.google.com/search?q=weather+in+{city}').text
    return html_content


def getHtmlTime(city):
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE

    # making considerations for places with spaces in between
    city = city.replace(' ', '+')
    html_time = session.get(f'https://www.google.com/search?q=time+in+{city}').text
    return html_time


def home(request):
    weatherData = None
    if 'city' in request.GET:
        # fetch weather data from Google
        city = request.GET.get('city')

        htmlContent = getHtmlContent(city)  # function call to get weather.
        cityTime = getHtmlTime(city) # function call to get time in that specific location.

        # parse the html content into human readable data in order to be able to present it to the user.
        soup = BeautifulSoup(htmlContent, 'html.parser')
        soupTime = BeautifulSoup(cityTime, 'html.parser')
        weatherData = dict()

        # checking to confirm if getHtmlContent returned some data for us "this handles if a place doesn't exits"
        try:
            tem = soup.find('span', attrs={'id': 'wob_tm'})  # I'm using the temperature value to do it.
        except ArithmeticError as e:
            return None
        else:
            weatherData['temp'] = tem
            while weatherData['temp'] is None:  # if it's 'True' that means no data returned so the place wasn't found.
                return render(request, 'weatherApi/404.html')

        weatherData['region'] = soup.find('div', attrs={'id': 'wob_loc'}).text
        for time in soupTime.findAll('div', attrs={'class': 'gsrt vk_bk dDoNo XcVN5d'}):
            weatherData['timeOfTheDay'] = time.text

        for date in soupTime.findAll('div', attrs={'class': 'vk_gy vk_sh'}):
            weatherData['date'] = date.text

        weatherData['weatherStatus'] = soup.find('span', attrs={'id': 'wob_dc'}).text
        # get the precipitation
        weatherData['precipitation'] = soup.find("span", attrs={"id": "wob_pp"}).text
        # get the % of humidity
        weatherData['humidity'] = soup.find("span", attrs={"id": "wob_hm"}).text
        # extract the wind
        weatherData['wind'] = soup.find("span", attrs={"id": "wob_ws"}).text
        weatherData['temperature'] = soup.find('span', attrs={'id': 'wob_tm'}).text

        # getting the weather for the next few days, this is where I'm fetching the daily Max & Min temperature ranges.
        dayMaxMin = soup.find('div', attrs={'id': 'wob_dp'})
        for day in dayMaxMin.findAll('div', attrs={'class': 'wob_df'}):
            temp = day.findAll('span', {'class': 'wob_t'})
            # maximum temperature in Celsius.
            max_temp = temp[0].text
            weatherData['maxTemp'] = max_temp
            # minimum temperature in Celsius.
            min_temp = temp[2].text
            weatherData['minTemp'] = min_temp
            break
    return render(request, 'weatherApi/home.html', {'weather': weatherData})
