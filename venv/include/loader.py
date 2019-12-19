import csv
import operator
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

    def orderedLoader(self, path):
        ifile = open(path, "r")
        reader = csv.reader(ifile, delimiter=",")
        sort = sorted(reader, key=operator.itemgetter(14), reverse=True)
        return sort[1:11]

    # carrega ratings de um utilizador
    def user_ratings_loader(self, userId, path):
        ifile = open(path, "r")
        a = [];
        rowCount = 0
        reader = csv.reader(ifile, delimiter=",")
        for row in reader:
            if rowCount == 0:
                rowCount += 1
            elif int(row[0]) == userId:
                a.append(row)
        return a

    # comprara igualdade de 2 arrays
    def comparacao_percentual(self, arr1, arr2):
        count1 = 0.0
        countEqual = 0.0
        for i in range(1, len(arr2)):
            count1 += 1.0
            if arr1[16 + i] == arr2[i]:
                countEqual += 1.0
        if (countEqual / count1) == 1.0: return True
        return False

    def comparacao_percentual_1(self, array, arr2):
        count1 = 0.0
        countEqual = 0.0
        for i in range(0, len(array)):
            count1 += 1.0
            if arr2[i] == array[i]:
                countEqual += 1.0
        if (countEqual / count1) == 1.0: return True
        return False    
    
    def best10_theme_movies(self, movieIds, path):
        with open(path, "r") as ifile:
            reader = csv.reader(ifile, delimiter=",")
            rowCount = 0;
            passed = True
            filmes = films = []
            for row in reader:
                if rowCount == 0:
                    rowCount += 1
                elif row[2] in movieIds:
                    rowCount = 1
                    with open(path, "r") as ifile2:
                        reader2 = csv.reader(ifile2, delimiter=",")
                        for row2 in reader2:
                            if rowCount == 1:
                                rowCount += 1
                            elif self.comparacao_percentual(row2, row[16:36]):  # se tiver os mesmos temas adiciona
                                films.append((row2[2], row2[13], row2[14]))
        print("\n\n##----------## Removing repeated ##----------##\n\n");
        tam = len(films)
        rowCount = 0
        films.sort(key=lambda tup: tup[2], reverse=True)
        for (a, b, c) in films:
            if a not in movieIds:
                movieIds.append(a)
                filmes.append((a, b, c))
            rowCount += 1
            if rowCount == tam: break
        return filmes

    def theme_loader(self, userId, path_user, path_movies):
        # guarda userId,movieId,rating,timestamp
        print("\n\n\tRetrieving User Preferences:\n\n")
        user_preferences = self.user_ratings_loader(userId, path_user)

        print("##----------------## divisor ##----------------##")
        print("     Retrieving User Probable Preferences:")
        good_films = res = []
        for rating in user_preferences:
            if float(rating[2]) >= 4:  # gostou
                good_films.append(rating[1])
        return self.best10_theme_movies(good_films, path_movies)

    def colab_filtering(self, users_path, movies_path):

        column_names = ['userId', 'movieId', 'rating', 'timestamp']
        movies_column_names = ['movieId', 'original_title']
        user_ratings = pd.read_csv(users_path, sep=",", names=column_names)
        user_ratings['rating'] = pd.to_numeric(user_ratings['rating'], errors='coerce')
        user_ratings['movieId'] = pd.to_numeric(user_ratings['movieId'], errors='coerce')

        # creating dataframe with 'rating' && count values
        ratings = pd.DataFrame(user_ratings.groupby('movieId')['rating'].mean())
        ratings['num of ratings'] = pd.DataFrame(user_ratings.groupby('movieId')['rating'].count())

        ratings.sort_values('rating', ascending=False)

        movies = pd.read_csv(movies_path, sep=",", usecols=movies_column_names)
        movies['movieId'] = pd.to_numeric(movies['movieId'], errors='coerce')

        data = ratings.merge(movies, on='movieId', how='left')

        res = data.sort_values(['num of ratings', 'rating'], ascending=[False, False]).head(20).dropna()
        return res[0:10]

    def movie_per_language(self, language, movies_path):

        movies_column_names = ['original_title', 'vote_average', language]
        allmovies = pd.read_csv(movies_path, sep=",", usecols=movies_column_names)
        allmovies[language] = pd.to_numeric(allmovies[language], errors='coerce')
        movies = allmovies[(allmovies[language] == 1)]
        movies.sort_values('vote_average', ascending=False)
        res = movies.dropna().head(10)
        return res

    def cold_start(self,array,path):
        with open(path, "r") as ifile:
            reader = csv.reader(ifile, delimiter=",")
            rowCount = 0;
            passed = True
            filmes = films = []
            for row in reader:
                #print(row)
                if rowCount == 0:
                    rowCount += 1
                elif self.comparacao_percentual_1(array, row[16:36]):  # se tiver os mesmos temas adiciona
                        #print(row)
                    films.append((row[2], row[13], row[14]))
        films.sort(key=lambda tup: tup[2], reverse=True)
        return films
