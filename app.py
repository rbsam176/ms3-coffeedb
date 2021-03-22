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

def dynamicValues(fixed, databaseKey):
    combinedList = [fixed] + [databaseKey]
    removeDuplicates = set().union(*combinedList)
    return removeDuplicates

coffeeBeans = {
    "roast_types": ["dark", "medium", "light", "unknown"],
    "origin_types": dynamicValues(["brazil", "england"], mongo.db.beans.distinct('origin')),
    "brand_names": dynamicValues(["union", "monmouth", "starbucks"], mongo.db.beans.distinct('brand')),
    "unique_notes": dynamicValues(["caramel", "prune", "cherry"], mongo.db.beans.distinct('notes')),
    "coffeeImg": "https://images.photowall.com/products/49771/coffee-beans.jpg"
}

accountPreferences = {
    "organic_preferred": ["yes", "can't tell the difference", "never think about it"],
    "site_discovery": ["search engine", "from a friend", "online advertising", "offline advertising"]
}

@app.route("/")
def index():
    beans = mongo.db.beans.find()
    return render_template("index.html", beans=beans)

@app.route("/add", methods=["GET", "POST"])
def add():
    beans = mongo.db.beans.find().sort("_id", -1).limit(3) # RETURN MOST RECENT 3 ENTRIES
    username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
    first_name = mongo.db.users.find_one(
        {"username": session["user"]})["first_name"]
    last_name = mongo.db.users.find_one(
        {"username": session["user"]})["last_name"]
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

    return render_template("add.html", beans=beans, coffeeImg=coffeeBeans["coffeeImg"], roast_types=coffeeBeans["roast_types"], origin_types=coffeeBeans["origin_types"], uniqueNotes=coffeeBeans["unique_notes"], brand_names=coffeeBeans["brand_names"], full_name=full_name)

@app.route("/browse", methods=["GET"])
def browse():
    beans = mongo.db.beans.find() # DEFAULT VIEW SHOWS ALL RESULTS
    notes = mongo.db.beans.find({}, {"notes" : 1}) # RETURNS LIST OF ALL NON-UNIQUE NOTES IN DB
    uniqueNotes = coffeeBeans["unique_notes"] # RETURNS LIST OF ALL UNIQUE NOTES
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

    return render_template("browse.html", beans=beans, roast_types=coffeeBeans["roast_types"], origin_types=coffeeBeans["origin_types"], roastChecked=roastChecked, originChecked=originChecked, organicChecked=organicChecked, notesRelativePercentage=notesRelativePercentage, notesChecked=notesChecked)


@app.route("/edit/<beanId>", methods=["GET", "POST"])
def edit(beanId):
    print(beanId)
    matchedBean = mongo.db.beans.find_one(
            {"_id": ObjectId(beanId)})
    editBean = [matchedBean]
    if session["user"] == matchedBean["username"]:
        return render_template("edit.html", editBean=editBean)


@app.route("/signup", methods=["GET", "POST"])
def signup():
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
            "email": request.form.get("inputEmail").lower(),
            "username": request.form.get("inputUsername").lower(),
            "password": generate_password_hash(request.form.get("inputPassword")),
            "birthdate": request.form.get("inputBirthdate"),
            "country": request.form.get("inputCountry").lower(),
            "pref_roast": request.form.get("inputPrefRoast"),
            "pref_brand": request.form.get("inputPrefBrand"),
            "pref_organic": request.form.get("inputPrefOrganic"),
            "pref_origin": request.form.get("inputPrefOrigin"),
            "discovery": request.form.get("inputDiscovery")
        }
        mongo.db.users.insert_one(newUser)
        session["user"] = request.form.get("inputUsername").lower()
        flash(u"Registration Successful!", "success")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("signup.html", roast_types=coffeeBeans["roast_types"], brand_names=coffeeBeans["brand_names"], origin_types=coffeeBeans["origin_types"], organic_preferences=accountPreferences["organic_preferred"], site_discovery=accountPreferences["site_discovery"])


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

@app.route("/profile/<username>")
def profile(username):
    users = mongo.db.users.distinct('username') # RETURNS LIST OF USERS IN DATABASE
    if username in users: # IF URL CONTAINS REAL USERNAME
        user_submissions = mongo.db.beans.find({"username": username}) # GETS THEIR SUBMISSIONS
        first_name = mongo.db.users.find_one(
            {"username": username})["first_name"] # GETS THEIR FIRST NAME
        # RENDERS PROFILE PAGE VISISBLE TO ALL
        return render_template("profile.html", username=username, first_name=first_name, user_submissions=user_submissions)
    else:
        print('username not match')
        # REDIRECTS TO HOMEPAGE IS URL USERNAME DOESN'T EXIST IN DATABASE
        return redirect(url_for("index"))


@app.route("/profile/<username>/update_account", methods=["GET", "POST"])
def update_account(username):
    # IF USER ISN'T LOGGED IN OR NOT LOGGED IN AS USER OF PROFILE BEING VIEWED
    if "user" not in session or session["user"] != username:
        print('no user logged in')
        # REDIRECTS TO PROFILE PAGE
        return redirect(url_for("profile", username=username))
    if session["user"] == username: # IF LOGGED IN AS USER BEING VIEWED
        # GETS CURRENT PREFERENCES OF USER TO PRE-FILL INPUTS
        existingPreferences = {
            "first_name": mongo.db.users.find_one(
                {"username": session["user"]})["first_name"],
            "last_name": mongo.db.users.find_one(
                {"username": session["user"]})["last_name"],
            "email": mongo.db.users.find_one(
                {"username": session["user"]})["email"],
            "username": mongo.db.users.find_one(
                {"username": session["user"]})["username"],
            "birthdate": mongo.db.users.find_one(
                {"username": session["user"]})["birthdate"],
            "country": mongo.db.users.find_one(
                {"username": session["user"]})["country"],
            "pref_roast": mongo.db.users.find_one(
                {"username": session["user"]})["pref_roast"],
            "pref_brand": mongo.db.users.find_one(
                {"username": session["user"]})["pref_brand"],
            "pref_organic": mongo.db.users.find_one(
                {"username": session["user"]})["pref_organic"],
            "pref_origin": mongo.db.users.find_one(
                {"username": session["user"]})["pref_origin"],
            "discovery": mongo.db.users.find_one(
                {"username": session["user"]})["discovery"]
        }
        # IF UPDATE REQUEST IS SENT
        if request.method == "POST":
            # RETRIEVES NEW PREFERENCES
            editedPreferences = {
                "first_name": request.form.get("inputFirstName").lower(),
                "last_name": request.form.get("inputLastName").lower(),
                "email": request.form.get("inputEmail").lower(),
                "birthdate": request.form.get("inputBirthdate"),
                "country": request.form.get("inputCountry").lower(),
                "pref_roast": request.form.get("inputPrefRoast"),
                "pref_brand": request.form.get("inputPrefBrand"),
                "pref_organic": request.form.get("inputPrefOrganic"),
                "pref_origin": request.form.get("inputPrefOrigin"),
                "discovery": request.form.get("inputDiscovery")
            }
            # FINDS THE USERS UNIQUE ID IDENTIFIER
            userId = mongo.db.users.find_one(
            {"username": session["user"]})["_id"]
            # UPDATES THE DATABASE WITH NEW VALUES
            mongo.db.users.update_one(
                {"_id": userId},
                {"$set": editedPreferences}
            )
            # VALIDATES THE UPDATE HAS COMPLETED
            flash(u"Your changes have been saved", "success")
            return redirect(url_for("update_account", username=session["user"]))

        return render_template("update_account.html", username=existingPreferences["username"], first_name=existingPreferences["first_name"], last_name=existingPreferences["last_name"], email=existingPreferences["email"], birthdate=existingPreferences["birthdate"], country=existingPreferences["country"], pref_roast=existingPreferences["pref_roast"], pref_organic=existingPreferences["pref_organic"], pref_origin=existingPreferences["pref_origin"], discovery_options=accountPreferences["site_discovery"], discovery=existingPreferences["discovery"], roast_types=coffeeBeans["roast_types"], brand_names=coffeeBeans["brand_names"], pref_brand=existingPreferences["pref_brand"], organic_preferences=accountPreferences["organic_preferred"], origin_types=coffeeBeans["origin_types"])

@app.route("/profile/<username>/delete_account", methods=["GET", "POST"])
def delete_account(username):
    first_name = mongo.db.users.find_one(
            {"username": username})["first_name"] # GETS THEIR FIRST NAME
    deletion_types = {
        "delete_everything": "No, delete them along with my account",
        "keep_submissions": "Yes, keep them available for others to see" 
    }

    if request.method == "POST":
        deletionType = request.form.get("confirmDeletionType") # RETURNS DELETION CHOICE
        loggedInAccount = mongo.db.users.find_one(
            {"username": session["user"]}) # RETURNS MATCHING USERNAME FROM DATABASE

        # INCORRECT USERNAME VALIDATION
        if session["user"] != request.form.get("confirmUsername"):
            flash(u"You did not enter the correct username. Try again.", "warning")
            return redirect(url_for("delete_account", username=username))
        else:
            # USERNAME AND PASSWORD MATCHED
            if check_password_hash(loggedInAccount["password"], request.form.get("confirmPassword")):
                # DELETE USER AND THEIR SUBMISSIONS
                if deletionType == deletion_types["delete_everything"]:
                    submissionsQuery = {"username": loggedInAccount["username"]}
                    mongo.db.beans.delete_many(submissionsQuery)
                    mongo.db.users.delete_one(loggedInAccount)
                # DELETE ONLY USER, KEEP SUBMISSIONS
                if deletionType == deletion_types["keep_submissions"]:
                    mongo.db.users.delete_one(loggedInAccount)
                # DELETION VALIDATION
                flash(u"Your account has been permanently deleted", "success")
                session.pop("user") # LOG USER OUT
                return redirect(url_for("index"))
            else:
                # USERNAME IS CORRECT BUT PASSWORD INPUT DID NOT MATCH
                flash(u"You did not enter the correct password. Try again.", "warning")
                return redirect(url_for("delete_account", username=username))
                
    return render_template("delete_account.html", username=username, first_name=first_name, deletion_types=deletion_types)

@app.route("/logout")
def logout():
    flash(u"You have been logged out", "success")
    session.pop("user")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)
