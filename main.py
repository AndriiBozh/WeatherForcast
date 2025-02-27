import streamlit as st
import plotly.express as px
import dotenv
import requests

first_part_of_url = dotenv.get_key('.env', 'URL')
api_key = dotenv.get_key('.env', 'API_KEY')


# by default, 'openweathermap' sends us a forecast for 5 days.
# they give 3-hours forecast, i.e., 24 hours / 3 = 8 forecasts for each day.
# each forcast is a dictionary. Dictionaries are in a list.
# so, by default, we get a list of 5 x 8 = 40 dictionaries.
# to get result for a required number of days, we multiply 8 by a value, provided by user

def construct_url(url_base, city_name, key, number_of_days):
    cnt = number_of_days * 8
    return f'{url_base}q={city_name}&appid={key}&units=metric&cnt={cnt}'


main_header = 'Weather Forcast'
st.title(main_header)

place = st.text_input('Place: ')
days = st.slider('Pick a number of days', 1, 5, help='Select a number of days by moving a slider')
temperature_or_sky = st.selectbox('Pick one', ['Temperature', 'Sky condition'])

days_text = "day" if days == 1 else f"{days} days"
output = f"{place}. {temperature_or_sky} for the next {days_text}:"
full_url = construct_url(first_part_of_url, place, api_key, days)


def get_weather_data(url):
    req = requests.get(url=url)
    data = req.json()
    return data


if place:
    try:
        weather_data = get_weather_data(full_url)
        # do not show subheader in case the place (city, or town) was not found
        if weather_data['cod'] != '404':
            st.subheader(output)

        if temperature_or_sky == 'Temperature':  # default
            temperature = [el['main']['temp'] for el in weather_data['list']]
            dates = [el['dt_txt'] for el in weather_data['list']]

            figure = px.line(x=dates, y=temperature, labels={'x': 'Date', 'y': 'Temperature'})
            st.plotly_chart(figure)

        if temperature_or_sky == 'Sky condition':
            sky_cond = [el['weather'][0]['main'] for el in weather_data['list']]
            images = {'Clear': 'images/clear.png', 'Clouds': 'images/clouds.png', 'Rain': 'images/rain.png',
                      'Snow': 'images/snow.png'}
            # sky_cond items are, for example: ['Clear', 'Clear', 'Snow', 'Rain', ....]
            # item is, for example, 'Clear'
            # images[item] => images['Clear'] gives us element from
            # 'images' dictionary with a key 'Clear', that is 'images/clear.png'
            images_paths = [images[item] for item in sky_cond]
            st.image(images_paths, width=50)
    except KeyError:
        st.write(f'Unable to find {place}')
