import os
import sys
import random
import datetime
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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403

@app.route("/")
def index():
    beans = mongo.db.beans.find()
    return render_template("index.html", beans=beans)


def gatherInputs():
    userInput = {
        "brand": request.form["brand"],
        "name": request.form["name"],
        "roast": request.form["roast"],
        "origin": request.form["origin"],
        "notes": request.form.getlist('note'),
        "organic": bool(request.form.get("organic")),
        "url": request.form["website"],
        "img-url": request.form['imgURL'],
        "username": mongo.db.users.find_one(
            {"username": session["user"]})["username"]
    }
    return userInput


@app.route("/add", methods=["GET", "POST"])
def add():
    beans = mongo.db.beans.find().sort("_id", -1).limit(3) # RETURN MOST RECENT 3 ENTRIES
    form_type = "addCoffee"
    full_name = mongo.db.users.find_one(
        {"username": session["user"]})["first_name"] + " " + mongo.db.users.find_one(
        {"username": session["user"]})["last_name"]
    if request.method == "POST":
        print('add submitted')
        inputDictionary = gatherInputs()
        inputDictionary["full_name"] = full_name
        if mongo.db.beans.find_one(
            {"name": inputDictionary["name"]}):
            submissionImg = gatherInputs()["img-url"]
            brand_choice = gatherInputs()["brand"]
            coffee_name = gatherInputs()["name"]
            roast_choice = gatherInputs()["roast"]
            origin_choice = gatherInputs()["origin"]
            organic_choice = gatherInputs()["organic"]
            url_input = gatherInputs()["url"]
            notes_input = gatherInputs()["notes"]
            flash(u"A coffee with this name already exists.", "warning")
            context = {
                'form_type' : form_type,
                'notes_input' : notes_input,
                'url_input' : url_input,
                'organic_choice' : organic_choice,
                'origin_choice' : origin_choice,
                'roast_choice' : roast_choice,
                'coffee_name' : coffee_name,
                'brand_choice' : brand_choice,
                'submissionImg' : submissionImg,
                'coffeeImg' : coffeeBeans["coffeeImg"],
                'roast_types' : coffeeBeans["roast_types"],
                'origin_types' : coffeeBeans["origin_types"],
                'uniqueNotes' : coffeeBeans["unique_notes"],
                'brand_names' : coffeeBeans["brand_names"],
                'beans' : beans
            }
            return render_template("add.html", **context)

        mongo.db.beans.insert_one(inputDictionary)
        flash(u"Your submission has been added.", "success")
        return redirect(url_for("add"))

    context = {
            'form_type' : form_type,
            'beans' : beans,
            'coffeeImg' : coffeeBeans["coffeeImg"],
            'roast_types' : coffeeBeans["roast_types"],
            'origin_types' : coffeeBeans["origin_types"],
            'uniqueNotes' : coffeeBeans["unique_notes"],
            'brand_names' : coffeeBeans["brand_names"],
            'full_name' : full_name
        }
    return render_template("add.html", **context)


@app.route("/edit/<beanId>", methods=["GET", "POST"])
def edit(beanId):
    matchedBean = mongo.db.beans.find_one(
            {"_id": ObjectId(beanId)})
    submissionImg = matchedBean["img-url"]
    full_name = matchedBean["full_name"]
    brand_choice = matchedBean["brand"]
    coffee_name = matchedBean["name"]
    roast_choice = matchedBean["roast"]
    origin_choice = matchedBean["origin"]
    organic_choice = matchedBean["organic"]
    url_input = matchedBean["url"]
    notes_input = matchedBean["notes"]
    form_type = "editCoffee"


    if request.method == "POST":
        print('edit submitted')
        mongo.db.beans.update_one(
            {"_id": ObjectId(beanId)},
            {"$set": gatherInputs()}
        )
        flash(u"Your submission has been edited.", "success")
        return redirect(url_for("edit", beanId=beanId))
        

    if session["user"] == matchedBean["username"]:
        context = {
            'form_type' : form_type,
            'notes_input' : notes_input,
            'url_input' : url_input,
            'organic_choice' : organic_choice,
            'origin_choice' : origin_choice,
            'roast_choice' : roast_choice,
            'coffee_name' : coffee_name,
            'brand_choice' : brand_choice,
            'submissionImg' : submissionImg,
            'coffeeImg' : coffeeBeans["coffeeImg"],
            'roast_types' : coffeeBeans["roast_types"],
            'origin_types' : coffeeBeans["origin_types"],
            'uniqueNotes' : coffeeBeans["unique_notes"],
            'brand_names' : coffeeBeans["brand_names"],
            'full_name' : full_name
        }
        return render_template("edit.html", **context)


# CREATES DICTIONARY OF UNIQUE ITEMS AND THEIR OCCURANCE PERCENTAGE
def wordCloud(list, uniqueList):
    itemCount = {item:list.count(item) for item in uniqueList} # CONTAINS UNIQUE NOTES WITH ITS COUNT OF OCCURANCE

    itemPercentage = {}
    for item in itemCount:
        length = len(uniqueList) # RETURNS NUMBER OF NOTES
        occurance = itemCount.get(item) # RETURNS HOW MANY TIMES NOTES OCCUR
        percentage = occurance / length * 100 # DIVIDES TOTAL NUMBER OF NOTES BY OCCURANCE 
        itemPercentage[item] = percentage # ADDS TO DICTIONARY
    
    most_common_item = max(itemPercentage, key=itemPercentage.get) # SOURCE: https://stackoverflow.com/a/14091645
    most_common_percentage = itemPercentage.get(most_common_item) # HIGHEST PERCENTAGE
    
    itemPercentageDict = {}
    for num in itemPercentage:
        percentage = itemPercentage.get(num) / most_common_percentage * 100 # DIVIDES PERCENTAGE BY THE HIGHEST PERCENTAGE
        itemPercentageDict[num] = round(percentage, 1) # ROUNDS IT DOWN
    
    return itemPercentageDict

@app.route("/browse", methods=["GET"])
def browse():
    beans = mongo.db.beans.find() # DEFAULT VIEW SHOWS ALL RESULTS
    notes = mongo.db.beans.find({}, {"notes" : 1}) # RETURNS LIST OF ALL NON-UNIQUE NOTES IN DB
    uniqueNotes = coffeeBeans["unique_notes"] # RETURNS LIST OF ALL UNIQUE NOTES
    roastChecked = [] # RETURNS LIST OF ALL ROAST TYPES THAT WERE CHECKED
    originChecked = [] # RETURNS LIST OF ALL ORIGINS THAT WERE CHECKED
    organicChecked = [] # RETURNS WHETHER ORGANIC TOGGLE WAS ON/OFF
    notesChecked = [] # RETURNS LIST OF ALL NOTES THAT WERE CHECKED
    
    # CREATE DICTIONARY FOR WORD CLOUD
    notesCollection = list(notes) # CONVERTS NON-UNIQUE LIST OF NOTES INTO LIST
    notesList = [y for x in notesCollection for y in x['notes']] # UNPACKS LIST INTO LIST OF JUST NOTES VALUES
    notesRelativePercentage = wordCloud(notesList, uniqueNotes)

    # DYNAMICALLY CREATES A FIND QUERY
    # ADAPTED FROM https://stackoverflow.com/questions/65823199/dynamic-mongo-query-with-python
    dynamicQuery = {}
    dynamicQuery["$and"]=[]
    # GETS USER INPUT DATA AND APPENDS IT TO LISTS
    if request.method == "GET":

        # GETS SEARCH TEXT INPUT
        searchInput = request.args.get("searchCriteria")
        # GETS SEARCH TYPE (BRAND/NAME)
        searchType = request.args.get("searchType")
        # MATCHING ALL OR ANY CONDITIONS
        conditionType = request.args.get('conditionType')

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
            if conditionType == "all":
                dynamicQuery["$and"].append({ "notes": { "$all": notesChecked }})
            if conditionType == "any":
                dynamicQuery["$and"].append({ "notes": { "$in": notesChecked }})
        if searchInput:
            if searchType == 'brand':
                dynamicQuery["$and"].append({ "brand": searchInput.lower() })
            elif searchType == 'name':
                dynamicQuery["$and"].append({ "name": searchInput.lower() })
        
        # REPLACES BEANS DATA WITH DYNAMIC QUERY IF EXISTS
        if dynamicQuery["$and"]:
            beans = mongo.db.beans.find(dynamicQuery)

    beans = list(beans) # CONVERTS TO LIST BEFORE PASSING INTO TEMPLATE
    context = {
        'beans' : beans,
        'roast_types' : coffeeBeans["roast_types"],
        'origin_types' : coffeeBeans["origin_types"],
        'roastChecked' : roastChecked,
        'originChecked' : originChecked,
        'organicChecked' : organicChecked,
        'notesRelativePercentage' : notesRelativePercentage,
        'notesChecked' : notesChecked,
        'conditionType' : conditionType
    }

    return render_template("browse.html", **context)

def gatherRatings(submissionId):
    submission_data = mongo.db.beans.find_one(
            {"_id": ObjectId(submissionId)})
    
    # LIST CONTAINING ALL RATING NUMBERS OF DISPLAYED SUBMISSION
    ratings = []
    if 'rating' in submission_data:
        for item in submission_data["rating"]:
            ratings.append(int(item["score"]))
    else:
        ratings.append(0)
    
    return ratings

def getAverageRating(submissionId):
    ratings = gatherRatings(submissionId)
    # CALCULATE AVERAGE OF CURRENT SUBMISSIONS RATINGS
    if len(ratings) >= 2:
        averageRating = sum(ratings) / len(ratings)
    elif len(ratings) == 1:
        averageRating = ratings[0]
    else:
        averageRating = 0
    averageRating = round(averageRating)
    return averageRating


def getTotalRatings(submissionId):
    total_ratings = len(gatherRatings(submissionId))
    return total_ratings


@app.route("/view/<submissionId>", methods=["GET", "POST"])
def viewSubmission(submissionId):
    submission_data = mongo.db.beans.find_one(
            {"_id": ObjectId(submissionId)})    
    averageRating = getAverageRating(submissionId)

    if 'review' in submission_data:
        existing_reviews = submission_data["review"]
    else:
        existing_reviews = None

    # ASK USER TO LOGIN IN ORDER TO RATE
    if 'user' not in session:
        if request.method == "POST":
            flash(u"You need to login to rate", "warning")
        return render_template("view_submission.html", submission_data=submission_data, averageRating=averageRating, total_ratings=getTotalRatings(submissionId), existing_reviews=existing_reviews)
    
    # IF USER LOGGED IN
    elif 'user' in session:
        # GET USERID
        currentUserId = mongo.db.users.find_one(
            {"username": session["user"]})["_id"]
        
        # SET DEFAULT USER RATING
        existing_user_rating = 0

        # IF SUBMISSION HAS RATINGS
        if 'rating' in submission_data:
            for item in submission_data["rating"]:
                # IF USER HAS MADE A RATING BEFORE
                if item["user"] == currentUserId:
                    existing_user_rating = int(item["score"])

        if request.method == "POST":
            # IF USER CLICKS ON RATING BUTTON
            if "rating" in request.form:

                # GET USER CLICKED RATING
                rating = request.form['rating']

                if not existing_user_rating > 0:
                    # IF USER HASN'T ALREADY SUBMITTED, PUSH
                    mongo.db.beans.update_one(
                            {"_id": ObjectId(submissionId)},
                            { "$push": {"rating": {"user": currentUserId, "score": int(rating), "username": session["user"]}}}
                    )
                    return redirect(url_for("viewSubmission", submissionId=submissionId))
                else:
                    # IF USER HAS ALREADY SUBMITTED, UPDATE
                    mongo.db.beans.update_one(
                        {"_id" : ObjectId(submissionId), "rating.user" : ObjectId(currentUserId)},
                        {
                            "$set" : {
                                "rating.$.score" : int(rating)
                            }
                        }
                    )
                    return redirect(url_for("viewSubmission", submissionId=submissionId))

            if "review" in request.form:
                print('submit review')
                # GETS USER REVIEW INPUT
                reviewText = request.form['reviewContent']

                # DEFAULT USER REVIEW SET TO NONE
                existing_user_review = None

                # IF SUBMISSION HAS REVIEWS
                if 'review' in submission_data:
                    for item in submission_data["review"]:
                        # IF USER HAS MADE A RATING ALREADY
                        if item["user"] == currentUserId:
                            # REASSIGN VARIABLE TO CONTAIN REVIEW
                            existing_user_review = str(item["text"])
                
                # IF USER HAS ALREADY REVIEWED
                if existing_user_review:
                    print('already reviewed')
                    # UPDATE EXISTING REVIEW FIELD
                    mongo.db.beans.update_one(
                        {"_id" : ObjectId(submissionId), "review.user" : ObjectId(currentUserId)},
                        {
                            "$set" : {
                                "review.$.text" : str(reviewText),
                                "review.$.reviewTimestamp": datetime.datetime.utcnow()
                            }
                        }
                    )
                else:
                    # ADD REVIEW TO MONGODB DOCUMENT
                    print('never reviewed')
                    mongo.db.beans.update_one(
                        {"_id": ObjectId(submissionId)},
                        { "$push": 
                            {"review": 
                                {
                                    "user": currentUserId,
                                    "username": session["user"],
                                    "text": str(reviewText),
                                    "reviewTimestamp": datetime.datetime.utcnow()
                                }
                            }
                        }
                    )

                return redirect(url_for("viewSubmission", submissionId=submissionId))

        return render_template("view_submission.html", submission_data=submission_data, averageRating=averageRating, existing_user_rating=existing_user_rating, total_ratings=getTotalRatings(submissionId), existing_reviews=existing_reviews)

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
            "password": generate_password_hash(request.form.get("inputPassword"))
        }
        mongo.db.users.insert_one(newUser)
        session["user"] = request.form.get("inputUsername").lower()
        flash(u"Registration Successful!", "success")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        userEmailMatch = mongo.db.users.find_one(
            {"email": request.form.get("loginEmail").lower()})
        if userEmailMatch:
            matchedUsername = userEmailMatch["username"]
            # CHECKS IF HASHED PASSWORD MATCHES USER INPUT
            if check_password_hash(userEmailMatch["password"], request.form.get("loginPassword")):
                session["user"] = matchedUsername
                flash(u"Welcome {}".format(userEmailMatch["first_name"].capitalize()), "success")
                return redirect(url_for("profile", username=session["user"]))
            else:
                # INVALID PASSWORD MATCH
                flash(u"Incorrect login details. Please try again.", "warning")
                return redirect(url_for("login"))
        else:
            # INCORRECT EMAIL
            flash(u"Incorrect login details. Please try again.", "warning")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/profile/<username>")
def profile(username):
    users = mongo.db.users.distinct('username') # RETURNS LIST OF USERS IN DATABASE
    if username in users: # IF URL CONTAINS REAL USERNAME
        user_submissions = mongo.db.beans.find({"username": username}) # GETS THEIR SUBMISSIONS
        user_submissions = list(user_submissions)
        submission_count = len(list(user_submissions))
        first_name = mongo.db.users.find_one(
            {"username": username})["first_name"] # GETS THEIR FIRST NAME
        # RENDERS PROFILE PAGE VISISBLE TO ALL
        context = {
            'username' : username,
            'first_name' : first_name,
            'user_submissions' : user_submissions,
            'submission_count' : submission_count
        }
        print(user_submissions)
        return render_template("profile.html", **context)
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
                {"username": session["user"]})["username"]
        }

        # CREATES FULL NAME FROM EXISTING VALUES
        existing_full_name = existingPreferences["first_name"] + " " + existingPreferences["last_name"]

        # IF UPDATE REQUEST IS SENT
        if request.method == "POST":
            # RETRIEVES NEW PREFERENCES
            editedPreferences = {
                "first_name": request.form.get("inputFirstName").lower(),
                "last_name": request.form.get("inputLastName").lower(),
                "email": request.form.get("inputEmail").lower(),
                "username": request.form.get("inputUsername")
            }

            # CREATES FULL NAME FROM EDITED VALUES
            edited_full_name = editedPreferences["first_name"] + " " + editedPreferences["last_name"]

            # FINDS THE USERS UNIQUE ID IDENTIFIER
            userId = mongo.db.users.find_one(
            {"username": session["user"]})["_id"]

            # UPDATE ALL BEANS TO NEW USERNAME
            mongo.db.beans.update_many({"username": session["user"]}, {"$set": {"username": editedPreferences["username"]}})
            # UPDATE ALL BEANS TO NEW FULL NAME
            mongo.db.beans.update_many({"full_name": existing_full_name}, {"$set": {"full_name": edited_full_name}})

            # UPDATE ALL RATINGS TO NEW USERNAME
            mongo.db.beans.update_many(
                {"rating.username" : session["user"]},
                {
                    "$set" : {
                        "rating.$.username" : editedPreferences["username"]
                    }
                }
            )

            # UPDATE ALL REVIEWS TO NEW USERNAME
            mongo.db.beans.update_many(
                {"review.username" : session["user"]},
                {
                    "$set" : {
                        "review.$.username" : editedPreferences["username"]
                    }
                }
            )

            # UPDATES THE USERS COLLECTION WITH NEW VALUES
            mongo.db.users.update_one(
                {"_id": userId},
                {"$set": editedPreferences}
            )

            # UPDATE SESSION TOKEN TO NEW USERNAME VALUE
            session["user"] = editedPreferences["username"]

            # VALIDATES THE UPDATE HAS COMPLETED
            flash(u"Your changes have been saved", "success")
            return redirect(url_for("update_account", username=session["user"]))

        context = {
            'username' : existingPreferences["username"],
            'first_name' : existingPreferences["first_name"],
            'last_name' : existingPreferences["last_name"],
            'email' : existingPreferences["email"]
        }

        return render_template("update_account.html", **context)

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
                submissionsQuery = {"username": loggedInAccount["username"]}
                mongo.db.beans.delete_many(submissionsQuery)
                mongo.db.users.delete_one(loggedInAccount)
                # DELETION VALIDATION
                flash(u"Your account has been permanently deleted", "success")
                session.pop("user") # LOG USER OUT
                return redirect(url_for("index"))
            else:
                # USERNAME IS CORRECT BUT PASSWORD INPUT DID NOT MATCH
                flash(u"You did not enter the correct password. Try again.", "warning")
                return redirect(url_for("delete_account", username=username))
                
    return render_template("delete_account.html", username=username, first_name=first_name)

@app.route("/logout")
def logout():
    flash(u"You have been logged out", "success")
    session.pop("user")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)
