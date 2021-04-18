import os
import sys
import random
from datetime import datetime, timezone
import math
import base64
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

def getCoffeeData():
    coffeeData = {
        "roast_types": ["dark", "medium", "light"],
        "origin_types": dynamicValues(["brazil", "ethiopia", "blend", "colombia"], mongo.db.beans.distinct('origin')),
        "brand_names": dynamicValues(["union", "monmouth", "starbucks"], mongo.db.beans.distinct('brand')),
        "unique_notes": dynamicValues(["caramel", "prune", "cherry"], mongo.db.beans.distinct('notes')),
        "coffeeImg": "/static/assets/default_submission_img.png"
    }
    return coffeeData

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403

@app.route("/", methods=["GET", "POST"])
def index():
    # GETS MOST RECENT SUBMISSION 
    recentSubmission = mongo.db.beans.find_one(
        {}, sort=[( '_id', -1 )]
        )
    
    # CONTAINS DOC ID, AVERAGE RATING AND NUMBER OF RATINGS
    averages = []
    # COLLECTION CONTAINING ALL DOCUMENTS WITH RATINGS
    ratingsTrue = mongo.db.beans.find( { "rating": { "$exists": True } } )

    # LOOPS THROUGH COLLECTION AND APPENDS TO AVERAGES LIST
    for doc in list(ratingsTrue):
        averages.append((doc['_id'], getAverageRating(doc['_id']), len(gatherRatings(doc['_id']))))

    # SORTS BY AVERAGE RATING THEN BY QUANTITY OF RATINGS
    sortedAverages = sorted(averages, key=lambda average: (average[1], average[2]), reverse=True)
    # GETS TOP 5
    top5tuples = sortedAverages[:5]
    # CONTAINS FULL DOC DATA AND AVERAGE DATA
    top5docs = []
    for submission in top5tuples:
        top5docs.append((submission, mongo.db.beans.find_one(
            {"_id": ObjectId(submission[0])}) ))


    # COLLECTION CONTAINING ALL DOCUMENTS WITH REVIEWS
    reviewsTrue = mongo.db.beans.find( { "review": { "$exists": True } } )
    # CONTAINS DOC DATA AND REVIEWS
    reviewsCollection = []
    for doc in list(reviewsTrue):
        reviews = []
        for review in doc['review']:
            reviews.append(review)
        reviewsCollection.append((doc['_id'], doc['brand'], doc['name'], doc['roast'], reviews))

    # CONTAINS INDIVIDUAL TIMESTAMPS WITH DOC DATA
    reviewTimestamps = []
    for item in reviewsCollection:
        for timestamp in item[4]:
            reviewTimestamps.append((item[0], item[1], item[2], item[3], timestamp))
    # SORTS BY TIMESTAMP DATE
    sortedTimestamps = sorted(reviewTimestamps, key=lambda timestamp: timestamp[4]['reviewTimestamp'], reverse=True)
    # CONVERTS UTC TIME TO USER LOCAL TIMEZONE
    for x in sortedTimestamps:
        x[4]['reviewTimestamp'] = utcToLocal(x[4]['reviewTimestamp'])
    recentReviews = sortedTimestamps[:3]

    if request.method == "POST":
        searchCriteria = request.form["searchCriteria"]
        return redirect(url_for('browse', searchCriteria=searchCriteria))

    return render_template("index.html", recentSubmission=recentSubmission, top5docs=top5docs, recentReviews=recentReviews)

def encode64(file):
    image_string = base64.b64encode(file.read())
    return image_string.decode('utf8')

def gatherInputs(matchedBean = None):
    # HOLDS LIST OF NOTES FROM DATABASE
    captureNotes = []
    # GRABS NOTES INPUT AND TRANSFORMS TO LOWERCASE
    for note in request.form.getlist('note'):
        # APPENDS TO NOTES LIST
        captureNotes.append(note.lower())
    # CAPTURES USER INPUT DATA
    userInput = {
        "brand": request.form["brand"].lower(),
        "name": request.form["name"].lower(),
        "roast": request.form["roast"],
        "origin": request.form["origin"].lower(),
        "notes": captureNotes,
        "organic": bool(request.form.get("organic")),
        "url": request.form["website"],
        "img-base64": encode64(request.files['upload64']) if request.files['upload64'] else matchedBean["img-base64"],
        "username": mongo.db.users.find_one(
            {"username": session["user"]})["username"]
    }

    return userInput


@app.route("/add", methods=["GET", "POST"])
def add():
    form_type = "addCoffee"
    full_name = mongo.db.users.find_one(
        {"username": session["user"]})["first_name"] + " " + mongo.db.users.find_one(
        {"username": session["user"]})["last_name"]

    context = {
            'form_type' : form_type,
            'coffeeImg' : getCoffeeData()["coffeeImg"],
            'roast_types' : getCoffeeData()["roast_types"],
            'origin_types' : getCoffeeData()["origin_types"],
            'uniqueNotes' : getCoffeeData()["unique_notes"],
            'brand_names' : getCoffeeData()["brand_names"],
            'full_name' : full_name
    }

    if request.method == "POST":

        inputDictionary = gatherInputs()
        inputDictionary["full_name"] = full_name
    
        if mongo.db.beans.find_one(
            {"name": inputDictionary["name"]}):
            flash(u"A coffee with this name already exists.", "warning")
            return redirect(url_for("add"))
        else:
            insertSubmission = mongo.db.beans.insert_one(inputDictionary)
            flash(u"Your submission has been added.", "added")
            return redirect(url_for("viewSubmission", submissionId=insertSubmission.inserted_id))

    return render_template("add.html", **context)


@app.route("/edit/<beanId>", methods=["GET", "POST"])
def edit(beanId):
    matchedBean = mongo.db.beans.find_one(
            {"_id": ObjectId(beanId)})
    submissionImg = matchedBean["img-base64"]
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
        if "editCoffee" in request.form:  

            mongo.db.beans.update_one(
                {"_id": ObjectId(beanId)},
                {"$set": gatherInputs(matchedBean)}
            )

            flash(u"Your submission has been edited.", "added")
            return redirect(url_for("viewSubmission", submissionId=beanId))
        
        if "deleteCoffee" in request.form:
            mongo.db.beans.delete_one(
                {"_id": ObjectId(beanId)}
            )
            flash(u"Your submission has been deleted.", "success")
            return redirect(url_for("profile", username=session["user"]))
        

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
            'coffeeImg' : getCoffeeData()["coffeeImg"],
            'roast_types' : getCoffeeData()["roast_types"],
            'origin_types' : getCoffeeData()["origin_types"],
            'uniqueNotes' : getCoffeeData()["unique_notes"],
            'brand_names' : getCoffeeData()["brand_names"],
            'full_name' : full_name
        }
        return render_template("edit.html", **context)


# CREATES DICTIONARY OF UNIQUE ITEMS AND THEIR OCCURANCE PERCENTAGE
def wordCloud(list, uniqueList):

    # CREATES TUPLE WITH UNIQUE ITEM AND ITS NUMBER OF OCCURANCES
    itemCount = []
    for x in uniqueList:
        itemCount.append((x, list.count(x)))
    itemCount = sorted(itemCount, key=lambda item: item[1], reverse=True)

    itemPercentage = {}
    for item in itemCount:
        length = len(uniqueList) # RETURNS NUMBER OF NOTES
        occurance = item[1] # RETURNS HOW MANY TIMES NOTES OCCUR
        percentage = occurance / length * 100 # DIVIDES TOTAL NUMBER OF NOTES BY OCCURANCE 
        itemPercentage[item] = percentage # ADDS TO DICTIONARY

    most_common_item = max(itemPercentage, key=itemPercentage.get) # SOURCE: https://stackoverflow.com/a/14091645
    most_common_percentage = itemPercentage.get(most_common_item) # HIGHEST PERCENTAGE
    

    itemPercentageDict = {}
    for num in itemPercentage:
        percentage = itemPercentage.get(num) / most_common_percentage * 100 # DIVIDES PERCENTAGE BY THE HIGHEST PERCENTAGE
        itemPercentageDict[num] = round(percentage, 1) # ROUNDS IT DOWN <<< OLD
    
    newItemPercentageList = []
    for key, value in itemPercentageDict.items():
        newItemPercentageList.append((key[0], value))

    return newItemPercentageList

# CREATES OFFSET AMOUNT BASED ON SPECIFIED QUANTITY SHOWN PER PAGE
def pagination(perPage, dataCount):
    page = 1
    offset = 0
    pageQuantity = math.ceil(dataCount / perPage)
    if 'page' in request.args:
        page = int(request.args.get("page"))
        multiply = page - 1
        offset = multiply * perPage
    return offset, perPage, page, dataCount, pageQuantity

@app.route("/browse", methods=["GET"])
def browse():
    # GETS ALL DATA FROM BEANS COLLECTION (SORTED BY MOST RECENT)
    data = mongo.db.beans.find().sort("_id", -1)

    # RUNS PAGINATION FUNCTION TO GET VARIABLES
    offset, perPage, page, beansCount, pageQuantity = pagination(6, mongo.db.beans.count_documents({}))

    # USES PAGINATION VARIABLES TO ASSIGN OFFSET AND NUMBER PER PAGE
    beans = data.skip(offset).limit(perPage)

    # RETURNS LIST OF ALL NON-UNIQUE NOTES IN DB
    notes = mongo.db.beans.find({}, {"notes" : 1})

    # RETURNS LIST OF ALL UNIQUE NOTES
    uniqueNotes = getCoffeeData()["unique_notes"]
    
    notesRelativePercentages = None

    # IF BEANS COLLECTION HAS DOCUMENTS
    if mongo.db.beans.count_documents({}):
        # CREATE DICTIONARY FOR WORD CLOUD
        notesCollection = list(notes) # CONVERTS NON-UNIQUE LIST OF NOTES INTO LIST
        notesList = [y for x in notesCollection for y in x['notes']] # UNPACKS LIST INTO LIST OF JUST NOTES VALUES
        
        notesRelativePercentages = wordCloud(notesList, list(uniqueNotes))


    # SET DEFAULT HEADER FOR BROWSE
    browseHeader = "Results"

    # DYNAMICALLY CREATES A FIND QUERY
    # ADAPTED FROM https://stackoverflow.com/questions/65823199/dynamic-mongo-query-with-python
    dynamicQuery = {}
    dynamicQuery["$and"]=[]

    # GETS USER INPUT DATA AND APPENDS IT TO LISTS
    if request.method == "GET":

        # SETS DEFAULT SEARCH VALUE AS NONE
        searchInput = None
        # GETS SEARCH INPUT VALUE FROM INDEX REDIRECT IF EXISTS
        # SOURCE https://stackoverflow.com/questions/55447599/how-to-send-data-in-flask-to-another-page
        if request.args.get('indexSearchQuery'):
            searchInput = request.args.get('indexSearchQuery')
        # GETS SEARCH INPUT VALUE FROM BROWSE PAGE FORM IF EXISTS
        elif request.args.get("searchCriteria"):
            searchInput = request.args.get("searchCriteria")

       
        # CHECKS IF LIST VALUES EXIST AND APPENDS TO DYNAMIC QUERY
        if request.args.getlist("roast"):
            dynamicQuery["$and"].append({ "roast": { "$in": request.args.getlist("roast") }} )
        if request.args.getlist("origin"):
            dynamicQuery["$and"].append({ "origin": { "$in": request.args.getlist("origin") }} )
        if bool(request.args.getlist("organicRequired")):
            dynamicQuery["$and"].append({ "organic": True })
        if request.args.getlist('tag'):
            if request.args['conditionType'] == "all":
                dynamicQuery["$and"].append({ "notes": { "$all": request.args.getlist('tag') }})
            if request.args['conditionType'] == "any":
                dynamicQuery["$and"].append({ "notes": { "$in": request.args.getlist('tag') }})
        # IF SEARCH INPUT HAS VALUE
        if searchInput:
            # SEARCH DATABASE FOR VALUE IN 'BRAND' OR 'NAME' KEYS
            dynamicQuery["$and"].append({"$or":[{"brand": searchInput.lower() }, {"name": searchInput.lower()}]})

        # REPLACES BEANS DATA WITH DYNAMIC QUERY IF EXISTS
        if dynamicQuery["$and"]:
            findQuery = mongo.db.beans.find(dynamicQuery).sort("_id", -1).skip(offset).limit(perPage)
            # REASSIGNS VALUES TO PAGINATION VARIABLES
            offset, perPage, page, beansCount, pageQuantity = pagination(6, mongo.db.beans.count_documents(dynamicQuery))
            # REASSIGNS BEANS VARIABLE TO INCLUDE QUERY AND PAGINATION OFFSET/LIMIT
            beans = mongo.db.beans.find(dynamicQuery).sort("_id", -1).skip(offset).limit(perPage)

    # IF CUSTOM FILTER QUERY, CHANGE HEADER
    if dynamicQuery["$and"]:
            browseHeader = "Filtered results"

    beans = list(beans) # CONVERTS TO LIST BEFORE PASSING INTO TEMPLATE
    context = {
        'beans' : beans,
        'roast_types' : getCoffeeData()["roast_types"],
        'origin_types' : getCoffeeData()["origin_types"],
        'notesRelativePercentages' : notesRelativePercentages,
        'page_variable' : page,
        'beansCount' : beansCount,
        'pageQuantity' : pageQuantity,
        'browseHeader' : browseHeader,
        'offset' : offset
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
    averageRating = round(averageRating, 1)
    return averageRating


def getTotalRatings(submissionId):
    total_ratings = len(gatherRatings(submissionId))
    return total_ratings


@app.route("/view/<submissionId>", methods=["GET", "POST"])
def viewSubmission(submissionId):
    submission_data = mongo.db.beans.find_one(
            {"_id": ObjectId(submissionId)})    
    # CONVERTS TIMESTAMP TO USER TIMEZONE
    if 'review' in submission_data:
        for doc in submission_data['review']:
            doc['reviewTimestamp'] = utcToLocal(doc['reviewTimestamp'])

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
                    # UPDATE EXISTING REVIEW FIELD
                    mongo.db.beans.update_one(
                        {"_id" : ObjectId(submissionId), "review.user" : ObjectId(currentUserId)},
                        {
                            "$set" : {
                                "review.$.text" : str(reviewText),
                                "review.$.reviewTimestamp": datetime.utcnow()
                            }
                        }
                    )
                else:
                    # ADD REVIEW TO MONGODB DOCUMENT
                    mongo.db.beans.update_one(
                        {"_id": ObjectId(submissionId)},
                        { "$push": 
                            {"review": 
                                {
                                    "user": currentUserId,
                                    "username": session["user"],
                                    "text": str(reviewText),
                                    "reviewTimestamp": datetime.utcnow()
                                }
                            }
                        }
                    )

                return redirect(url_for("viewSubmission", submissionId=submissionId))

        return render_template("view_submission.html", submission_data=submission_data, averageRating=averageRating, existing_user_rating=existing_user_rating, total_ratings=getTotalRatings(submissionId), existing_reviews=existing_reviews)

# SOURCE: https://stackoverflow.com/questions/4563272/convert-a-python-utc-datetime-to-a-local-datetime-using-only-python-standard-lib
def utcToLocal(utc):
    return utc.replace(tzinfo=timezone.utc).astimezone(tz=None)

@app.route("/reviews/<submissionId>", methods=["GET"])
def allReviews(submissionId):
    data = mongo.db.beans.find_one({"_id": ObjectId(submissionId)})

    # CREATES FLAT LIST CONTAING REVIEW AND RATING DATA
    feedback = []
    for item in data['review']:
        feedback.append(item)
        for rating in data['rating']:
            if rating['user'] == item['user']:
                index = feedback.index(item)
                feedback[index]['rating'] = rating

    # CONVERTS TIMESTAMP TO USER TIMEZONE
    for x in feedback:
        x['reviewTimestamp'] = utcToLocal(x['reviewTimestamp'])
    
    # SETS DEFAULT SORT ORDER OF MOST RECENT
    # LAMBDA SOURCE: https://docs.python.org/3/howto/sorting.html
    submission_data = sorted(feedback, key=lambda timestamp: timestamp['reviewTimestamp'], reverse=True)

    if request.method == "GET":
        if request.args.get("sort") == 'dateDesc': # Recent
            submission_data = sorted(feedback, key=lambda timestamp: timestamp['reviewTimestamp'], reverse=True)
        elif request.args.get("sort") == 'dateAsc': # Oldest
            submission_data = sorted(feedback, key=lambda timestamp: timestamp['reviewTimestamp'], reverse=False)
        elif request.args.get("sort") == 'ratingDesc': # High > Low
            submission_data = sorted(feedback, key=lambda score: score['rating']['score'], reverse=True)
        elif request.args.get("sort") == 'ratingAsc': # Low > High
            submission_data = sorted(feedback, key=lambda score: score['rating']['score'], reverse=False)

    return render_template("all_reviews.html", submission_data=submission_data, submissionId=submissionId)



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
        # user_submissions = mongo.db.beans.find({"username": username}).sort("_id", -1) # GETS THEIR SUBMISSIONS
        data = mongo.db.beans.find({"username": username}).sort("_id", -1)
        offset, perPage, page, beansCount, pageQuantity = pagination(6, mongo.db.beans.count_documents({"username": username}))
        user_submissions = data.skip(offset).limit(perPage)

        user_submissions = list(user_submissions)
        submission_count = len(list(user_submissions))
        first_name = mongo.db.users.find_one(
            {"username": username})["first_name"] # GETS THEIR FIRST NAME
        # RENDERS PROFILE PAGE VISISBLE TO ALL
        context = {
            'username' : username,
            'first_name' : first_name,
            'user_submissions' : user_submissions,
            'submission_count' : submission_count,
            'offset' : offset,
            'perPage' : perPage,
            'page_variable' : page,
            'beansCount' : beansCount,
            'pageQuantity' : pageQuantity
        }

        return render_template("profile.html", **context)
    else:
        # REDIRECTS TO HOMEPAGE IS URL USERNAME DOESN'T EXIST IN DATABASE
        return redirect(url_for("index"))


@app.route("/profile/<username>/update_account", methods=["GET", "POST"])
def update_account(username):
    # IF USER ISN'T LOGGED IN OR NOT LOGGED IN AS USER OF PROFILE BEING VIEWED
    if "user" not in session or session["user"] != username:
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

    if request.method == "POST":
        if "deleteUser" in request.form:
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
