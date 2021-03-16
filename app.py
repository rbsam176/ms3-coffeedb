import os
import sys
import random
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
    if request.method == "POST":
        print(request.form["brand"])
        print(request.form["name"])
        print(request.form["roast"])
        print(request.form["origin"])
        print(request.form["organic"])
        print(request.form["website"])
        print(request.form.getlist('note'))

    return render_template("add.html", beans=beans, coffeeImg=coffeeImg, roast_types=roast_types, origin_types=origin_types, uniqueNotes=uniqueNotes, brand_names=brand_names)

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

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)
