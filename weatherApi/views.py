from bs4 import BeautifulSoup
from django.http import Http404
from django.http import HttpResponse, HttpResponseNotFound
import datetime
from django.shortcuts import render
import requests
from django.contrib import messages

# Create your views here.
from django.template import loader, Context


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


def home(request):
    weatherData = None
    if 'city' in request.GET:
        # fetch weather data from Google
        city = request.GET.get('city')

        htmlContent = getHtmlContent(city)

        # parse the html content into human readable data in order to be able to present it to the user.
        soup = BeautifulSoup(htmlContent, 'html.parser')

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
        weatherData['timeOfTheDay'] = soup.find('div', attrs={'id': 'wob_dts'}).text
        weatherData['weatherStatus'] = soup.find('span', attrs={'id': 'wob_dc'}).text
        weatherData['temperature'] = soup.find('span', attrs={'id': 'wob_tm'}).text

        # getting the weather for the next few days, this is where I'm fetching the daily Max & Min temperature ranges.
        days = soup.find('div', attrs={'id': 'wob_dp'})
        for day in days.findAll('div', attrs={'class': 'wob_df'}):
            temp = day.findAll('span', {'class': 'wob_t'})
            # maximum temperature in Celsius.
            max_temp = temp[0].text
            weatherData['maxTemp'] = max_temp
            # minimum temperature in Celsius.
            min_temp = temp[2].text
            weatherData['minTemp'] = min_temp
            break

    return render(request, 'weatherApi/home.html', {'weather': weatherData})

# def current_datetime(request):
#     now = datetime.datetime.now()
#     html = "<html><body>It is now %s.</body></html>" % now
#     return HttpResponse(html)
