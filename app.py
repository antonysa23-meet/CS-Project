from flask import Flask, flash, request, redirect, url_for, render_template
from flask import session as login_session
import pyrebase
import urllib.request
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
 
UPLOAD_FOLDER = 'static/uploads/'

firebaseConfig = {
  'apiKey': "AIzaSyCyVvJYWy3ZmhBsbhRSqlN1xhYbTP0Fr4A",
  'authDomain': "blwit-69bcd.firebaseapp.com",
  'databaseURL': "https://blwit-69bcd-default-rtdb.firebaseio.com",
  'projectId': "blwit-69bcd",
  'storageBucket': "blwit-69bcd.appspot.com",
  'messagingSenderId': "369453153109",
  'appId': "1:369453153109:web:21f2ece7a404513abc8ddc",
  'databaseURL':'https://blwit-69bcd-default-rtdb.firebaseio.com/'
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
 
app.config['SECRET_KEY'] = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/home', methods=['POST','GET'])
def home():
	user = ""
	user = (db.child("Users").child(login_session['user']['localId']).get().val())['username']
	return render_template('home.html', username = user)
 
@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
       username = request.form['username']
       email = request.form['email']
       password = request.form['password']
       fullname = request.form['fullname']
       bio = request.form['bio']
       try:
           login_session['user'] = auth.create_user_with_email_and_password(email, password)
           user = {"fullname": fullname, "email": email, 'username':username, 'password': password}
           db.child("Users").child(login_session['user']
           ['localId']).set(user)
           return redirect(url_for('home'))
       except:
           return redirect(url_for('signup'))
    return render_template("signup.html")


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
       email = request.form['email']
       password = request.form['password']
       try:
           login_session['user'] = auth.sign_in_with_email_and_password(email, password)
           return redirect(url_for('home'))
       except:
           error = "Authentication failed"
           return redirect(url_for('signin'))
    return render_template("signin.html")

@app.route('/signout')
def signout():
	login_session['user'] = None
	auth.current_user = None
	return redirect(url_for('signin'))


@app.route('/upload', methods=['POST', 'GET'])
def upload_image():
	if request.method == 'POST':
		if login_session['user'] != None:
		    print('test')
		    print(request.files)
		    if 'file' not in request.files:
		        flash('No file part')
		        return redirect(request.url)
		    file = request.files['file']
		    if file and allowed_file(file.filename):
		        filename = secure_filename(file.filename)
		        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		        now = datetime.now()
		        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
		        user = db.child("Users").child(login_session['user']['localId']).get().val()['username']
		        post = {"name": filename, "title": request.form['title'], "text": request.form['text'], 'time' : dt_string, 'user':user, 'likes' : 0, 'dislikes': 0}
		        db.child("posts").push(post)
		             
		        return redirect(url_for('posts'))
		    else:
		        flash('Allowed image types are - png, jpg, jpeg, gif')
		        return redirect(request.url)
		else:
			return 'NOT SIGNED IN'
	else:
		return render_template('upload.html')

@app.route('/posts')
def posts():
	dic = db.child('posts').get().val()
	return render_template('posts.html', dic = dic)
@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/add_like/<string:item>', methods=['GET', 'POST'])
def add_like(item):
    if request.method == 'POST':
        likes = {'likes' : db.child('posts').child(item).get().val()['likes'] + 1}
        db.child("posts").child(item).update(likes)
        return redirect(url_for('posts'))

@app.route('/add_dislike/<string:item>', methods=['GET', 'POST'])
def add_dislike(item):
    if request.method == 'POST':
        likes = {'dislikes' : db.child('posts').child(item).get().val()['dislikes'] + 1}
        db.child("posts").child(item).update(likes)
        return redirect(url_for('posts'))

@app.route('/me')
def me():
	username =db.child("Users").child(login_session['user']['localId']).get().val()['username']
	password = db.child("Users").child(login_session['user']['localId']).get().val()['password']
	email = db.child("Users").child(login_session['user']['localId']).get().val()['email']
	fullname = db.child("Users").child(login_session['user']['localId']).get().val()['fullname']
	return render_template('me.html', username = username, password = password, email = email, fullname = fullname)

if __name__ == "__main__":
    app.run(debug=True)