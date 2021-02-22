"""
Mykola Kryvyi
Lab 2.3
"""
import requests
import folium
from geopy.geocoders import Nominatim
from flask import Flask, render_template, request
def twitter_api(person):
    """
    (str) -> json

    Function uses Twitter API and returns information of friends list
    of the person
    """
    base_url = "https://api.twitter.com/"

    bearer_token = ""

    search_url = '{}1.1/friends/list.json'.format(base_url)

    search_headers = {
        'Authorization': 'Bearer {}'.format(bearer_token)
    }

    search_params = {
        'screen_name': person,
        'count':30
    }

    response = requests.get(search_url, headers = search_headers, params=search_params)
    return response

def friends_location(person):
    """
    (str) -> (list)
    Function returns list of lists, and in each list there is a name of the
    friend and his location(address)
    >>> friends_location("@BarackObama")
    ['BillClinton', 'New York, NY'], ['KamalaHarris', 'California'],...
    """
    json_response = twitter_api(person).json()['users']
    list_of_users = []
    for user in json_response:
        if user['location'] != '':
            list_of_users.append([user['screen_name'], user['location']])
    return list_of_users

def finding_coordinates(person):
    """
    (str) -> (list)
    Function finds coordinates of the location of each friend and
    adds it to the list
    >>> finding_coordinates('@BarackObama')
    [['BillClinton', 'New York, NY', (40.7127281, -74.0060152)],\
['KamalaHarris', 'California', (36.7014631, -118.755997)],...
    """
    geolocator = Nominatim(user_agent="Twitter map")
    list_of_lists = friends_location(person)
    for user in list_of_lists:
        place = user[1]
        try:
            location_friend = geolocator.geocode(place)
            coordinates = (location_friend.latitude, location_friend.longitude)
            user.append(coordinates)
        except AttributeError:
            continue
    return list_of_lists

def creating_map(person):
    """
    (str) -> str
    Function creates an HTML map with icons, that demonstrate location
    of user's friends.
    """
    mainlst = finding_coordinates(person)
    my_map = folium.Map(location=[mainlst[0][2][0],mainlst[0][2][1]],zoom_start = 6)
    my_group = folium.FeatureGroup(name = 'Twitter map')
    for user in mainlst:
        try:
            name = user[0]
            friendslatitude = user[2][0]
            friendslongtitude = user[2][1]
            my_group.add_child(folium.Marker(location=[friendslatitude,friendslongtitude], \
            popup = name, icon = folium.Icon(color = 'darkblue', icon='cloud')))
        except IndexError:
            continue
    my_map.add_child(my_group)
    my_map.save('templates/twitter.html')
    return 'twitter.html'

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    """
    Function that creates HTML page, so that the user can unput
    the name of the Twitter account he would like to observe information about
    """
    if request.method == "POST":
        msg = request.form.get('msg')
        print(msg)
        return render_template(creating_map(msg))

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
