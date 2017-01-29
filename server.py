from flask import Flask, render_template, request, redirect, url_for
from database import *
import flask_login, json, re
from bson.objectid import ObjectId
from jinja2 import evalcontextfilter, Markup, escape
from api import *
from questions import *
import random, time

app = Flask(__name__)
app.secret_key = '80e48d13643b4b2f53663be3967bcc76' #pharma-c
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


@app.route("/")
def main_page():
    return render_template('register.html')

@app.route("/help")
def help():
    return render_template('register.html')

@app.route("/save/<pid>/<q1>/<q2>/<q3>", methods=['GET'])
def save(pid, q1, q2, q3):
    print pid, q1, q2, q3
    collection = database.patients
    p = collection.Patient.find_and_modify(
        query={"uid": str(pid)},
        update={"$set": {"uid": str(pid), "q1": str(q1), "q2": str(q2), "q3": str(q3)}
    }, new=True, upsert=True)


    return render_template('saved.html')

@app.route("/notify/<pid>")
def notify(pid):
    collection = database.patients
    patient = collection.Patient.find_one({'uid': str(pid)})

    q1 = q2 = q3 = 0

    if(patient):
        # print patient

        if(patient['q1'] == "true"):
            q1 = 1
        if(patient['q2'] == "true"):
            q2 = 1
        if(patient['q3'] == "true"):
            q3 = 1

        print q1, q2, q3

        randomQ = random.randrange(0,3)

        ans = answers[randomQ]

        message = questions[randomQ]
        message += "\n"
        for a in ans:
            message += "<a href=\"http://pharma-c.me/answer/" + pid + "/ " + str(randomQ) +"/"+ a + "\">" + a + "</a> \n"

        print message

        send_notification("Quick Question", message, "tel:1-800-PHARMA-C", "Call my pharmacist!")

        return render_template("notified.html")
    
    return str("Not found")

@app.route("/view/<pid>")
def view(pid):
    return render_template('results.html')

#http://pharma-c.me/answer/1/Yes
@app.route("/answer/<pid>/<qid>/<ans>")
def answer(pid, qid, ans):

    collection = database.responses
    
    p = collection.Response()

    p["time"] = time.time()
    p["pid"] = unicode(pid)
    p["question"] = unicode(qid)
    p["answer"] = unicode(ans)
    
    p.save()

    return str("Thanks")


    
if __name__ == "__main__":
    app.run(debug=True)