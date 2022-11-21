
import pyrebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for,jsonify
import pickle
import requests
import json

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "eaHWKSXPtK0m7BuLoSTrywJcns7e7SU4kWkKuHS5Ok1o"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

app = Flask(__name__)       #Initialze flask constructor

#Add your own details
config = {
  "apiKey": "AIzaSyDZXLOALLRvAnbUXR1e9wYHZfbMEO9M1Zk",
  "authDomain": "ibm-proj-34f67.firebaseapp.com",
  "projectId": "ibm-proj-34f67",
  "databaseURL": "https://ibm-proj-34f67-default-rtdb.firebaseio.com/",
  "storageBucket": "ibm-proj-34f67.appspot.com"
}

#initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

#Initialze person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}

#model=pickle.load(open("model.pkl",'rb'))

#Login
@app.route("/")
def login():
    return render_template("login.html")

#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

#Welcome page
@app.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
        return render_template("welcome.html", email = person["email"], name = person["name"])
    else:
        return redirect(url_for('login'))

#If someone clicks on login, they are redirected to /result
@app.route("/result", methods = ["POST", "GET"])
def result():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        email = result["email"]
        password = result["pass"]
        try:
            #Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            #Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            #Get the name of the user
            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]
            #Redirect to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))

#If someone clicks on register, they are redirected to /register
@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            #Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            #Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            #Append data to the firebase realtime database
            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)
            #Go to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect to register
            return redirect(url_for('register'))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))

#prediction after submit the form
@app.route('/y_predict',methods=['POST'])
def y_predict():
    gre=request.form["GRE Score"]
    toefl=request.form["TOEFL Score"]
    rating=request.form["University Rating"]
    sop=request.form["SOP"]
    lor=request.form["LOR"]
    cgpa=request.form["CGPA"]
    research=request.form["Research"]

    t=[[int(gre),int(toefl),int(rating),float(sop),float(lor),float(cgpa),int(research)]]

    payload_scoring = {"input_data": [{"field": ['GRE Score', 'TOEFL Score', 'University Rating', 'SOP','LOR ', 'CGPA', 'Research'], "values": t}]}
    
    response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/58c8fd11-26de-4325-bd0c-7bd66d879324/predictions?version=2022-11-19', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})

    predictions=response_scoring.json()
    print(predictions)

    pred=predictions['predictions'][0]['values'][0][0]

    return render_template('welcome.html',prediction_text=pred)


if __name__ == "__main__":
    app.run(debug=True)
