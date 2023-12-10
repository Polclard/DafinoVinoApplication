import csv
import json

import flask_login
import pandas as pd
from flask import redirect
from flask import render_template, request, Blueprint, flash, url_for
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from __init__ import db


class Winery:
    def __init__(self, id, name, description, image_link, rating, location):
        self.id = id
        self.name = name
        self.description = description
        self.image_link = image_link
        self.rating = rating
        self.location = location


def instantiate_wineries():
    file = pd.read_csv("static/csv/final_scraped_wineries.csv", encoding='latin1')
    parsed_json = file.to_json(orient='records')
    parsed_json = json.loads(parsed_json)
    # print(parsed_json)
    new_list = list()
    i = 0
    for item in parsed_json:
        new_list.append(Winery(i,
                               item['Winary Name'],
                               item['Winary Description'],
                               item['Winary Image Link'],
                               item['Winary Rating'],
                               item['Winary Location']))
        i += 1
    return new_list


def find_winery_by_id(list_to_search, id):
    list_found = [item for item in list_to_search if item.id == id]
    return list_found[0]


def winery_repository():
    return instantiate_wineries()


def find_winery_by_id_ser(list_to_search, id):
    return find_winery_by_id(list_to_search, id)


main = Blueprint('main', __name__)

wineries_list = winery_repository()


@main.route('/')
def main_page():
    return render_template("mainpage.html")


@main.route('/wineries/<int:user_id>')
@login_required
def detail_winery(user_id):
    selected_winery = find_winery_by_id_ser(wineries_list, user_id)
    print(selected_winery.name)
    return render_template("detail_view.html", data=selected_winery)


@main.route('/wineries', methods=['GET'])
@login_required
def wineries():
    page = 0
    print(request.args.get('page'))
    if (request.args.get('page') is not None and
            request.args.get('page') != "" and
            request.args.get('page') != " " and
            int(request.args.get('page')) - 10 >= 0):
        page = int(request.args.get('page'))
    if (request.args.get('page') is not None and
            int(request.args.get('page')) > len(wineries_list)):
        page = 0

    return render_template("wineries.html", page=page, data=wineries_list[page: page + 10])


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, current_user=current_user)


@main.route('/saveChanges', methods=['POST'])
@login_required
def saveChanges():
    new_name = request.form.get('name')
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')

    user = flask_login.current_user
    if not user or not check_password_hash(user.password, old_password):
        flash('Something is incorrect, please try again.')
        return redirect(url_for('main.profile'))

    if new_password != "" and new_password != " ":
        flask_login.current_user.password = generate_password_hash(new_password)
    flask_login.current_user.name = new_name
    db.session.commit()
    return redirect(url_for('main.profile'))


@main.route("/location")
@login_required
def location():
    return render_template("allow_location.html")


from math import radians, sin, cos, sqrt, atan2


def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Calculate the differences between latitudes and longitudes
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Calculate the distance
    distance = R * c

    return distance


@main.route("/near_me", methods=['POST'])
@login_required
def near_me():
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    print(f"Received location: Latitude={latitude}, Longitude={longitude}")

    nearby_wineries = [winery for winery in wineries_list if
                       haversine(float(latitude),
                                 float(longitude),
                                 float(winery.location.split(" ")[0]),
                                 float(winery.location.split(" ")[1])) <= 50]

    [print(loc) for loc in nearby_wineries]
    print(len(nearby_wineries))

    return render_template("wineries_near_me.html", longitude=longitude, latitude=latitude, data=nearby_wineries)


@main.route("/add_winery")
@login_required
def add_winery():
    if current_user.is_authenticated and current_user.role.name == "ADMIN":
        return render_template('add_winery.html')
    return redirect(url_for('main.wineries'))


@main.route("/add_winery_post", methods=['POST'])
@login_required
def add_winery_post():
    if current_user.is_authenticated and current_user.role.name == "ADMIN":
        winery_name = request.form.get("winery_name")
        winery_description = request.form.get("winery_description")
        winery_rating = float(request.form.get("winery_rating"))
        winery_image_link = request.form.get("winery_image_link")
        winery_longitude = request.form.get("winery_longitude")
        winery_latitude = request.form.get("winery_latitude")

        winery_coordinates = f"{winery_longitude} {winery_latitude}"

        file_path = "static/csv/final_scraped_wineries.csv"
        # Open the CSV file in 'a' (append) mode to add a new row
        with open(file_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Write the new row data
            csv_writer.writerow([winery_name, winery_description, winery_image_link, winery_rating, winery_coordinates])

        global wineries_list
        wineries_list = winery_repository()

    return redirect(url_for('main.wineries'))


def delete_row_from_csv(file_path, row_index_to_delete):
    # Read the CSV file into a list of lists
    with open(file_path, 'r', newline='', encoding='latin1') as csvfile:
        csv_reader = csv.reader(csvfile)
        data = list(csv_reader)

    # Check if the row index to delete is within the valid range
    if 0 <= row_index_to_delete < len(data):
        # Delete the specified row
        del data[row_index_to_delete]

        # Write the updated data back to the CSV file
        with open(file_path, 'w', newline='', encoding='latin1') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(data)
        print(f"Row at index {row_index_to_delete} deleted.")
    else:
        print("Invalid row index.")


@main.route('/delete_winery/<int:item_id>')
@login_required
def delete_winery(item_id):
    if current_user.is_authenticated and current_user.role.name == "ADMIN":
        print("YES")
        delete_row_from_csv("static/csv/final_scraped_wineries.csv", int(item_id) + 1)
        global wineries_list
        wineries_list = winery_repository()
    return redirect(url_for('main.wineries'))
