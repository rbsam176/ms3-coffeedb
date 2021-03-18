import os
import sys
import random
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def index():
    beans = mongo.db.beans.find()
    return render_template("index.html", beans=beans)

@app.route("/add", methods=["GET", "POST"])
def add():
    beans = mongo.db.beans.find().sort("_id", -1).limit(3)
    coffeeImg = "https://images.photowall.com/products/49771/coffee-beans.jpg"
    roast_types = mongo.db.beans.distinct('roast') # GETS ALL UNIQUE VALUES WITH KEY OF 'ROAST'
    origin_types = mongo.db.beans.distinct('origin') # GETS ALL UNIQUE VALUES WITH KEY OF 'ORIGIN'
    uniqueNotes = mongo.db.beans.distinct('notes') # RETURNS LIST OF UNIQUE NOTES
    brand_names = mongo.db.beans.distinct('brand') # RETURNS LIST OF UNIQUE BRANDS
    username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
    first_name = mongo.db.users.find_one({"username": session["user"]})["first_name"]
    last_name = mongo.db.users.find_one({"username": session["user"]})["last_name"]
    full_name = first_name + " " + last_name
    if request.method == "POST":
        userInput = {
            "brand": request.form["brand"],
            "name": request.form["name"],
            "roast": request.form["roast"],
            "origin": request.form["origin"],
            "notes": request.form.getlist('note'),
            "organic": bool(request.form.get("organic")),
            "url": request.form["website"],
            "img-url": request.form['imgURL'],
            "username": username,
            "full_name": full_name
        }
        mongo.db.beans.insert_one(userInput)

    return render_template("add.html", beans=beans, coffeeImg=coffeeImg, roast_types=roast_types, origin_types=origin_types, uniqueNotes=uniqueNotes, brand_names=brand_names, full_name=full_name)

@app.route("/browse", methods=["GET"])
def browse():
    beans = mongo.db.beans.find() # DEFAULT VIEW SHOWS ALL RESULTS
    notes = mongo.db.beans.find({}, {"notes" : 1}) # RETURNS LIST OF ALL NON-UNIQUE NOTES
    uniqueNotes = mongo.db.beans.distinct('notes') # RETURNS LIST OF ALL UNIQUE NOTES
    roast_types = mongo.db.beans.distinct('roast') # GETS ALL UNIQUE VALUES WITH KEY OF 'ROAST'
    origin_types = mongo.db.beans.distinct('origin') # GETS ALL UNIQUE VALUES WITH KEY OF 'ORIGIN'
    roastChecked = [] # RETURNS LIST OF ALL ROAST TYPES THAT WERE CHECKED
    originChecked = [] # RETURNS LIST OF ALL ORIGINS THAT WERE CHECKED
    organicChecked = [] # RETURNS WHETHER ORGANIC TOGGLE WAS ON/OFF
    notesChecked = [] # RETURNS LIST OF ALL NOTES THAT WERE CHECKED
    notesCollection = list(notes) # CONVERTS NON-UNIQUE LIST OF NOTES INTO LIST
    notesList = [y for x in notesCollection for y in x['notes']] # UNPACKS LIST INTO LIST OF JUST NOTES VALUES
    notesCount = {note:notesList.count(note) for note in uniqueNotes} # CONTAINS UNIQUE NOTES WITH ITS COUNT OF OCCURANCE

    notesPercentage = {}
    for x in notesCount:
        length = len(uniqueNotes) # RETURNS NUMBER OF NOTES
        occurance = notesCount.get(x) # RETURNS HOW MANY TIMES NOTES OCCUR
        percentage = occurance / length * 100 # DIVIDES TOTAL NUMBER OF NOTES BY OCCURANCE 
        notesPercentage[x] = percentage # ADDS TO DICTIONARY

    highestNoteDict = max(notesPercentage, key=notesPercentage.get) # SOURCE: https://stackoverflow.com/a/14091645
    highestPercent = notesPercentage.get(highestNoteDict) # HIGHEST PERCENTAGE
    
    notesRelativePercentage = {}
    for x in notesPercentage:
        relativePercentage = notesPercentage.get(x) / highestPercent * 100 # DIVIDES PERCENTAGE BY THE HIGHEST PERCENTAGE
        notesRelativePercentage[x] = round(relativePercentage, 1) # ROUNDS IT DOWN

    # DYNAMICALLY CREATES A FIND QUERY
    # ADAPTED FROM https://stackoverflow.com/questions/65823199/dynamic-mongo-query-with-python
    dynamicQuery = {}
    dynamicQuery["$and"]=[]

    # GETS USER INPUT DATA AND APPENDS IT TO LISTS
    if request.method == "GET":
        for roast in request.args.getlist("roast"):
            roastChecked.append(roast)
        for origin in request.args.getlist("origin"):
            originChecked.append(origin)
        if bool(request.args.getlist("organicRequired")):
            organicChecked.append(True)
        for tag in request.args.getlist("tag"):
            notesChecked.append(tag)
       
        # CHECKS IF LIST VALUES EXIST AND APPENDS TO DYNAMIC QUERY
        if roastChecked:
            dynamicQuery["$and"].append({ "roast": { "$in": roastChecked}})
        if originChecked:
            dynamicQuery["$and"].append({ "origin": { "$in": originChecked }})
        if organicChecked:
            dynamicQuery["$and"].append({ "organic": True })
        if notesChecked:
            dynamicQuery["$and"].append({ "notes": { "$in": notesChecked }})
        
        # REPLACES BEANS DATA WITH DYNAMIC QUERY IF EXISTS
        if dynamicQuery["$and"]:
            beans = mongo.db.beans.find(dynamicQuery)

    beans = list(beans) # CONVERTS TO LIST BEFORE PASSING INTO TEMPLATE

    return render_template("browse.html", beans=beans, roast_types=roast_types, origin_types=origin_types, roastChecked=roastChecked, originChecked=originChecked, organicChecked=organicChecked, notesRelativePercentage=notesRelativePercentage, notesChecked=notesChecked)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    roast_types = mongo.db.beans.distinct('roast') # GETS ALL UNIQUE VALUES WITH KEY OF 'ROAST'
    brand_names = mongo.db.beans.distinct('brand') # GETS ALL UNIQUE VALUES WITH KEY OF 'BRAND'
    origin_types = mongo.db.beans.distinct('origin') # GETS ALL UNIQUE VALUES WITH KEY OF 'ORIGIN'
    if request.method == "POST":
        existing_user_email = mongo.db.users.find_one({"email": request.form.get("inputEmail").lower()})
        existing_user_username = mongo.db.users.find_one({"username": request.form.get("inputUsername").lower()})
        if existing_user_email:
            flash(u"An account with this email already exists", "warning")
            return redirect(url_for("signup"))
        if existing_user_username:
            flash(u"An account with this username already exists", "warning")
            return redirect(url_for("signup"))
        newUser = {
            "first_name": request.form.get("inputFirstName").lower(),
            "last_name": request.form.get("inputLastName").lower(),
            "email": request.form.get("inputEmail"),
            "username": request.form.get("inputUsername"),
            "password": generate_password_hash(request.form.get("inputPassword")),
            "birthdate": request.form.get("inputBirthdate").lower(),
            "country": request.form.get("inputCountry").lower(),
            "pref_roast": request.form.get("inputPrefRoast").lower(),
            "pref_brand": request.form.get("inputPrefBrand").lower(),
            "pref_organic": request.form.get("inputPrefOrganic").lower(),
            "pref_origin": request.form.get("inputPrefOrigin").lower(),
            "discovery": request.form.get("inputDiscovery").lower()
        }
        mongo.db.users.insert_one(newUser)
        session["user"] = request.form.get("inputUsername").lower()
        flash(u"Registration Successful!", "success")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("signup.html", roast_types=roast_types, brand_names=brand_names, origin_types=origin_types)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user_email = mongo.db.users.find_one(
            {"email": request.form.get("loginEmail").lower()})
        existing_user_username = mongo.db.users.find_one(
            {"username": request.form.get("loginUsername").lower()})
        if existing_user_email or existing_user_username:
            # CHECKS IF HASHED PASSWORD MATCHES USER INPUT
            if check_password_hash(existing_user_username["password"], request.form.get("loginPassword")):
                session["user"] = request.form.get("loginUsername").lower()
                flash(u"Welcome {}".format(existing_user_username["first_name"].capitalize()), "success")
                return redirect(url_for("profile", username=session["user"]))
            else:
                # INVALID PASSWORD MATCH
                flash(u"Could not find a matching user", "warning")
                return redirect(url_for("login"))
        else:
            # INCORRECT EMAIL
            flash(u"Could not find a matching user", "warning")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
    if session["user"]:
        return render_template("profile.html", username=username)
    
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    flash(u"You have been logged out", "success")
    session.pop("user")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)
