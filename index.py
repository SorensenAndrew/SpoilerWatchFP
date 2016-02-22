from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask import session
from flask import jsonify
import urllib
import json
import pprint
import hashlib
import mysql.connector
from urllib2 import urlopen
from urllib2 import Request
from json import load
from lxml import html
import requests

app = Flask(__name__)
app.secret_key = "4321"

@app.route('/')
def index():
    return redirect('/login')


@app.route('/login', methods=['post','get'])
def login():
    return render_template('login.html')


@app.route('/users')
def users():
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("select * from users")
    data = cursor.fetchall()
    return render_template('users.html',data=data)


@app.route('/shows')
def show():
    name = session["username"]
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("select showName, showTitle, showSeason, showEpisode from showData where username='"+ name+ "'")
    showdata = cursor.fetchall()
    return render_template('shows.html',showdata=showdata)



@app.route('/checklogin', methods=['post','get'])
def checklogin():
    session["username"] = request.form["username"]
    session["password"] = request.form["password"]
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    hashval = hashlib.md5(request.form["password"]).hexdigest()

    cursor.execute("select * from users where username=%s and password=%s", (session["username"], session["password"]))
    data = cursor.fetchall()
    if data:
        data = {"username":session["username"],"password":session["password"]}
        return render_template('userHome.html',data=data)
    else:
        return redirect('/login')

@app.route('/friendForm', methods=['post','get'])
def friendForm():
    return render_template('addFriend.html')

@app.route('/addFriend', methods=['post','get'])
def addfriend():
    name = session["username"]
    friend = request.form['Addfriend']
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("insert into friends(username1, username2)values(%s,%s)", (name, friend))
    db.commit()
    return redirect('/friends')

@app.route('/friends')
def friends():
    name = session["username"]
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("select username1, username2 from friends where username1='"+ name+ "'")
    data = cursor.fetchall()
    return render_template('friends.html',data=data)

@app.route('/friendData',methods=['post', 'get'])
def frienddata():
    friendname = request.form['friend']
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("select showName, showTitle, showSeason, showEpisode from showData where username='" + friendname + "'")
    data = cursor.fetchall()
    return render_template('friendData.html',data=data)


@app.route('/newUser')
def newUser():
    return render_template('addUserform.html')


@app.route('/addUser',methods=['post', 'get'])
def addUser():
    uname = request.form['newUser']
    upass = request.form['newPassword']
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("insert into users(username, password)values(%s,%s)", (uname, upass))
    db.commit()
    return redirect('/login')

################## Admin SignUp/Login ##################################

@app.route('/addAdmin',methods=['post', 'get'])
def addAdmin():
    aname = request.form['newAdmin']
    apass = request.form['newAdminPassword']
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("insert into admin(adminUser, password)values(%s,%s)", (aname, apass))
    db.commit()
    return redirect('/login')

@app.route('/newAdmin')
def newAdmin():
    return render_template('addAdminAccess.html')

@app.route('/adminCheck',methods=['post', 'get'])
def adminCheck():
    session["adminAccessPassword"] = request.form["adminAccessPassword"]
    apass = request.form['adminAccessPassword']
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("select * from adminPass", (session["adminAccessPassword"]))
    data = cursor.fetchall()
    if data:
        data = {"adminAccessPassword":session["adminAccessPassword"]}
        return render_template('adminReg.html',data=data)
    else:
        return redirect('/login')

@app.route('/checkAdminLogin', methods=['post','get'])
def checkAdminLogin():
    session["adminUser"] = request.form["adminUser"]
    session["adminPassword"] = request.form["adminPassword"]
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    hashval = hashlib.md5(request.form["adminPassword"]).hexdigest()

    cursor.execute("select * from admin where adminUser=%s and password=%s", (session["adminUser"], session["adminPassword"]))
    data = cursor.fetchall()
    if data:
        data = {"adminUser":session["adminUser"],"adminPassword":session["adminPassword"]}
        return render_template('adminHome.html',data=data)
    else:
        return redirect('/login')

###################### Complaint File ###############################################

@app.route('/fileComplaint', methods=['post','get'])
def complaint():
    name = "testName"
    complaint = request.form['complaint']
    unchecked = 0
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("insert into complaint(user, complaint, complete)values(%s,%s,%s)", (name, complaint, unchecked))
    db.commit()
    return redirect('/friends')



######################################################################################

@app.route('/parseJSON',methods=['post', 'get'])
def parseJSON():
    name = session["username"]
    title = request.form["title"]
    season = request.form['season']
    episode = request.form['episode']
    url = "http://www.omdbapi.com/?t=" + title +"&Season="+ season + "&Episode=" + episode +"&r=json"
    url = url.replace(" ","%20")
    loadurl = urllib.urlopen(url)
    data = json.loads(loadurl.read().decode(loadurl.info().getparam('charset') or 'utf-8'))
    episodedata = data['Episode']
    titledata = data['Title']
    seasondata= data['Season']
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("insert into showData(username, showTitle, showSeason, showEpisode, showName)values(%s,%s,%s,%s,%s)", (name, titledata, seasondata, episodedata, title))
    db.commit()
    return render_template('profilePage.html',data=data)


@app.route('/showSearch')
def nprForm():
    return render_template('showSearch.html')


@app.route('/deleteShow', methods=['post', 'get'])
def deleteshow():
    name = session["username"]
    random = request.form["random"]
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("delete from showData where showName='" + random + "' and username='" + name + "'")
    db.commit()
    return redirect('/shows')

#### Show Update ###########

@app.route('/updateShow', methods=['post', 'get'])
def updateshow():
    name = session["username"]
    show = request.form["show"]
    showTitle = request.form["title"]
    showSeason = request.form["season"]
    showEpisode = request.form["episode"]
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("update showData set showTitle=%s, showSeason=%s, showEpisode=%s where showName='" + show + "' and username='" + name + "'", (showTitle, showSeason, showEpisode ))
    db.commit()
    return redirect('/shows')


########################

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/formtest', methods=['post','get'])
def formtest():
    userinput = request.form["user"]
    hashed = hashlib.md5(userinput).hexdigest()
    return hashed

################### HTML Scraping ###################################
page = requests.get('http://econpy.pythonanywhere.com/ex/001.html')
tree = html.fromstring(page.content)

#This will create a list of buyers:
buyers = tree.xpath('//div[@title="buyer-name"]/text()')
#This will create a list of prices
prices = tree.xpath('//span[@class="item-price"]/text()')

print 'Buyers: ', buyers
print 'Prices: ', prices


if __name__ == '__main__':
    app.run(debug = True)