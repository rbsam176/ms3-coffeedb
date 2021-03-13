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

@app.route("/browse", methods=["GET", "POST"])
def browse():
    beans = mongo.db.beans.find() # DEFAULT VIEW SHOWS ALL RESULTS
    notes = mongo.db.beans.find({}, {"notes" : 1}) # RETURNS LIST OF ALL NON-UNIQUE NOTES
    uniqueNotes = mongo.db.beans.distinct('notes') # RETURNS LIST OF ALL UNIQUE NOTES
    roast_types = mongo.db.beans.distinct('roast') # GETS ALL UNIQUE VALUES WITH KEY OF 'ROAST'
    origin_types = mongo.db.beans.distinct('origin') # GETS ALL UNIQUE VALUES WITH KEY OF 'ORIGIN'
    roastChecked = [] # RETURNS LIST OF ALL ROAST TYPES THAT WERE CHECKED
    originChecked = [] # RETURNS LIST OF ALL ORIGINS THAT WERE CHECKED
    organicChecked = [] # RETURNS WHETHER ORGANIC TOGGLE WAS ON/OFF
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
    
    print(notesRelativePercentage)

    # take the highest percentage
    # divide the figure by the number of font sizes in the cloud
    # if the note's percentage is > 75% of highest percentage, be h2
    # if the note's percentage is > 50% of highest percentage, be h3 etc.
    ## make dictionary of note name and h size, eg: lemon: h4
    ### then in jinja use like this: <{{ note-font-size }}>{{ note }}</{{ note-font-size }}>

    
    if request.method == "POST":
        if request.form.get('submit', None) == "Submit": # IF POST REQUEST WAS FROM SUBMIT BUTTON, SOURCE: https://stackoverflow.com/questions/8552675/form-sending-error-flask
            for item in request.form: # APPENDS ALL KEY VALUE PAIRS TO THEIR OWN ARRAYS
                checkboxReturn = item.split('=')
                if checkboxReturn[0] == 'roast':
                    roastChecked.append(checkboxReturn[1])
                if checkboxReturn[0] == 'origin':
                    originChecked.append(checkboxReturn[1])
                if item == 'organicRequired':
                    organicChecked.append(True)
            

            # DYNAMICALLY CREATES A FIND QUERY
            # ADAPTED FROM https://stackoverflow.com/questions/65823199/dynamic-mongo-query-with-python
            dynamicQuery = {}
            dynamicQuery["$and"]=[]
            # CHECKS IF VALUES EXIST AND ADDS TO DYNAMIC QUERY
            if roastChecked:
                dynamicQuery["$and"].append({ "roast": { "$in": roastChecked}})
            if originChecked:
                dynamicQuery["$and"].append({ "origin": { "$in": originChecked }})
            if organicChecked:
                dynamicQuery["$and"].append({ "organic": True })
            # REPLACES VIEW WITH DYNAMIC QUERY SET BY USE FILTER INPUT
            beans = mongo.db.beans.find(dynamicQuery)
        elif request.form.get('reset', None) == "Reset": # IF POST REQUEST WAS FROM RESET BUTTON
            beans = mongo.db.beans.find() # DISPLAY DEFAULT VIEW SHOWING ALL RESULTS
        


    beans = list(beans)
    return render_template("browse.html", beans=beans, roast_types=roast_types, origin_types=origin_types, roastChecked=roastChecked, originChecked=originChecked, organicChecked=organicChecked, notesRelativePercentage=notesRelativePercentage)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)