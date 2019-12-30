from flask import Flask, render_template, url_for, flash, redirect, json
from forms import RegistrationForm, LoginForm
from flask_pymongo import PyMongo
import os
import re

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/webAppDB"
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
mongo = PyMongo(app)
user_global_id = ""

@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html", title="Home")
@app.route("/personalHome")
def personalHome():
	return render_template("personalHome.html", title="personalHome")

def autenticate(email,password,form):
	if mongo.db.users.find({"email" : email, "password" : password}).count() > 0:
		flash('You have been logged in!', 'success')
		user_global_id = email
		films = mongo.db.films.find().sort([("vote_count",-1), ("release_date",-1)])
		res = []
		for f in films:
			if not isinstance(f["title"], int):
				res += mongo.db.films.find(f)
		return render_template("personalHome.html", title="personalHome",films = res[:10])
	else:
	    flash('Login unsuccessful. Please check credentials.', 'danger')
	return render_template('login.html', title='Login', form=form)

"""
Top 10 filmes mais bem cotados
"""
@app.route("/top10", methods=['GET', 'POST'])
def top10_avg():
	films = mongo.db.films.find().sort([("vote_average", -1)])
	res = []
	for f in films:
		if not isinstance(f["title"], int):
			res += mongo.db.films.find(f)
	return render_template("personalHome.html", title="personalHome",films = res[:10])

'''
Users Colaborative Filtering
'''
@app.route("/colab_filtering", methods=['GET', 'POST'])
def colab_filtering():
	user = mongo.db.user.find({"email": user_global_id})
	user_id = user["id"]
	usrRatings = mongo.db.userRating.find({"userId": user_id})
	users = mongo.db.userRating.find()
	#Encontra gajos que viram os mesmos filmes
	for usr in usrRatings:
		similar += mongo.db.userRating.find({"movieId" : usr["movieId"]})
	mostSimilar = sorted(similar, key=itemgetter('userId'))
	i = 0
	for key, value in itertools.groupby(similar, key=itemgetter('userId')):
		if i == 9: break
		i=i+1
		for v in value:
			films += mongo.db.userRatings.find({"userId": v["userId"]})
	for f in films:
		recFilms += mongo.db.films.find({"id" : f["movieId"]})
	res = []
	for f in recFilms:
		if not isinstance(f["title"], int):
			res +=  mongo.db.films.find(f)
	return render_template("personalHome.html", title="personalHome",films = res[:15])


def loadNew():
	films = mongo.db.films.find({"userId": {"$in":[1,10]}})
	res = []
	for f in films:
		if not isinstance(f["title"], int):
			res += f
	return res[:15]


@app.route("/login", methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.is_submitted():
		return autenticate(form.email.data,form.password.data,form)
	return render_template('login.html', title='Login', form=form)

def registerNewUser(username,email,password):
	user_global_id = email
	l = mongo.db.users.count() + 1
	mongo.db.users.insert({"id": l ,"user" : username, "email" : email, "password" : password})

def onlyOne(username,email):
	if mongo.db.users.find({"user" : username}).count() > 0:
		flash('That username is alredy in use try a diferent one!', 'fail')
		return False
	if mongo.db.users.find({"email" : email}).count() > 0:
		flash('That email is alredy in use try a diferent one!', 'fail')
		return False
	return True

@app.route("/genreSearch/<genre>", methods=['GET', 'POST'])
def genreSearch(genre):
	films = mongo.db.films.find({ genre : 1})
	res = []
	for f in films:
		if not isinstance(f["title"], int):
			res += mongo.db.films.find(f)
	return render_template("personalHome.html", title="personalHome",films = res[:15])


@app.route("/yearSearch/<year>", methods=['GET', 'POST'])
def yearSearch(year):
	mystr = str(year)
	films = mongo.db.films.find({"release_date" :{"$regex": mystr}})
	res = []
	for f in films:
		if not isinstance(f["title"], int):
			res +=  mongo.db.films.find(f)
	return render_template("personalHome.html", title="personalHome",films = res[:15])


@app.route("/register", methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.is_submitted() and form.password.data == form.confirm_password.data and onlyOne(form.username.data,form.email.data):
		registerNewUser(form.username.data,form.email.data,form.password.data)
		flash(f'Account created for { form.username.data }!', 'success')
		films = loadNew()
		return render_template("personalHome.html", title="personalHome",films = films)
	return render_template('register.html', title='Register', form=form)

@app.route("/about")
def about():
	return render_template("about.html")

if __name__ == "__main__":
	app.run(debug=True)