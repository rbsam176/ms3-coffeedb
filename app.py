import os
import random
from datetime import datetime, timezone
import math
import json
import re
from imagekitio.client import ImageKit
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for, jsonify)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

# IMAGEKIT AUTH
imagekit = ImageKit(
    private_key=os.environ.get("IMAGEKIT_PRIVATE"),
    public_key=os.environ.get("IMAGEKIT_PUBLIC"),
    url_endpoint=os.environ.get("IMAGEKIT_ENDPOINT")
)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    # GATHER DATA TO BE PASSED TO FRONTEND
    values = {
        "brands": list(getCoffeeData()['brand_names']),
        "names": list(mongo.db.beans.distinct('name')),
        "origins": list(getCoffeeData()['origin_types']),
        "notes": list(getCoffeeData()['unique_notes'])
    }
    # CONVERT LIST TO JSON
    json_values = json.dumps(values)
    # SEND TO TEMPLATE
    return jsonify(autocomplete_values=json_values)


def dynamicValues(fixed, databaseKey):
    combinedList = [fixed] + [databaseKey]
    removeDuplicates = set().union(*combinedList)
    return removeDuplicates


def getCoffeeData():
    origins = dynamicValues(["brazil", "ethiopia", "blend", "colombia"],
                            mongo.db.beans.distinct('origin'))

    coffeeData = {
        "roast_types": ["dark", "medium", "light"],
        "origin_types": dynamicValues(
            ["brazil", "ethiopia", "blend", "colombia"],
            mongo.db.beans.distinct('origin')),
        "brand_names": dynamicValues(
            ["union", "monmouth", "starbucks"],
            mongo.db.beans.distinct('brand')),
        "unique_notes": dynamicValues(
            ["caramel", "prune", "cherry"],
            mongo.db.beans.distinct('notes')),
        "coffeeImg": "/static/assets/default_submission_img.png"
    }
    return coffeeData


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/", methods=["GET", "POST"])
def index():
    # GETS MOST RECENT SUBMISSION
    recentSubmission = mongo.db.beans.find_one(
        {}, sort=[('_id', -1)]
        )

    # # CONTAINS DOC ID, AVERAGE RATING AND NUMBER OF RATINGS
    averages = []
    # # COLLECTION CONTAINING ALL DOCUMENTS WITH RATINGS
    ratingsTrue = mongo.db.beans.find(
                                     {"rating": {"$exists": True}},
                                     projection={
                                                 "rating": 1, "brand": 1,
                                                 "name": 1})

    # LOOPS THROUGH COLLECTION AND APPENDS TO AVERAGES LIST
    for doc in list(ratingsTrue):
        averages.append((doc['_id'], getAverageRating(doc['_id']),
                        len(gatherRatings(doc['_id']))))

    # SORTS BY AVERAGE RATING THEN BY QUANTITY OF RATINGS
    sortedAverages = sorted(averages, key=lambda average:
                            (average[1], average[2]), reverse=True)
    # GETS TOP 5
    top5tuples = sortedAverages[:5]
    # CONTAINS FULL DOC DATA AND AVERAGE DATA
    top5docs = []
    for submission in top5tuples:
        top5docs.append((submission, mongo.db.beans.find_one(
            {"_id": ObjectId(submission[0])}, projection={
                "rating": 1, "brand": 1, "name": 1})))

    # COLLECTION CONTAINING ALL DOCUMENTS WITH REVIEWS
    reviewsTrue = mongo.db.beans.find({"review": {
        "$exists": True}}, projection={
        "review": 1, "brand": 1, "name": 1, "roast": 1})

    # CONTAINS DOC DATA AND REVIEWS
    reviewsCollection = []
    for doc in list(reviewsTrue):
        reviews = []
        for review in doc['review']:
            reviews.append(review)
        reviewsCollection.append((doc['_id'], doc['brand'], doc['name'],
                                 doc['roast'], reviews))

    # CONTAINS INDIVIDUAL TIMESTAMPS WITH DOC DATA
    reviewTimestamps = []
    for item in reviewsCollection:
        for timestamp in item[4]:
            reviewTimestamps.append((item[0], item[1], item[2], item[3],
                                    timestamp))
    # SORTS BY TIMESTAMP DATE
    sortedTimestamps = sorted(reviewTimestamps, key=lambda timestamp:
                              timestamp[4]['reviewTimestamp'], reverse=True)
    # CONVERTS UTC TIME TO USER LOCAL TIMEZONE
    for x in sortedTimestamps:
        x[4]['reviewTimestamp'] = utcToLocal(x[4]['reviewTimestamp'])
    recentReviews = sortedTimestamps[:3]

    if request.method == "POST":
        searchCriteria = request.form["searchCriteria"]
        return redirect(url_for('browse', searchCriteria=searchCriteria))

    return render_template("index.html", recentSubmission=recentSubmission,
                           top5docs=top5docs, recentReviews=recentReviews)


def gatherInputs(matchedBean=None):
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
        "organic": True if "True" in request.form.getlist('organicRequired')
        else False,
        "url": request.form["website"],
        "img-url": uploadImage(request.files['uploadImg'])['response']['url'],
        "username": mongo.db.users.find_one(
            {"username": session["user"]})["username"]
    }
    return userInput


def uploadImage(image):
    imagekitUpload = imagekit.upload_file(
        file=image,
        file_name=image.filename,
        options={
            "is_private_file": False,
        },
    )
    return imagekitUpload


@app.route("/add", methods=["GET", "POST"])
def add():
    # IF USER IS LOGGED IN
    if "user" in session:
        form_type = "addCoffee"
        first_name = mongo.db.users.find_one(
            {"username": session["user"]})["first_name"]
        last_name = mongo.db.users.find_one(
                {"username": session["user"]})["last_name"]
        full_name = first_name + " " + last_name

        context = {
                'form_type': form_type,
                'coffeeImg': getCoffeeData()["coffeeImg"],
                'roast_types': getCoffeeData()["roast_types"],
                'origin_types': getCoffeeData()["origin_types"],
                'uniqueNotes': getCoffeeData()["unique_notes"],
                'brand_names': getCoffeeData()["brand_names"],
                'full_name': full_name
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
                return redirect(url_for("viewSubmission",
                                submissionId=insertSubmission.inserted_id))

        return render_template("add.html", **context)
    # IF USER NOT LOGGED IN, REDIRECT
    else:
        return redirect(url_for("signup"))


@app.route("/edit/<beanId>", methods=["GET", "POST"])
def edit(beanId):
    matchedBean = mongo.db.beans.find_one(
            {"_id": ObjectId(beanId)})
    # IF USER LOGGED IN IS USER OF SUBMISSION
    if session["user"] == matchedBean["username"]:
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

        context = {
            'form_type': form_type,
            'notes_input': notes_input,
            'url_input': url_input,
            'organic_choice': organic_choice,
            'origin_choice': origin_choice,
            'roast_choice': roast_choice,
            'coffee_name': coffee_name,
            'brand_choice': brand_choice,
            'submissionImg': submissionImg,
            'coffeeImg': getCoffeeData()["coffeeImg"],
            'roast_types': getCoffeeData()["roast_types"],
            'origin_types': getCoffeeData()["origin_types"],
            'uniqueNotes': getCoffeeData()["unique_notes"],
            'brand_names': getCoffeeData()["brand_names"],
            'full_name': full_name
        }
        return render_template("edit.html", **context)

    # IF USER IS NOT SUBMISSION USER THEN REDIRECT TO VIEW SUBMISSION
    else:
        return redirect(url_for("viewSubmission", submissionId=beanId))


def countOccurances(nonUniqueList, uniqueList):
    itemCount = []
    for x in uniqueList:
        itemCount.append((x, nonUniqueList.count(x)))
    itemCount = sorted(itemCount, key=lambda item: item[1], reverse=True)

    return itemCount


# CREATES DICTIONARY OF UNIQUE ITEMS AND THEIR OCCURANCE PERCENTAGE
def wordCloud(list, uniqueList):

    # CREATES TUPLE WITH UNIQUE ITEM AND ITS NUMBER OF OCCURANCES
    itemCount = []
    for x in uniqueList:
        itemCount.append((x, list.count(x)))
    itemCount = sorted(itemCount, key=lambda item: item[1], reverse=True)

    itemPercentage = {}
    for item in itemCount:
        # RETURNS NUMBER OF NOTES
        length = len(uniqueList)
        # RETURNS HOW MANY TIMES NOTES OCCUR
        occurance = item[1]
        # DIVIDES TOTAL NUMBER OF NOTES BY OCCURANCE
        percentage = occurance / length * 100
        # ADDS TO DICTIONARY
        itemPercentage[item] = percentage

    # SOURCE: https://stackoverflow.com/a/14091645
    most_common_item = max(itemPercentage, key=itemPercentage.get)
    # HIGHEST PERCENTAGE
    most_common_percentage = itemPercentage.get(most_common_item)

    itemPercentageDict = {}
    for num in itemPercentage:
        # DIVIDES PERCENTAGE BY THE HIGHEST PERCENTAGE
        percentage = itemPercentage.get(num) / most_common_percentage * 100
        # ROUNDS IT DOWN <<< OLD
        itemPercentageDict[num] = round(percentage, 1)
    itemPercentageList = []
    for key, value in itemPercentageDict.items():
        itemPercentageList.append((key[0], value))

    itemPercentagesSplit = []
    for index, item in enumerate(itemPercentageList):
        if index >= 10:
            itemPercentagesSplit.append((item[0], item[1], "extra-note"))
        else:
            itemPercentagesSplit.append(item)

    return itemPercentagesSplit


# CREATES OFFSET AMOUNT BASED ON SPECIFIED QUANTITY SHOWN PER PAGE
def pagination(perPage, dataCount):
    page = 1
    offset = 0
    pageQuantity = math.ceil(dataCount / perPage)
    if 'page' in request.args:
        page = int(request.args.get("page"))
        currentPage = page - 1
        offset = currentPage * perPage
    return offset, perPage, page, dataCount, pageQuantity


def pagination_sort(beans):
    # New > old
    if request.args.get("sort") == 'dateDesc':
        beans = beans.sort("_id", -1)
    # Old > new
    if request.args.get("sort") == 'dateAsc':
        beans = beans.sort("_id", 1)
    # A > Z name
    if request.args.get("sort") == 'nameAz':
        beans = beans.sort("name", 1)
    # Z > A name
    if request.args.get("sort") == 'nameZa':
        beans = beans.sort("name", -1)
    # A > Z brand
    if request.args.get("sort") == 'brandAz':
        beans = beans.sort("brand", 1)
    # Z > A brand
    if request.args.get("sort") == 'brandZa':
        beans = beans.sort("brand", -1)


@app.route("/browse", methods=["GET"])
def browse():
    # RETURNS NUMBER OF DOCUMENTS IN BEANS COLLECTION
    count = mongo.db.beans.count_documents({})

    # RUNS PAGINATION FUNCTION TO GET VARIABLES
    offset, perPage, page, beansCount, pageQuantity = pagination(6, count)

    # USES PAGINATION VARIABLES TO ASSIGN OFFSET AND NUMBER PER PAGE
    beans = mongo.db.beans.find().sort("_id", -1).skip(offset).limit(perPage)

    # RETURNS LIST OF ALL NON-UNIQUE NOTES IN DB
    notes = mongo.db.beans.find({}, projection={"notes": 1})

    # RETURNS LIST OF ALL UNIQUE NOTES
    uniqueNotes = getCoffeeData()["unique_notes"]

    # RETURNS LIST OF ALL NON-UNIQUE ORIGINS IN DB
    originColl = mongo.db.beans.find({}, projection={"origin": 1})

    origins = []
    for doc in originColl:
        origins.append(doc['origin'])

    # RETURNS LIST OF ALL UNIQUE ORIGINS
    uniqueOrigins = getCoffeeData()["origin_types"]

    notesRelativePercentages = None

    # IF BEANS COLLECTION HAS DOCUMENTS
    if mongo.db.beans.count_documents({}):
        # CREATE DICTIONARY FOR WORD CLOUD
        notesCollection = list(notes)
        # UNPACKS LIST INTO LIST OF JUST NOTES VALUES
        notesList = [y for x in notesCollection for y in x['notes']]

        notesRelativePercentages = wordCloud(notesList, list(uniqueNotes))
        originsOccurances = countOccurances(origins, uniqueOrigins)

    # SET DEFAULT HEADER FOR BROWSE
    browseHeader = "All results"

    # DYNAMICALLY CREATES A FIND QUERY
    # ADAPTED FROM:
    # https://stackoverflow.com/questions/65823199/dynamic-mongo-query-with-python
    dynamicQuery = {}
    dynamicQuery["$and"] = []

    # GETS USER INPUT DATA AND APPENDS IT TO LISTS
    if request.method == "GET":

        # SETS DEFAULT SEARCH VALUE AS NONE
        searchInput = None
        # GETS SEARCH INPUT VALUE FROM INDEX REDIRECT IF EXISTS
        # SOURCE:
        # https://stackoverflow.com/questions/55447599/how-to-send-data-in-flask-to-another-page
        if request.args.get('indexSearchQuery'):
            searchInput = request.args.get('indexSearchQuery')
        # GETS SEARCH INPUT VALUE FROM BROWSE PAGE FORM IF EXISTS
        elif request.args.get("searchCriteria"):
            searchInput = request.args.get("searchCriteria")

        # CHECKS IF LIST VALUES EXIST AND APPENDS TO DYNAMIC QUERY
        if request.args.getlist("roast"):
            dynamicQuery["$and"].append({"roast": {"$in":
                                        request.args.getlist("roast")}})
        if request.args.getlist("origin"):
            dynamicQuery["$and"].append({"origin": {"$in":
                                        request.args.getlist("origin")}})
        if "True" in request.args.getlist('organicRequired'):
            dynamicQuery["$and"].append({"organic": True})
        if request.args.getlist('tag'):
            if request.args['conditionType'] == "all":
                dynamicQuery["$and"].append({"notes": {"$all":
                                            request.args.getlist('tag')}})
            if request.args['conditionType'] == "any":
                dynamicQuery["$and"].append({"notes": {"$in":
                                            request.args.getlist('tag')}})
        # IF SEARCH INPUT HAS VALUE
        if searchInput:
            # SEARCH DATABASE FOR VALUE IN 'BRAND' OR 'NAME' KEYS
            dynamicQuery["$and"].append(
                {"$or": [{"brand": searchInput.lower()},
                         {"name": searchInput.lower()}]}
            )

        # REPLACES BEANS DATA WITH DYNAMIC QUERY IF EXISTS
        if dynamicQuery["$and"]:

            # REASSIGNS VALUES TO PAGINATION VARIABLES
            offset, perPage, page, beansCount, pageQuantity = pagination(
                6, mongo.db.beans.count_documents(dynamicQuery))

            # REASSIGNS BEANS VARIABLE TO INCLUDE QUERY
            # AND PAGINATION OFFSET/LIMIT
            beans = mongo.db.beans.find(
                dynamicQuery).sort("_id", -1).skip(offset).limit(perPage)

        pagination_sort(beans)

    # IF CUSTOM FILTER QUERY, CHANGE HEADER
    if dynamicQuery["$and"]:
            browseHeader = "Filtered results"

    # SOURCE
    # https://stackoverflow.com/questions/17649875/why-does-random-shuffle-return-none
    shuffledNotes = random.sample(
        notesRelativePercentages, len(notesRelativePercentages))

    # CONVERTS TO LIST BEFORE PASSING INTO TEMPLATE
    beans = list(beans)
    context = {
        'beans': beans,
        'roast_types': getCoffeeData()["roast_types"],
        'originsOccurances': originsOccurances,
        'shuffledNotes': shuffledNotes,
        'page_variable': page,
        'beansCount': beansCount,
        'pageQuantity': pageQuantity,
        'browseHeader': browseHeader,
        'offset': offset
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

    # DEFAULT USER REVIEW SET TO NONE
    existing_user_review = None

    # ASK USER TO LOGIN IN ORDER TO RATE
    if 'user' not in session:
        if request.method == "POST":
            flash(u"You need to login to rate", "warning")
        context = {
            "submission_data": submission_data,
            "averageRating": averageRating,
            "total_ratings": getTotalRatings(submissionId),
            "existing_reviews": existing_reviews
        }
        return render_template("view_submission.html", **context)

    # IF USER LOGGED IN
    elif 'user' in session:
        # GET USERID
        currentUserId = mongo.db.users.find_one(
            {"username": session["user"]})["_id"]

        # SET DEFAULT USER RATING
        existing_user_rating = 0

        # GETS USERS OWN REVIEW IF EXISTS
        if 'review' in submission_data:
            for item in submission_data["review"]:
                # IF USER HAS MADE A RATING ALREADY
                if item["user"] == currentUserId:
                    # REASSIGN VARIABLE TO CONTAIN REVIEW
                    existing_user_review = str(item["text"])

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
                            {"$push":
                                {"rating":
                                    {"user": currentUserId,
                                        "score": int(rating),
                                        "username": session["user"]}}}
                    )
                    return redirect(url_for("viewSubmission",
                                            submissionId=submissionId))
                else:
                    # IF USER HAS ALREADY SUBMITTED, UPDATE
                    mongo.db.beans.update_one(
                        {"_id": ObjectId(submissionId),
                            "rating.user": ObjectId(currentUserId)},
                        {
                            "$set": {
                                "rating.$.score": int(rating)
                            }
                        }
                    )
                    return redirect(url_for("viewSubmission",
                                            submissionId=submissionId))

            if "review" in request.form:
                # GETS USER REVIEW INPUT
                reviewText = request.form['reviewContent']

                # IF USER HAS ALREADY REVIEWED
                if existing_user_review:
                    # UPDATE EXISTING REVIEW FIELD
                    mongo.db.beans.update_one(
                        {"_id": ObjectId(submissionId),
                            "review.user": ObjectId(currentUserId)},
                        {
                            "$set": {
                                "review.$.text": str(reviewText),
                                "review.$.reviewTimestamp": datetime.utcnow()
                            }
                        }
                    )
                else:
                    # ADD REVIEW TO MONGODB DOCUMENT
                    mongo.db.beans.update_one(
                        {"_id": ObjectId(submissionId)},
                        {"$push":
                            {"review":
                                {
                                    "user": currentUserId,
                                    "username": session["user"],
                                    "text": str(reviewText),
                                    "reviewTimestamp": datetime.utcnow()
                                }}}
                    )

                return redirect(url_for("viewSubmission",
                                        submissionId=submissionId))

        context = {
            "submission_data": submission_data,
            "averageRating": averageRating,
            "existing_user_rating": existing_user_rating,
            "existing_user_review": existing_user_review,
            "total_ratings": getTotalRatings(submissionId),
            "existing_reviews": existing_reviews
        }
        return render_template("view_submission.html", **context)


# SOURCE:
# https://stackoverflow.com/questions/4563272/convert-a-python-utc-datetime-to-a-local-datetime-using-only-python-standard-lib
def utcToLocal(utc):
    return utc.replace(tzinfo=timezone.utc).astimezone(tz=None)


@app.route("/reviews/<submissionId>", methods=["GET"])
def allReviews(submissionId):
    data = mongo.db.beans.find_one({"_id": ObjectId(submissionId)})

    # CREATES FLAT LIST CONTAING REVIEW AND RATING DATA
    feedback = []
    for item in data['review']:
        feedback.append(item)
        if 'rating' in data:
            for rating in data['rating']:
                if rating['user'] == item['user']:
                    index = feedback.index(item)
                    feedback[index]['rating'] = rating

    # CONVERTS TIMESTAMP TO USER TIMEZONE
    for x in feedback:
        x['reviewTimestamp'] = utcToLocal(x['reviewTimestamp'])

    # SETS DEFAULT SORT ORDER OF MOST RECENT
    # LAMBDA SOURCE: https://docs.python.org/3/howto/sorting.html
    submission_data = sorted(
        feedback, key=lambda timestamp:
            timestamp['reviewTimestamp'], reverse=True)

    if request.method == "GET":
        # Recent > old
        if request.args.get("sort") == 'dateDesc':
            submission_data = sorted(
                                    feedback, key=lambda timestamp:
                                    timestamp['reviewTimestamp'],
                                    reverse=True)
        # Old > new
        elif request.args.get("sort") == 'dateAsc':
            submission_data = sorted(
                feedback, key=lambda timestamp:
                timestamp['reviewTimestamp'],
                reverse=False)
        # High > Low
        elif request.args.get("sort") == 'ratingDesc':
            submission_data = sorted(feedback,
                                     key=lambda score:
                                     score['rating']['score'],
                                     reverse=True)
        # Low > High
        elif request.args.get("sort") == 'ratingAsc':
            submission_data = sorted(feedback,
                                     key=lambda score:
                                     score['rating']['score'],
                                     reverse=False)

    return render_template("all_reviews.html",
                           submission_data=submission_data,
                           submissionId=submissionId)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    # SOURCE:
    # https://stackoverflow.com/questions/19605150/regex-for-password-must-contain-at-least-eight-characters-at-least-one-number-a
    regexBase = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"
    regexNoSymbol = "[a-zA-Z\d]{8,}$"
    regexSymbol = "(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    regexPlain = regexBase + regexNoSymbol
    regexSpecial = regexBase + regexSymbol

    # IF USER IS NOT LOGGED IN ALREADY
    if "user" not in session:
        if request.method == "POST":
            existing_user_email = mongo.db.users.find_one(
                {"email": request.form.get("inputEmail").lower()})
            existing_user_username = mongo.db.users.find_one(
                {"username": request.form.get("inputUsername").lower()})

            if existing_user_email:
                flash(u"An account with this email already exists", "warning")
                return redirect(url_for("signup"))
            if existing_user_username:
                flash(u"An account with this username already exists",
                      "warning")
                return redirect(url_for("signup"))
            newUser = {
                "first_name": request.form.get("inputFirstName").lower(),
                "last_name": request.form.get("inputLastName").lower(),
                "email": request.form.get("inputEmail").lower(),
                "username": request.form.get("inputUsername").lower(),
                "password": generate_password_hash(
                    request.form.get("inputPassword"))
            }

            regexSpecialCheck = re.search(
                regexSpecial, request.form.get("inputPassword"))
            regexPlainCheck = re.search(
                regexPlain, request.form.get("inputPassword"))

            # IF PASSWORD MEETS CRITERIA
            if regexPlainCheck or regexSpecialCheck:
                mongo.db.users.insert_one(newUser)
                # SET SESSION TOKEN
                session["user"] = request.form.get("inputUsername").lower()
                flash(u"Registration Successful!", "success")
                return redirect(url_for("profile", username=session["user"]))
            elif not regexPlainCheck or regexSpecialCheck:
                flash(u"Password criteria not met", "warning")
                return redirect(url_for("signup"))

        return render_template("signup.html")
    # IF USER IS LOGGED IN, REDIRECT
    else:
        return redirect(url_for("profile", username=session["user"]))


@app.route("/login", methods=["GET", "POST"])
def login():
    # IF USER IS NOT LOGGED IN ALREADY
    if "user" not in session:
        if request.method == "POST":
            userEmailMatch = mongo.db.users.find_one(
                {"email": request.form.get("loginEmail").lower()})
            if userEmailMatch:
                matchedUsername = userEmailMatch["username"]
                # CHECKS IF HASHED PASSWORD MATCHES USER INPUT
                if check_password_hash(userEmailMatch["password"],
                                       request.form.get("loginPassword")):
                    session["user"] = matchedUsername
                    flash(u"Welcome back {}".format(
                        userEmailMatch["first_name"].capitalize()), "success")
                    return redirect(url_for("profile",
                                    username=session["user"]))
                else:
                    # INVALID PASSWORD MATCH
                    flash(u"Incorrect login details. Please try again.",
                          "warning")
                    return redirect(url_for("login"))
            else:
                # INCORRECT EMAIL
                flash(u"Incorrect login details. Please try again.", "warning")
                return redirect(url_for("login"))
        return render_template("login.html")
    # IF USER IS LOGGED IN, REDIRECT
    else:
        return redirect(url_for("profile", username=session["user"]))


def getUserData(username):
    firstName = mongo.db.users.find_one({"username": username})['first_name']
    userData = mongo.db.users.find_one({"username": username})['_id']
    userSubmissionsCount = mongo.db.beans.count_documents(
        {"username": username})
    userCreationTimestamp = ObjectId(userData).generation_time
    userSince = utcToLocal(userCreationTimestamp).date()

    userData = {
        'firstName': firstName,
        'userData': userData,
        'userSubmissionsCount': userSubmissionsCount,
        'userCreationTimestamp': userCreationTimestamp,
        'userSince': userSince
    }

    return userData


@app.route("/profile/<username>")
def profile(username):
    # RETURNS LIST OF USERS IN DATABASE
    users = mongo.db.users.distinct('username')
    # IF URL CONTAINS REAL USERNAME
    if username in users:
        data = mongo.db.beans.find({"username": username}).sort("_id", -1)
        offset, perPage, page, beansCount, pageQuantity = pagination(
            6, mongo.db.beans.count_documents({"username": username})
        )
        user_submissions = data.skip(offset).limit(perPage)

        pagination_sort(user_submissions)

        user_submissions = list(user_submissions)
        submission_count = len(list(user_submissions))

        # RENDERS PROFILE PAGE VISISBLE TO ALL
        context = {
            'username': username,
            'user_submissions': user_submissions,
            'submission_count': submission_count,
            'offset': offset,
            'perPage': perPage,
            'page_variable': page,
            'beansCount': beansCount,
            'pageQuantity': pageQuantity,
            'getUserData': getUserData(username)
        }

        return render_template("profile.html", **context)
    else:
        # REDIRECTS TO HOMEPAGE IF URL USERNAME DOESN'T EXIST IN DATABASE
        return redirect(url_for("index"))


@app.route("/profile/<username>/update_account", methods=["GET", "POST"])
def update_account(username):
    # IF USER ISN'T LOGGED IN OR NOT LOGGED IN AS USER OF PROFILE BEING VIEWED
    if "user" not in session or session["user"] != username:
        # REDIRECTS TO PROFILE PAGE
        return redirect(url_for("profile", username=username))
    # IF LOGGED IN AS USER BEING VIEWED
    if session["user"] == username:
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
            "password": mongo.db.users.find_one(
                {"username": session["user"]})["password"]
        }

        # CREATES FULL NAME FROM EXISTING VALUES
        existing_first_name = existingPreferences["first_name"]
        existing_last_name = existingPreferences["last_name"]
        existing_full_name = existing_first_name + " " + existing_last_name

        # IF UPDATE REQUEST IS SENT
        if request.method == "POST":
            # FINDS THE USERS UNIQUE ID IDENTIFIER
            userId = mongo.db.users.find_one(
                {"username": session["user"]})["_id"]

            if "updateAccount" in request.form:

                # RETRIEVES NEW PREFERENCES
                editedPreferences = {
                    "first_name": request.form.get("inputFirstName").lower(),
                    "last_name": request.form.get("inputLastName").lower(),
                    "email": request.form.get("inputEmail").lower(),
                    "username": request.form.get("inputUsername")
                }

                edited_user_email = mongo.db.users.find_one(
                    {"email": editedPreferences["email"]})
                edited_user_username = mongo.db.users.find_one(
                    {"username": editedPreferences["username"]})

                # IF EXISTING INPUT IS NOT THE SAME AS POST REQUEST VALUE
                if editedPreferences["email"] != existingPreferences["email"]:
                    # IF NEW EMAIL ALREADY EXISTS
                    if edited_user_email:
                        flash(
                            u"An account with this email already exists",
                            "warning")
                        return redirect(url_for("update_account",
                                                username=session["user"]))
                # IF EXISTING INPUT IS NOT THE SAME AS POST REQUEST VALUE
                if editedPreferences["username"] != existingPreferences[
                                                    "username"]:
                    # IF NEW USERNAME ALREADY EXISTS
                    if edited_user_username:
                        flash(u"An account with this username already exists",
                              "warning")
                        return redirect(url_for("update_account",
                                                username=session["user"]))

                # CREATES FULL NAME FROM EDITED VALUES
                edited_first_name = editedPreferences["first_name"]
                edited_last_name = editedPreferences["last_name"]
                edited_full_name = edited_first_name + " " + edited_last_name

                # UPDATE ALL BEANS TO NEW USERNAME
                mongo.db.beans.update_many(
                    {"username": session["user"]},
                    {"$set": {"username": editedPreferences["username"]}})

                # UPDATE ALL BEANS TO NEW FULL NAME
                mongo.db.beans.update_many(
                    {"full_name": existing_full_name},
                    {"$set": {"full_name": edited_full_name}})

                # UPDATE ALL RATINGS TO NEW USERNAME
                mongo.db.beans.update_many(
                    {"rating.username": session["user"]},
                    {
                        "$set": {
                            "rating.$.username": editedPreferences["username"]
                        }
                    }
                )

                # UPDATE ALL REVIEWS TO NEW USERNAME
                mongo.db.beans.update_many(
                    {"review.username": session["user"]},
                    {
                        "$set": {
                            "review.$.username": editedPreferences["username"]
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
                return redirect(url_for("update_account",
                                        username=session["user"]))

            # SOURCE:
            # https://stackoverflow.com/questions/19605150/regex-for-password-must-contain-at-least-eight-characters-at-least-one-number-a
            regexBase = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"
            regexNoSymbol = "[a-zA-Z\d]{8,}$"
            regexSymbol = "(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
            regexPlain = regexBase + regexNoSymbol
            regexSpecial = regexBase + regexSymbol

            if "changePassword" in request.form:

                # USER ENTERED EXISTING PASSWORD
                inputExistingPassword = request.form.get(
                    "inputExistingPassword")

                newPassword = generate_password_hash(request.form.get(
                                                    "inputPassword"))

            # CHECK EXISTING PASSWORD MATCHES NEW PASSWORD
            if check_password_hash(
                                   existingPreferences['password'],
                                   inputExistingPassword):

                # CHECK REGEX MATCHES
                regexSpecialCheck = re.search(
                    regexSpecial, request.form.get("inputPassword"))
                regexPlainCheck = re.search(
                    regexPlain, request.form.get("inputPassword"))

                # IF NEW PASSWORD CONFORMS TO CRITERIA
                if regexPlainCheck or regexSpecialCheck:
                    # IF BOTH NEW PASSWORDS MATCH
                    if request.form.get("inputPassword") == request.form.get(
                                                    "inputConfirmPassword"):

                        # UPDATES THE USERS COLLECTION WITH NEW PASSWORD
                        mongo.db.users.update_one(
                            {"_id": userId},
                            {
                                "$set": {
                                    "password": newPassword
                                }
                            }
                        )

                        # VALIDATES THE UPDATE HAS COMPLETED
                        flash(u"Your password has been changed successfully",
                              "success")
                        return redirect(url_for("update_account",
                                                username=session["user"]))

                    else:
                        flash(u"New passwords do not match", "warning")
                        return redirect(url_for("update_account",
                                        username=session["user"]))

                else:
                    flash(u"New password doesn't meet criteria", "warning")
                    return redirect(url_for("update_account",
                                            username=session["user"]))

            else:
                flash(u"Existing password entered incorrectly", "warning")
                return redirect(url_for("update_account",
                                        username=session["user"]))

        context = {
            'username': existingPreferences["username"],
            'first_name': existingPreferences["first_name"],
            'last_name': existingPreferences["last_name"],
            'email': existingPreferences["email"],
            'getUserData': getUserData(username)
        }

        return render_template("update_account.html", **context)


@app.route("/profile/<username>/delete_account", methods=["GET", "POST"])
def delete_account(username):
    # IF USER ISN'T LOGGED IN OR NOT LOGGED IN AS USER OF PROFILE BEING VIEWED
    if "user" not in session or session["user"] != username:
        # REDIRECTS TO PROFILE PAGE
        return redirect(url_for("profile", username=username))
    if request.method == "POST":
        if "deleteUser" in request.form:
            # RETURNS MATCHING USERNAME FROM DATABASE
            loggedInAccount = mongo.db.users.find_one(
                {"username": session["user"]})

            # INCORRECT USERNAME VALIDATION
            if session["user"] != request.form.get("confirmUsername"):
                flash(u"You did not enter the correct username. Try again.",
                      "warning")
                return redirect(url_for("delete_account", username=username))
            else:
                # USERNAME AND PASSWORD MATCHED
                if check_password_hash(loggedInAccount["password"],
                                       request.form.get("confirmPassword")):
                    # DELETE USER AND THEIR SUBMISSIONS
                    submissionsQuery = {"username":
                                        loggedInAccount["username"]}
                    mongo.db.beans.delete_many(submissionsQuery)
                    mongo.db.users.delete_one(loggedInAccount)
                    # DELETION VALIDATION
                    flash(u"Your account has been permanently deleted",
                          "success")
                    # LOG USER OUT
                    session.pop("user")
                    return redirect(url_for("index"))
                else:
                    # USERNAME IS CORRECT BUT PASSWORD INPUT DID NOT MATCH
                    flash(
                        u"You did not enter the correct password. Try again.",
                        "warning")
                    return redirect(url_for("delete_account",
                                            username=username))
    return render_template("delete_account.html", username=username,
                           getUserData=getUserData(username))


@app.route("/logout")
def logout():
    # IF USER NOT LOGGED IN
    if "user" not in session:
        return redirect(url_for("login"))
    else:
        flash(u"You have been logged out", "success")
        session.pop("user")
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
