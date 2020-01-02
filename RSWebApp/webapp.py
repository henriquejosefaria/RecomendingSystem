from flask import Flask, render_template, url_for, flash, redirect, json, request
from forms import RegistrationForm, LoginForm
from flask_pymongo import PyMongo
import os
import pandas as pd
from itertools import groupby   
import webbrowser
from flask_jsglue import *

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/webAppDB"
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
mongo = PyMongo(app)
global user_global_id
user_global_id = "a"

@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html", title="Home")
@app.route("/personalHome")
def personalHome():
	return render_template("personalHome.html", title="personalHome")

def autenticate(email,password,form):
	global user_global_id
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
Top 10 filmes mais bem cotados (Cold-Case Users)
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
Filtros Colaborativos Baseados em Utilizadores
Users Colaborative Filtering (se não tem filmes vistos usa coldSart Users)
'''
@app.route("/colab_filtering", methods=['GET', 'POST'])
def colab_filtering():
	user = mongo.db.users.find_one({"email": user_global_id})
	#Cold Start Users
	if mongo.db.userRating.find({"userId": user["id"]}).count() == 0:
		return top10_avg()
	moviesToCompare = mongo.db.userRating.find({"userId": user["id"]})
	similar = similar_film = filmes = []
	res = []
	res2 = []
	row = ten = 0
	passa = 0
	#Encontra pessoas que viram os mesmos filmes
	for mv in moviesToCompare:
		similar += mongo.db.userRating.find({"movieId": mv["movieId"]})
	for s in similar:
			s["dif"] = abs(mv["rating"] - s["rating"])
	df = pd.DataFrame(similar)
	new = df.groupby(['userId'], as_index=False)["dif"].sum().to_dict('r')
	similar2 = sorted(new,key=lambda x: x['dif'])
	#Lista dos filmes vistos pelos 10 utilizadores mais parecidos
	for s in similar2:
		user_id = s['userId']
		if row == 0:
			row = s["userId"]
		elif ten > 10:
			break
		elif user_id != row:
			filmes = mongo.db.userRating.find({"userId": row,"movieId": {"$lt":1000}},{"movieId":1,"_id":0}).limit(15)
			for f in filmes:
					film = mongo.db.films.find({"movieId": f["movieId"]})
					if film != None:
						res += film
						ten +=1;
			for r in res:
				passa = 0
				for m in moviesToCompare:
					if r["movieId"] == m["movieId"]:
						passa = 1
						break
				if passa == 0:
					res2 += r
				else:
					ten -=1

			row = s["userId"]
			ten += 1
		else:
			row = row
	return render_template("personalHome.html", title="personalHome",films = res[:15])

'''
Métodos Baseados em Memória
Filtros Colaborativos Baseados em itens
'''
@app.route("/mem_based", methods=['GET', 'POST'])
def memBased():
	best15 = mongo.db.userRating.find({"movieId": {"$lt": 1000}},{"movieId":1,"rating":1,"_id":0}).sort([("rating",-1)]).limit(15)
	res = []
	ratings = []
	for movie in best15:
		ratings.append(movie["rating"])
		res += mongo.db.films.find({"movieId": movie["movieId"]})
	return render_template("personalHome.html", title="personalHome",films = res[:15],ratings = ratings)

'''
Films Cold-Case Start
'''
def loadNew():
	films = mongo.db.films.find({"userId": {"$in":[1,10]}})
	res = []
	for f in films:
		if not isinstance(f["title"], int):
			res += f
	return res[:15]

'''
Sistemas de Recomendação Baseados em Conteúdo
Film recomendation based on watched films by the user that he liked 3+
'''
@app.route("/urFilmBasedList", methods=['GET', 'POST'])
def filmWatchBased():
	user = mongo.db.users.find_one({"email":user_global_id})
	moviesSeen = mongo.db.userRating.find({"userId": user["id"], "rating": {"$gt":2}},{"movieId":1,"_id":0})
	genresAgregation = []
	genres = []
	films = []
	rec = []
	res = []
	for m in moviesSeen:
		genresAgregation += mongo.db.films.find({"movieId": m["movieId"]})
	for g in genresAgregation:
		if g["Animation"] == 1 and "Animation" not in genres:
			genres.append("Animation")
		if g["Adventure"] == 1 and "Adventure" not in genres:
			genres.append("Adventure")
		if g["Romance"] == 1 and "Romance" not in genres:
			genres.append("Romance")
		if g["Comedy"] == 1 and "Comedy" not in genres:
			genres.append("Comedy")
		if g["Action"] == 1 and "Action" not in genres:
			genres.append("Action")
		if g["Family"] == 1 and "Family" not in genres:
			genres.append("Family")
		if g["History"] == 1 and "History" not in genres:
			genres.append("History")
		if g["Drama"] == 1 and "Drama" not in genres:
			genres.append("Drama")
		if g["Crime"] == 1 and "Crime" not in genres:
			genres.append("Crime")
		if g["Fantasy"] == 1 and "Fantasy" not in genres:
			genres.append("Fantasy")
		if g["Sience Fiction"] == 1 and "Sience Fiction" not in genres:
			genres.append("Sience Fiction")
		if g["Thriller"] == 1 and "Thriller" not in genres:
			genres.append("Thriller")
		if g["Music"] == 1 and "Music" not in genres:
			genres.append("Music")
		if g["Horror"] == 1 and "Horror" not in genres:
			genres.append("Horror")
		if g["Documentary"] == 1 and "Documentary" not in genres:
			genres.append("Documentary")
		if g["Mystery"] == 1 and "Mystery" not in genres:
			genres.append("Mystery")
		if g["Western"] == 1 and "Western" not in genres:
			genres.append("Western")
		if g["TV Movie"] == 1 and "TV Movie" not in genres:
			genres.append("TV Movie")
		if g["War"] == 1 and "War" not in genres:
			genres.append("War")
		if g["Foreign"] == 1 and "Foreign" not in genres:
			genres.append("Foreign")
	for g in genres:
		size = 0
		films = mongo.db.films.find({g: 1}).limit(15)
		for f in films:
			if f["movieId"] not in res and f["movieId"] not in moviesSeen:
				res.append(f["movieId"])
				rec.append(f)
				size +=1;
			if size == 2:
				break
	return render_template("personalHome.html", title="personalHome",films = rec[:15])

'''
Sistemas de recomendação baseados em restrições
Search Bar 
'''
@app.route("/search", methods=['GET','POST'])
def search():
	if request.method == 'POST': 		
		text = request.form['search']
		if mongo.db.films.find({text: 1}).count() > 0:
			films = mongo.db.films.find({text: 1})
			return render_template("personalHome.html", title="personalHome",films = films[:15])
		elif text == "False" or text == "True":
			if mongo.db.films.find({"adult": {"$regex": text}}).count() > 0:
				films = mongo.db.films.find({"title": {"$regex": text}})
				return render_template("personalHome.html", title="personalHome",films = films[:15])
			elif mongo.db.films.find({"title": {"$regex": text}}).count() > 0:
				films = mongo.db.films.find({"title": {"$regex": text}})
				return render_template("personalHome.html", title="personalHome",films = films[:15])
			elif mongo.db.films.find({"original_title": {"$regex": text}}).count() > 0:
				films = mongo.db.films.find({"original_title": {"$regex": text}})
				return render_template("personalHome.html", title="personalHome",films = films[:15])
			elif mongo.db.films.find({"tagline": {"$regex": text}}).count() > 0:
				films = mongo.db.films.find({"tagline": {"$regex": text}})
				return render_template("personalHome.html", title="personalHome",films = films[:15])
			elif mongo.db.films.find({"original_language": {"$regex": text}}).count() > 0:
				films = mongo.db.films.find({"original_language": {"$regex": text}})
				return render_template("personalHome.html", title="personalHome",films = films[:15])
			else:
				films = loadNew()
				return render_template("personalHome.html", title="personalHome",films = [])
		else:
			if mongo.db.films.find({"title": {"$regex": text}}).count() > 0:
				films = mongo.db.films.find({"title": {"$regex": text}})
				return render_template("personalHome.html", title="personalHome",films = films[:15])
			elif mongo.db.films.find({"original_title": {"$regex": text}}).count() > 0:
				films = mongo.db.films.find({"original_title": {"$regex": text}})
				return render_template("personalHome.html", title="personalHome",films = films[:15])
			elif mongo.db.films.find({"tagline": {"$regex": text}}).count() > 0:
				films = mongo.db.films.find({"tagline": {"$regex": text}})
				return render_template("personalHome.html", title="personalHome",films = films[:15])
			elif mongo.db.films.find({"original_language": {"$regex": text}}).count() > 0:
				films = mongo.db.films.find({"original_language": {"$regex": text}})
				return render_template("personalHome.html", title="personalHome",films = films[:15])
			else:
				films = loadNew()
				return render_template("personalHome.html", title="personalHome",films = [])
	else:
		films = loadNew()
		return render_template("personalHome.html", title="personalHome",films = [])

@app.route("/contacts", methods=['GET','POST'])
def contacts():
	return render_template("contacts.html", title="Contacts")


@app.route("/homepage", methods=['GET','POST'])
def basepage():
	submitScore()
	films = loadNew()
	return render_template("personalHome.html", title="personalHome",films = films)

@app.route("/rate/<filmId>", methods=['GET','POST'])
def rate(filmId):
	this_userId = mongo.db.users.find({"email": user_global_id})
	return render_template("rate.html", title="Rate",filmId = filmId, userId = this_userId)

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
	films = mongo.db.films.find({ genre : 1}).sort([("release_date",-1)])
	res = []
	for f in films:
		if not isinstance(f["title"], int):
			res += mongo.db.films.find(f)
	return render_template("personalHome.html", title="personalHome",films = res[:15])


@app.route("/yearSearch/<year>", methods=['GET', 'POST'])
def yearSearch(year):
	mystr = str(year)
	films = mongo.db.films.find({"release_date" :{"$regex": mystr}}).sort([("vote_average",-1),("release_date",-1)])
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

if __name__ == "__main__":
	app.run(debug=True)