__author__ = 'AndrewSorensen'

from flask import Flask
from flask import render_template
from flask import redirect
app = Flask(__name__)

@app.route('/')
def index():
    return redirect('/main')


@app.route('/main', methods=['post','get'])
def main():
    return render_template('main.html')
if __name__ == '__main__':
    app.run()