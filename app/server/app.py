# server.py
from flask import Flask, flash, redirect, render_template, request, session, abort, jsonify
from calRetrieve import *
import datetime
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, create_engine, Sequence, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
import createTables
import uuid
import os
app = Flask(__name__, static_folder="../static/dist", template_folder="../static")
app.secret_key = str(uuid.uuid4())

Base=declarative_base()
postgresql_uri=os.environ['DATABASE_URL']
engine=create_engine(postgresql_uri)

Session = sessionmaker(bind=engine)
db = Session()

@app.route("/")
def index():
    calendarCall()
    return render_template("index.html")

@app.route('/oauth2callback')
def oauth2callback():
    return mainOauth2callback()

@app.route('/login')
def login():
    # If you are logged in already, redirect you to the proper webpage
    if session.get('logged_in') == True:
        if session['role'] == 'Manager':
            return redirect('/managerdashboard')
        elif session['role'] == 'Student':
            return redirect('/studentdashboard')
    return render_template("login.html")

@app.route('/loginC', methods = ['POST'])
def loginC():
    inputusername = request.args.get("inputusername")
    inputpassword = request.args.get("inputpassword")
    data = request.get_json(silent=True)
    item = {'username': data.get('inputusername'), 'password': data.get('inputpassword')}

    res = db.execute("""SELECT id from student where username = '%s' and password= '%s';"""%(item['username'], item['password']))
    res1 = res.fetchall()
    res = db.execute("""SELECT id from manager where username = '%s' and password= '%s';"""%(item['username'], item['password']))
    res2 = res.fetchall()
    if len(res1) > 0:
        session['username'] = item['username']
        session['role'] = 'Student'
        session['logged_in'] = True

        print('student logged in')

        go_to = check_and_redirect_back('/studentdashboard')
        return go_to

    elif len(res2)> 0:
        session['username'] = item['username']
        session['role'] = 'Manager'
        session['logged_in'] = True
        print('manager logged in')
        go_to = check_and_redirect_back('/managerdashboard')
        return  go_to
    else:
        print('wrong combination for username and password')
        return '/login'

@app.route('/signup')
def signup():
    # If you are logged in already, redirect you to the proper webpage
    if session.get('logged_in') == True:
        if session['role'] == 'Manager':
            return redirect('/managerdashboard')
        elif session['role'] == 'Student':
            return redirect('/studentdashboard')
    return render_template('index.html')

@app.route('/signupC', methods = ['POST'])
def signupC():
    inputusername = str(request.args.get("inputusername"))
    inputpassword = str(request.args.get("inputpassword"))
    inputrole = request.args.get("inputrole")
    data = request.get_json(silent=True)
    item = {'username': data.get('inputusername'), 'password': data.get('inputpassword'),'role': data.get('inputrole')}
    print(item)
    res = db.execute("""SELECT id from %s where username = '%s' and password= '%s';"""%(item['role'], item['username'], item['password']))
    res = res.fetchall()
    if len(res) >0:
        return '/login'
    else:
        db.execute("""INSERT into %s(username, password) VALUES ('%s','%s');"""%(item['role'],item['username'],item['password']))
        db.commit()

        session['username'] = item['username']
        session['role'] = item['role']
        session['logged_in'] = True

        print("insert is executed")
        
        if item['role'] == 'Manager':
            go_to = check_and_redirect_back('/managerdashboard')
            return  go_to
        elif item['role'] == 'Student':
            go_to = check_and_redirect_back('/studentdashboard')
            return  go_to
        return '/'

@app.route("/logout")
def logout():
    session['username'] = None
    session['role'] = None
    session['logged_in'] = False

    return redirect('/')

# @app.route('/nordicshift.ico')
# def icon():
#   print("in icon route")
#   return render_template("index.html")
@app.route('/myprofile')
def myprofile():
    if session.get('role') == 'manager':
        return redirect('/managerprofile')
    elif session.get('role') == 'student':
        return redirect('/studentprofile')
    else:
        return redirect('/login')

@app.route('/api/managerprofile', methods = ['POST'])
def managerprofile():
    print(session)
    data = request.get_json(silent=True)
    department = data.get("department")
    student = data.get("student")
    print("department: ", data.get("department"))
    print("student: ", data.get("student"))
    if department!='':
        res = db.execute("""SELECT * from department where name ='%s';"""%department)
        res = res.fetchall()
        if len(res) == 0:
            db.execute("""INSERT into department(name) VALUES ('%s');"""%department)
        db.execute("""UPDATE manager SET dept = (SELECT id from department where name ='%s') WHERE username = '%s';"""%(department, session.get('username')))
        db.commit()
    if student!='':
        if '@luther.edu' not in student:
            return 'error'
        res = db.execute("""SELECT * from student where username ='%s'"""%student)
        res = res.fetchall()
        if len(res)==0:
            db.execute("""INSERT into student(username, password) VALUES ('%s','student');"""%student)
        db.execute("""INSERT into ds(department,student) VALUES ((SELECT dept from manager where username = '%s'),(SELECT id from student where username ='%s'));"""%(session.get("username"), student))
        db.commit()
    return '/myprofile'

#naming standard, if it is being used for an axios call, use /api/name_of_call
@app.route("/api/calendar")
def calendar():
  myevents = [{
  "title": 'Your Shift',
  "start":  datetime.datetime(2017, 10, 31, 13),
  "end": datetime.datetime(2017, 10, 31, 15),
  "hexColor" : "#ee5f5b"
  }]
  #color scheme colors: #62c462, #5bc0de, #f89406,  #ee5f5b
  print("In calendar!!")
  data = {"calData": "Calendar Data", "events": myevents}
  return jsonify(data)

@app.route("/api/addEvent", methods = ['POST'])
def addEvent():
  print ('IN ADD EVENT!')
  #title = request.args.get("title")
  #print("title: ", title)
  data = request.get_json(silent=True)
  myEvent = data.get('myEvent')
  # myEvent['title'] = 'New Shift'
  myEvent['hexColor'] = '#f89406'
  #print('myEvent: ', myEvent)
  data = myEvent
  #TODO write change to database, add new shift
  date_str = "2016-03-28T20:23:46+0800"
  old_format = "%Y-%m-%dT%H:%M:%S.%fZ"
  new_format = '%Y-%m-%d %H:%M:%S'
  startTime = data.get('start')
  start=datetime.datetime.strptime(startTime, old_format).strftime(new_format)
  endTime = data.get('end')
  end = datetime.datetime.strptime(endTime, old_format).strftime(new_format)
  db.execute("""INSERT into shift(dept, startTime, endTime) VALUES ((SELECT dept from manager where username = '%s'), '%s', '%s');"""%(session.get('username'),start, end))
  db.commit()
  print(myEvent)
  return jsonify(data)

@app.route("/api/moveEvent", methods = ['POST'])
def moveEvent():
  print ('IN MOVE EVENT!')
  #title = request.args.get("title")
  #print("title: ", title)
  data = request.get_json(silent=True)
  myEvent = data.get('myEvent')
  data = myEvent
  date_str = "2016-03-28T20:23:46+0800"
  old_format = "%Y-%m-%dT%H:%M:%S.%fZ"
  new_format = '%Y-%m-%d %H:%M:%S'
  startTime = data.get('start')
  start=datetime.datetime.strptime(startTime, old_format).strftime(new_format)
  endTime = data.get('end')
  end = datetime.datetime.strptime(endTime, old_format).strftime(new_format)
  #TODO write change to database , need to remove/modify old shift
  db.execute("""UPDATE shift SET startTime ='%s' and endTime='%s'""")
  return jsonify(data)

@app.route("/api/deleteEvent", methods = ['POST'])
def deleteEvent():
  print ("IN DELETE EVENT")
  data = request.get_json(silent=True)
  myEvent = data.get('myEvent')
  #TODO delete shift from database
  #maybe return new list of events, or leave it to the front end
  return "done"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if session.get("logged_in") == True or path == '/':
        return render_template("index.html")
    else:
        session['attempted_url'] = path
        return redirect("/login")

# This is a function that will redirect you to a credential protected page.
# It will check to see if you tried to access the page and redirect you to it if needed
# else, it will redirect you to the alt_url.
def check_and_redirect_back(alt_url):
    if session.get('attempted_url'):
        redir = session.get('attempted_url')
        del session['attempted_url']
        return '/' + redir
    else:
        return alt_url

if __name__ == "__main__":
    createTables.createTables()
    app.run(debug=True)
