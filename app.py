from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask import session
import urllib
import json
import hashlib
import mysql.connector

app = Flask(__name__)
app.secret_key = "4321"



@app.route('/')
def index():
    return redirect('/login')

######## User Registration ########

@app.route('/newUser')
def newUser():
    return render_template('addUserform.html')


@app.route('/addUser',methods=['post', 'get'])
def addUser():
    try:
        uname = request.form['newUser']
        upass = request.form['newPassword']
        db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
        cursor = db.cursor()
        cursor.execute("insert into users(username, password)values(%s,%s)", (uname, upass))
        db.commit()
        return render_template('/newUserWelcome.html')
    except:
        return render_template('usernameError.html')


###### News Feed #####

@app.route('/home')
def navhome():
    name = session["username"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
    cursor = db.cursor()
    cursor.execute("select * from showdata sd join friends f on (f.username2=sd.username)where f.username1='"+ name+ "'")
    showdata = cursor.fetchall()
    return render_template('userHome.html',showdata=showdata)


###########################


@app.route('/login', methods=['post','get'])
def login():
    return render_template('login.html')

@app.route('/users')
def users():
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
    cursor = db.cursor()
    cursor.execute("select * from users")
    data = cursor.fetchall()
    return render_template('users.html',data=data)

###### Display Shows #######################
@app.route('/shows')
def show():
    name = session["username"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
    cursor = db.cursor()
    cursor.execute("select showName, showTitle, showSeason, showEpisode,episodeCount from showData where username='"+ name+ "'")
    showdata = cursor.fetchall()
    return render_template('shows.html',showdata=showdata)

#### Show Progress and Badges ####

@app.route('/showInfo', methods=['post','get'])
def badgePage():
    name = session["username"]
    showName = request.form['showName']
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
    cursor = db.cursor()
    cursor.execute("select showName, showTitle, showSeason, showEpisode,episodeCount, plot, posterID, airDate from showData where showName='" + showName + "' and username='" + name + "'")
    showdata = cursor.fetchall()
    badgeCursor = db.cursor()
    badgeCursor.execute("select showName, badges from badges where showName='" + showName + "' and username='" + name + "'")
    badgeData = badgeCursor.fetchall()
    return render_template('showInfo.html',showdata=showdata, badgeData = badgeData)

### Show All Badges Page #####

@app.route('/allBadges', methods=['get'])
def allBadges():
    name = session["username"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
    badgeCursor = db.cursor()
    badgeCursor.execute("select badges from badges where username='" + name + "'")
    badgeData = badgeCursor.fetchall()
    return render_template('allBadges.html', badgeData = badgeData)

###### Verify user login ######

@app.route('/checklogin', methods=['post','get'])
def checklogin():
    session["username"] = request.form["username"]
    session["password"] = request.form["password"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
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

@app.route('/addFriend', methods=['post','get'])
def addfriend():
    name = session["username"]
    friend = request.form['Addfriend']
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
    cursor = db.cursor()
    cursor.execute("select username from users where username='"+ friend + "'")
    userCheck = cursor.fetchall()
    if userCheck:
        cursor3 = db.cursor()
        cursor3.execute("select * from friends f where username1 = '"+ name+ "' and username2='"+ friend + "';")
        friendCheck = cursor3.fetchall()
        if friendCheck:
            return render_template('error.html')
        else:
            cursor2 = db.cursor()
            cursor2.execute("insert into friends(username1, username2)values(%s,%s)", (name, friend))
            db.commit()
            return redirect('/friends')




@app.route('/friends')
def friends():
    name = session["username"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
    cursor = db.cursor()
    cursor.execute("select username1, username2 from friends where username1='"+ name + "'")
    data = cursor.fetchall()
    return render_template('friends.html',data=data)

@app.route('/manageFriends', methods=['post', 'get'])
def friendmanager():
    name = session["username"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
    cursor = db.cursor()
    cursor.execute("select username1, username2 from friends where username1='"+ name+ "'")
    data = cursor.fetchall()
    return render_template('manageFriends.html',data=data)

@app.route('/friendData',methods=['post', 'get'])
def frienddata():
    friendname = request.form['friend']
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
    cursor = db.cursor()
    cursor.execute("select showName, showTitle, showSeason, showEpisode from showData where username='" + friendname + "'")
    data = cursor.fetchall()
    badgeCursor = db.cursor()
    badgeCursor.execute("select badges from badges where username='" + friendname + "'")
    badgeData = badgeCursor.fetchall()
    return render_template('friendData.html',data=data, badgeData=badgeData)

@app.route('/deleteFriends', methods=['post', 'get'])
def deletefriend():
    name = session["username"]
    friendname = request.form['friend']
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
    cursor = db.cursor()
    cursor.execute("delete from friends where username2='" + friendname + "' and username1='"+ name+ "'")
    db.commit()
    return render_template('deleteConf.html')




################### Add Show ###################################################################

@app.route('/parseJSON',methods=['post', 'get'])
def parseJSON():
    try:
        name = session["username"]
        title = request.form["title"].title()
        season = request.form['season']
        episode = request.form['episode']
        url = "http://www.omdbapi.com/?t=" + title +"&Season="+ season + "&Episode=" + episode +"&r=json&apikey=e24fb313 "
        url = url.replace(" ","%20")
        loadurl = urllib.urlopen(url)
        data = json.loads(loadurl.read().decode(loadurl.info().getparam('charset') or 'utf-8'))
        url2 = "http://www.omdbapi.com/?t=" + title +"&Season="+ season +"&r=json"
        url2 = url2.replace(" ","%20")
        loadurl2 = urllib.urlopen(url2)
        data2 = json.loads(loadurl2.read().decode(loadurl2.info().getparam('charset') or 'utf-8'))
        episodeCount = []
        episodeCount.append(data2['Episodes'])
        for i in range(len(episodeCount)):
            print len(episodeCount[i])
        totalEpisodes = len(episodeCount[i])
        episodedata = data['Episode']
        titledata = data['Title']
        seasondata= data['Season']
        plotData = data['Plot']
        airDate = data['Released']
        posterID = data['seriesID']
        tE = int(totalEpisodes)
        eD = int(episodedata)
        db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
        cursor = db.cursor()
        cursor.execute("insert into showData(username, showTitle, showSeason, showEpisode, showName, episodeCount, plot, posterID, airDate)values(%s,%s,%s,%s,%s, %s, %s, %s, %s)", (name, titledata, seasondata, episodedata, title, totalEpisodes, plotData, posterID, airDate))
        cursor2 = db.cursor()
        cursor2.execute("select showEpisode, episodeCount from showData where showName='" + title + "'")
        new_count = cursor2.fetchall()
        if eD == tE:
            badge = "You have completed season '" + season + "' of '" + title + "'"
            cursor3 = db.cursor()
            cursor3.execute("insert into badges(username, showSeason, showName, badges)values(%s,%s,%s,%s)", (name, season, title, badge))
        cursor4 = db.cursor()
        cursor4.execute("select showName from showData where username='" + name + "'")
        totalShowsFollowed = cursor4.fetchall()
        if len(totalShowsFollowed) == 5:
            showNumberBadge = "Following 5 Shows!"
            cursor5 = db.cursor()
            cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, showNumberBadge))
        elif len(totalShowsFollowed) == 10:
            showNumberBadge = "Following 10 Shows!"
            cursor5 = db.cursor()
            cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, showNumberBadge))
        elif len(totalShowsFollowed) == 15:
            showNumberBadge = "Following 15 Shows!"
            cursor5 = db.cursor()
            cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, showNumberBadge))
        elif len(totalShowsFollowed) == 20:
            showNumberBadge = "Following 20 Shows!"
            cursor5 = db.cursor()
            cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, showNumberBadge))
        elif len(totalShowsFollowed) == 25:
            showNumberBadge = "Following 25 Shows!"
            cursor5 = db.cursor()
            cursor5.execute("insert into badges(username, badges)values(%s,%s)", (name, showNumberBadge))
        db.commit()
        return render_template('addedNotification.html',data=data,newVar=new_count)
    except:
        return render_template('error.html')


@app.route('/showSearch')
def nprForm():
    return render_template('showSearch.html')


@app.route('/deleteShow', methods=['post', 'get'])
def deleteshow():
    name = session["username"]
    random = request.form["random"]
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
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
    db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='CLEARDB_us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
    cursor2 = db.cursor2()
    cursor2.execute("select showName, showEpisode, episodeCount from showData where username='" + name + "'")
    newVar = cursor2.fetchall()
    print newVar
    return  render_template('shows.html')

# where username='" + name + "' and showName='" + showName + "'" #

#### Show Update ###########

@app.route('/updateShow', methods=['post', 'get'])
def updateshow():
    try:
        name = session["username"]
        title = request.form["title"]
        season = request.form['season']
        episode = request.form['episode']
        url = "http://www.omdbapi.com/?t=" + title +"&Season="+ season + "&Episode=" + episode +"&r=json"
        url = url.replace(" ","%20")
        loadurl = urllib.urlopen(url)
        data = json.loads(loadurl.read().decode(loadurl.info().getparam('charset') or 'utf-8'))
        episodedata = data['Episode']
        eD = int(episodedata)
        titledata = data['Title']
        seasondata= data['Season']
        plotdata = data['Plot']
        airdatedata = data['Released']
        db = mysql.connector.connect(user='b31545577f01ed', password='7bc97660',host='us-cdbr-iron-east-04.cleardb.net', database='heroku_0762eace2527e49')
        cursor = db.cursor()
        cursor.execute("update showData set showTitle=%s, showSeason=%s, showEpisode=%s, plot=%s, airDate=%s where showName='" + title + "' and username='" + name  + "'", (titledata, seasondata, episodedata, plotdata, airdatedata ))
        cursor2 = db.cursor()
        cursor2.execute("select showEpisode, episodeCount, plot, airDate from showData where showName='" + title + "'")
        new_count = cursor2.fetchall()
        cursor3 = db.cursor()
        cursor3.execute("select episodeCount from showData where showName='" + title + "'")
        testvar = cursor3.fetchone()
        tE = testvar[0]
        if eD == tE:
            badge = "You have completed season '" + season + "' of '" + title + "'"
            cursor3 = db.cursor()
            cursor3.execute("insert into badges(username, showSeason, showName, badges)values(%s,%s,%s,%s)", (name, season, title, badge))
        db.commit()
        return render_template('addedNotification.html',data=data, newVar=new_count)
    except:
        return render_template('error.html')


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