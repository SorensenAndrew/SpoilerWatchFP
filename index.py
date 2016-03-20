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
import datetime


app = Flask(__name__)
app.secret_key = "4321"

@app.route('/')
def index():
    return redirect('/login')

###### News Feed #####

@app.route('/home')
def navhome():
    name = session["username"]
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("select * from showData where username!='"+ name + "' order by dateAdded desc")
    showdata = cursor.fetchall()
    return render_template('userHome.html',showdata=showdata)

@app.route('/comment', methods=['post','get'])
def comment():
    comment = request.form["comment"]
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("insert into comments(comment)values(%s)", (comment))
    render_template('userHome.html')


###########################


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

###### Display Shows #######################
@app.route('/shows')
def show():
    name = session["username"]
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("select showName, showTitle, showSeason, showEpisode,episodeCount from showData where username='"+ name+ "'")
    showdata = cursor.fetchall()
    return render_template('shows.html',showdata=showdata)


#### Show Progress and Badges ####

@app.route('/badges', methods=['post','get'])
def badgePage():
    name = session["username"]
    showName = request.form['showName']
    season = request.form['season']
    currentEpisode = request.form['currentEpisode']
    lastEpisode = request.form['lastEpisode']
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("select showName, showTitle, showSeason, showEpisode,episodeCount from showData where showName='" + showName + "' and username='" + name + "'")
    showdata = cursor.fetchall()
    badgeCursor = db.cursor()
    badgeCursor.execute("select showName, badges from badges where showName='" + showName + "' and username='" + name + "'")
    badgeData = badgeCursor.fetchall()
    if currentEpisode == lastEpisode:
        badge = "You have completed season '" + season + "' of '"+ showName+ "'"
        db2 = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
        cursor2 = db2.cursor()
        cursor2.execute("insert into badges(username, showSeason, showName, badges)values(%s,%s,%s,%s)", (name, season, showName, badge))
        db2.commit()
    return render_template('badges.html',showdata=showdata, badgeData = badgeData)


###### Verify user login ######

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
        return render_template('showSearch.html',data=data)
    else:
        return redirect('/login')

#### Friends List and Management ########

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

######## User Registration ########

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


################### Add Show ###################################################################

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
    url2 = "http://www.omdbapi.com/?t=" + title +"&Season="+ season +"&r=json"
    url2 = url2.replace(" ","%20")
    loadurl2 = urllib.urlopen(url2)
    data2 = json.loads(loadurl2.read().decode(loadurl2.info().getparam('charset') or 'utf-8'))
    # print data2['Episodes']
    episodeCount = []
    episodeCount.append(data2['Episodes'])
    for i in range(len(episodeCount)):
        print len(episodeCount[i])
    totalEpisodes = len(episodeCount[i])
    episodedata = data['Episode']
    titledata = data['Title']
    seasondata= data['Season']
    db = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor = db.cursor()
    cursor.execute("insert into showData(username, showTitle, showSeason, showEpisode, showName, episodeCount)values(%s,%s,%s,%s,%s, %s)", (name, titledata, seasondata, episodedata, title, totalEpisodes))
    cursor2 = db.cursor()
    cursor2.execute("select showEpisode, episodeCount from showData where showName='" + title + "'")
    new_count = cursor2.fetchall()
    db.commit()
    return render_template('profilePage.html',data=data,newVar=new_count)


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

@app.route('/form')
def form():
    return render_template('form.html')

### Javascript Fetch Data ####

@app.route('/dataRoute', methods=['get'])
def dataRoute():
    name = session["username"]
    db2 = mysql.connector.connect(user='root', password='root',host='localhost', database='spoilerDB', port='8889')
    cursor2 = db2.cursor2()
    cursor2.execute("select showName, showEpisode, episodeCount from showData where username='" + name + "'")
    newVar = cursor2.fetchall()
    print newVar
    return  render_template('shows.html')

# where username='" + name + "' and showName='" + showName + "'" #

#### Show Update ###########

@app.route('/updateShow', methods=['post', 'get'])
def updateshow():
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
    cursor.execute("update showData set showTitle=%s, showSeason=%s, showEpisode=%s where showName='" + title + "' and username='" + name  + "'", (titledata, seasondata, episodedata))
    cursor2 = db.cursor()
    cursor2.execute("select showEpisode, episodeCount from showData where showName='" + title + "'")
    new_count = cursor2.fetchall()
    db.commit()
    return render_template('profilePage.html',data=data, newVar=new_count)


######### Logout ###############

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')



############################



@app.route('/formtest', methods=['post','get'])
def formtest():
    userinput = request.form["user"]
    hashed = hashlib.md5(userinput).hexdigest()
    return hashed



if __name__ == '__main__':
    app.run(debug = True)