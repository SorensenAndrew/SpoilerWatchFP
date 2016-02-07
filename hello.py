import os
from rauth.service import OAuth2Service
from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask import session
from flask import url_for
from flask import flash

FB_CLIENT_ID = '231849067150204'
FB_CLIENT_SECRET = 'fd4acef5c95ed3c3a20300b9065ae36a'

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = "4321"

graph_url = 'https://graph.facebook.com/'
facebook = OAuth2Service(name='facebook',
                         authorize_url='https://www.facebook.com/dialog/oauth',
                         access_token_url=graph_url + 'oauth/access_token',
                         client_id=app.config['FB_CLIENT_ID'],
                         client_secret=app.config['FB_CLIENT_SECRET'],
                         base_url=graph_url)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/facebook/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    params = {'redirect_uri': redirect_uri}
    return redirect(facebook.get_authorize_url(**params))


@app.route('/facebook/authorized')
def authorized():
    # check to make sure the user authorized the request
    if not 'code' in request.args:
        flash('You did not authorize the request')
        return redirect(url_for('index'))

    # make a request for the access token credentials using code
    redirect_uri = url_for('authorized', _external=True)
    data = dict(code=request.args['code'], redirect_uri=redirect_uri)

    session = facebook.get_auth_session(data=data)

    # the "me" response
    me = session.get('me').json()

    User.get_or_create(me['username'], me['id'])

    flash('Logged in as ' + me['name'])
    return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

