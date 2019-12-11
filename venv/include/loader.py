import csv
import operator
import os
import pandas as pd

#         adult [0];  "homepage"   [1]; "id"       [2]; "imdb_id" [3]; "original_language"  [4]; "original_title"  [5]; "overview"      [6];"popularity" [7]
# "poster_path" [8]; "release_date"[9];"runtime"  [10]; "status" [11]; "tagline"           [12]; "title"          [13]; "vote_average" [14];"vote_count" [15]
# "Animation"  [16]; "Adventure"  [17];"Romance"  [18]; "Comedy" [19]; "Action"            [20]; "Family"         [21]; "History"      [22];"Drama"      [23]
#  "Crime"     [24]; "Fantasy"    [25];"Si-Fi"    [26];"Thriller"[27]; "Music"             [28]; "Horror"         [29]; "Documentary"  [30];"Mystery"    [31]
# "Western"    [32]; "TV Movie"   [33];"War"      [34];"Foreign" [35]; "ColectionId"       [36]; "Colection"      [37]; "English"      [38];"Deutsh"     [39]
# "Français"  [40]; "Espanhol"   [41];
class loader:

  def __init__(self):
      self.path = None

  def orderedLoader(self,path):
      ifile = open(path, "r")
      reader = csv.reader(ifile, delimiter=",")
      sort = sorted(reader, key=operator.itemgetter(14),reverse=True)
      return sort[1:11]

  #carrega ratings de um utilizador
  def user_ratings_loader(self,userId,path):
      ifile = open(path, "r")
      a = []; rowCount = 0
      reader = csv.reader(ifile, delimiter=",")
      for row in reader:
          if rowCount == 0: rowCount += 1
          elif int(row[0]) == userId:
              a.append(row)
      return a

  def comparacao_percentual(self,arr1,arr2):
      count1 = 0.0
      countEqual = 0.0
      for i in range (1,len(arr2)):
              count1 += 1.0
              if arr1[16+i] == arr2[i]:
                  countEqual += 1.0
      if (countEqual/count1) ==1.0: return True
      return False

  def best10_theme_movies(self,movieIds,path):
      with open(path, "r") as ifile:
          reader = csv.reader(ifile, delimiter=",")
          rowCount = 0;
          passed  = True
          filmes = films = res = ids = []
          for row in reader:
              if rowCount == 0: rowCount +=1
              elif row[2] in movieIds:
                  rowCount = 1
                  with open(path, "r") as ifile2:
                      reader2 = csv.reader(ifile2, delimiter=",")
                      for row2 in reader2:
                          if rowCount == 1: rowCount += 1
                          elif self.comparacao_percentual(row2, row[16:36]):  # se semelhança for superior a 60% adiciona
                              films.append((row2, row2[14],row[2]))
      print("Removing repeated");
      passed = True
      print(len(films))
      rowCount = 0
      for (a, b, c) in films:
          if c in ids:
            rowCount +=0
          else:
              ids.append(c)
              filmes.append((a,b))
          rowCount += 1
          if rowCount == 100: print("DEVIA TER ACABADO    100")
          elif rowCount == 1000: print("DEVIA TER ACABADO   1000")
          elif rowCount == 10000: print("DEVIA TER ACABADO 10000")
          elif rowCount == 20000: print("DEVIA TER ACABADO 20000")
          elif rowCount == 30000: print("DEVIA TER ACABADO 30000")
          elif rowCount == 40000: print("DEVIA TER ACABADO 40000")
          elif rowCount == 50000: print("DEVIA TER ACABADO 50000")
          elif rowCount == 60000: print("DEVIA TER ACABADO 60000")
          elif rowCount == 70000: print("DEVIA TER ACABADO 70000")
          elif rowCount == 80000: print("DEVIA TER ACABADO 80000")
          elif rowCount == 90000: print("DEVIA TER ACABADO 90000")
      print("fim")
      srt = sorted(filmes,key = lambda x: x[1],reverse=True)
      for(a,b) in srt:
          res.append(a)
      return res[1:11]


  def theme_loader(self,userId,path_user,path_movies):
      #guarda userId,movieId,rating,timestamp
      print("Retrieving User Preferences:")
      user_preferences = self.user_ratings_loader(userId,path_user)

      print("##----------------## divisor ##----------------##")
      print("Retrieving User Probable Preferences:")
      good_films = res = []
      for rating in user_preferences:
          if float(rating[2]) >= 4: # gostou
              good_films.append(rating[1])
      return self.best10_theme_movies(good_films,path_movies)


  def colab_filtering(self,users_path,movies_path):

      column_names = ['userId','movieId','rating','timestamp']
      movies_column_names = ['movieId','original_title']
      user_ratings = pd.read_csv(users_path,sep=",",names=column_names)
      user_ratings['rating'] = pd.to_numeric(user_ratings['rating'],errors='coerce')
      user_ratings['movieId'] = pd.to_numeric(user_ratings['movieId'], errors='coerce')

      # creating dataframe with 'rating' && count values
      ratings = pd.DataFrame(user_ratings.groupby('movieId')['rating'].mean())
      ratings['num of ratings'] = pd.DataFrame(user_ratings.groupby('movieId')['rating'].count())

      ratings.sort_values('rating', ascending=False)

      movies = pd.read_csv(movies_path,sep=",",usecols=movies_column_names)
      movies['movieId'] = pd.to_numeric(movies['movieId'], errors='coerce')

      data = ratings.merge(movies,on='movieId',how='left')

      res = data.sort_values(['num of ratings','rating'],ascending=[False,False]).head(20).dropna()
      return res[0:10]


