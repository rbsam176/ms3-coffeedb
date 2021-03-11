import os
import sys
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
    roast_types = mongo.db.beans.distinct('roast') # GETS ALL UNIQUE VALUES WITH KEY OF 'ROAST'
    origin_types = mongo.db.beans.distinct('origin') # GETS ALL UNIQUE VALUES WITH KEY OF 'ORIGIN'
    if request.method == "POST":
        roastChecked = []
        originChecked = []
        for item in request.form: # APPENDS ALL KEY VALUE PAIRS TO THEIR OWN ARRAYS
            checkboxReturn = item.split('=')
            if checkboxReturn[0] == 'roast':
                roastChecked.append(checkboxReturn[1])
            if checkboxReturn[0] == 'origin':
                originChecked.append(checkboxReturn[1])

        # DYNAMICALLY CREATES A FIND QUERY
        dynamicQuery = {}
        dynamicQuery["$and"]=[]
        # CHECKS IF VALUES EXIST AND ADDS TO DYNAMIC QUERY
        if roastChecked:
            dynamicQuery["$and"].append({ "roast": { "$in": roastChecked}})
        if originChecked:
            dynamicQuery["$and"].append({ "origin": { "$in": originChecked }})
        if 'organicRequired' in request.form:
            dynamicQuery["$and"].append({ "organic": True })
        # REPLACES VIEW WITH DYNAMIC QUERY SET BY USE FILTER INPUT
        beans = mongo.db.beans.find(dynamicQuery)

    return render_template("browse.html", beans=beans, roast_types=roast_types, origin_types=origin_types)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
    port=int(os.environ.get("PORT")),
    debug=True)