import requests
import string
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from datetime import datetime
from geopy import geocoders
from tzwhere import tzwhere
from pytz import timezone
from flask import render_template, flash, url_for, redirect, request, jsonify
from models import *
from functions import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, LoginManager
from datetime import datetime
from main import *



@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@app.route('/')
@login_required
def index_get():
    cities = City.query.all()

    weather_data = []

    for city in cities:
        r = get_weather_data(city.name)
        weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
            'country' : r['sys']['country'],
        }
        weather_data.append(weather)
    
        
    return render_template('index.html', weather_data=weather_data)

@app.route('/', methods=['POST'])
@login_required
def index_post():
    err_msg = ''
    new_city = request.form.get('city')
    new_city = new_city.lower()
    new_city = string.capwords(new_city)
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()
        
        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)

                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = 'That is not a valid city!'
        else:
            err_msg = 'City already exists in the database!'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added successfully!', 'success')

    return redirect(url_for('index_get'))

@app.route('/delete/<name>')
@login_required
def delete_city( name ):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f"Deleted {city.name} Successfully!", 'success')
    return redirect(url_for('index_get'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', first_name=current_user.first_name)


@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False

        user = User.query.filter_by(email=email).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash("Please check your login details and try again.")
            return redirect(url_for("login")) # if the user doesn"t exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=remember)

        flash('Logged in successfully.')
        return redirect(url_for('index_get'))
    else:
        return render_template('login.html')
    

@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))


@app.route('/signup',  methods=["GET","POST"])
def signup():
    if request.method == 'POST':
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('User exists!','error')
            return redirect(url_for("signup"))

        # create a new user with the form data. Hash the password so the plaintext version isn"t saved.
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=generate_password_hash(password, method="sha256"))

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    else:
        return render_template('signup.html')
    
