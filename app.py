from flask import Flask, jsonify, render_template, request, session, url_for, redirect, abort
import pymysql.cursors
import requests
import os, hashlib

app = Flask(__name__)
app.config['GOOGLEMAPS_KEY'] = "AIzaSyByFsKyIG7yUKCfYYXP7fsZ17_UhyrVxV8"

search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
details_url = "https://maps.googleapis.com/maps/api/place/details/json"
#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 3308,
                       user='root',
                       password='',
                       db='SP',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    hashed = hashlib.md5(password.encode()).hexdigest()
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM person WHERE username = %s and password = %s'
    cursor.execute(query, (username, hashed))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('main'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']
    hashed = hashlib.md5(password.encode()).hexdigest()
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM person WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO person (username, password, firstName,\
               lastName, email) VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, hashed, firstName,\
               lastName, email))
        conn.commit()
        cursor.close()
        return render_template('home.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/US_map')
def hotspot():
    return render_template('Hotspot.html')

@app.route('/main')
def main():
    user = session['username']
    return render_template('main.html', username=user)

@app.route('/game')
def play():
    return render_template('game.html')

@app.route('/checklist', methods=['GET', 'POST'])
def index():
    if request.method == 'POST': 
        res = request.form.getlist('checkbox')
        result = len(res)
        return render_template('result.html', result=result)
    return render_template('checklist.html')

#create vaccine Centers Class
class Center:
    def __init__(self,key,name,lat,lng):
        self.key = key
        self.name = name
        self.lat = lat
        self.lng = lng

centers = {Center('wp', 'Walgreens Pharmacy', 40.69342896732124, -73.97107067334586)}

centers_key = {center.key: center for center in centers}

@app.route('/vaccineCenters', methods=["GET"])
def map():
    return render_template('vaccineCenters.html')

@app.route("/sendRequest/<string:query>")
def results(query):
    search_payload  = {"key": "AIzaSyByFsKyIG7yUKCfYYXP7fsZ17_UhyrVxV8", "query": query}
    search_req = requests.get(search_url, params=search_payload)
    search_json = search_req.json()
    print(search_json)
    place_id = search_json["results"][0]["place_id"]

    details_payload = {"key":key, "placeid":place_id}
    details_resp = requests.get(details_url, params=details_payload)
    details_json = details_resp.json()

    url = details_json["result"]["url"]
    return jsonify({'result' : url})

app.secret_key = 'some key that you will never guess'
# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
