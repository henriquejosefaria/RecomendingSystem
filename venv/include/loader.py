import csv
import operator
import pandas as pd
from pymongo import MongoClient
pd.set_option('display.max_columns', None)
cliente = MongoClient('mongodb://localhost:27017/')

dados = cliente['webAppDB']

filmsList = dados.films

#         adult [0];  "homepage"   [1]; "id"       [2]; "imdb_id" [3]; "original_language"  [4]; "original_title"  [5]; "overview"      [6];"popularity" [7]
# "poster_path" [8]; "release_date"[9];"runtime"  [10]; "status" [11]; "tagline"           [12]; "title"          [13]; "vote_average" [14];"vote_count" [15]
# "Animation"  [16]; "Adventure"  [17];"Romance"  [18]; "Comedy" [19]; "Action"            [20]; "Family"         [21]; "History"      [22];"Drama"      [23]
#  "Crime"     [24]; "Fantasy"    [25];"Si-Fi"    [26];"Thriller"[27]; "Music"             [28]; "Horror"         [29]; "Documentary"  [30];"Mystery"    [31]
# "Western"    [32]; "TV Movie"   [33];"War"      [34];"Foreign" [35]; "ColectionId"       [36]; "Colection"      [37]; "English"      [38];"Deutsh"     [39]
# "Français"  [40]; "Espanhol"   [41];
class loader:

    def __init__(self):
        self.path = None

    # Devolve os 10 filmes mais bem cotados por especialistas de sempre
    def orderedLoader(self, path):
        ifile = open(path, "r")
        reader = csv.reader(ifile, delimiter=",")
        sort = sorted(reader, key=operator.itemgetter(14), reverse=True)
        return sort[1:11]

    # carrega ratings de um utilizador especifico
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

    # comprara igualdade de 2 arrays de inteiros (usado para verificar se dois filmes são compatíveis em gênero)
    def comparacao_percentual(self, array, arr2):
        count1 = 0.0
        countEqual = 0.0
        for i in range(0, len(array)):
            count1 += 1.0
            if arr2[i] == array[i]:
                countEqual += 1.0
        if (countEqual / count1) == 1.0: return True
        return False    


    # Procura os 10 filmes mais bem cotados cujo género seja o mesmo dos filmes vistos pelo utilizador e dos quais este gostou

    # Escolhe os 10 filmes mais bem classificados dos mesmos gêneros dos quais o utilizador gosta
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
                            elif self.comparacao_percentual(row2[16:36], row[16:36]):  # se tiver os mesmos temas adiciona
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

    # Seletor dos filmes vistos pelo utilizador dos quais este gostou (>= 4)
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

    #Carrega os utilizadores da base de dados
    def users_loader(self,users_path):
        column_names = ['userId', 'movieId', 'rating', 'timestamp']
        user_ratings = pd.read_csv(users_path, sep=",", names=column_names)
        user_ratings['rating'] = pd.to_numeric(user_ratings['rating'], errors='coerce')
        user_ratings['movieId'] = pd.to_numeric(user_ratings['movieId'], errors='coerce')
        return user_ratings

    #Carrega o id e o titulo dos filmes da base de dados
    def movies_loader(self,movies_path):
        movies_column_names = ['movieId', 'original_title']
        movies = pd.read_csv(movies_path, sep=",", usecols=movies_column_names)
        movies['movieId'] = pd.to_numeric(movies['movieId'], errors='coerce')
        return movies

       # Coleciona todos os filmes vistos por todos os utilizadores e apresenta os 10 mais bem cotados por estes
    def colab_filtering(self, users_path, movies_path):

        user_ratings = self.users_loader(users_path)

        # creating dataframe with 'rating' && count values
        ratings = pd.DataFrame(user_ratings.groupby('movieId')['rating'].mean())
        ratings['num of ratings'] = pd.DataFrame(user_ratings.groupby('movieId')['rating'].count())
        ratings.sort_values('rating', ascending=False)

        movies = self.movies_loader(movies_path)

        data = ratings.merge(movies, on='movieId', how='left')

        res = data.sort_values(['num of ratings', 'rating'], ascending=[False, False]).dropna()
        result = res[res.columns[3:4]]
        return result

    # Dada uma linguagem apresentam-se todos os filmes que estejam nessa linguagem
    def movie_per_language(self, language, movies_path):

        movies_column_names = ['original_title', 'vote_average', language]
        allmovies = pd.read_csv(movies_path, sep=",", usecols=movies_column_names)
        allmovies[language] = pd.to_numeric(allmovies[language], errors='coerce')
        movies = allmovies[(allmovies[language] == 1)]
        movies.sort_values('vote_average', ascending=False)
        res = movies.dropna()
        return res

    #se o filme estiver na lista retorna o rating dado pelo utilizador
    def same_movie(self, movie_id, user_preferences):
        for pref in user_preferences:
            if int(pref[1]) == movie_id:
                return pref[2]
        return -1

    #Encontra os 20 utilizadores com gostos mais similares ao utilizador alvo e faz uma sugestão dos melhores filmes vistos por estes outros utilizadores
    def best_20Peers(self, userId, users_path, movies_path):
        movies_column_names = ['movieId', 'original_title']
        # Carragar todos os utilizadores
        user_ratings = self.users_loader(users_path)
        #Carregar o utilizador alvo
        user_preferences = self.user_ratings_loader(userId, users_path)
        # Carregar todos os filmes
        movies = self.movies_loader(movies_path)
        # Construir o array de proximidade por distancia euclidiana
        single_users = user_ratings.groupby('userId')
        distEuc = []
        recomending_movies = []
        recmovies = []
        res = []
        for id, group in single_users:
            count = nCount = total = 0
            similar_user = -1
            for idx, ratings in group.iterrows():
                total += 1
                if similar_user == -1:
                    similar_user = ratings['userId']
                r = int(self.same_movie(ratings['movieId'], user_preferences))
                if (r > -1): #Se o utilizador viu um mesmo filme que o alvo vou calcular a distancia euclidiana das avaliações
                    count += abs(r - ratings['rating'])  # distancia euclidiana
                    nCount += 1
                elif ratings['rating'] > 2: #se não for um filme já visto pelo utilizador alvo adiciono-o para o poder recomendar
                    recomending_movies.append((similar_user, ratings['movieId']))
            if nCount > 0 & total != nCount:
                distEuc.append((similar_user, count / nCount))
        distEuc.sort(key=lambda tup: tup[1])
        #Filtra os filmes dos 20 utilizadores com os gostos mais parecidos com os do utilizador alvo
        for (user,rating) in distEuc[:20]:
            for (user_id,movie_id) in recomending_movies:
                if user_id == user: recmovies.append(movie_id)
        for id, movie in movies.iterrows():
            if movie['movieId'] in recmovies:
                res.append(movie['original_title'])
        return res

    #Dadas as preferências de gênero de um utilizador pesquisa os filmes que este mais poderá gostar
    def cold_start_users(self,array,path):
        filmes = []
        with open(path, "r") as ifile:
            reader = csv.reader(ifile, delimiter=",")
            rowCount = 0; films = []
            for row in reader:
                if rowCount == 0:
                    rowCount += 1
                elif self.comparacao_percentual(array, row[16:36]):  # se tiver os mesmos temas adiciona
                    films.append((row[2], row[13], row[14]))
        films.sort(key=lambda tup: tup[2], reverse=True)
        for (a, b, c) in films:
            filmes.append(b)
        return filmes

    # NOTA: De futuro atualizar formula e adicionar campo de número de vezes apresentado aos utilizadores.
    # Quanto mais apresentações deste filme foram feitas a pessoas mais oportunidades elas tiveram para o ver, se não o esclheram não é assim tão atrativo
    # para além disso filmes novos precisam de aparecer também

    # Carrega os filmes todos dos sem visualizações para o que tem maior número de visualizações
    def new_films_loader(self,movies_path):
        movies_column_names = ['original_title', 'vote_count']
        allmovies = pd.read_csv(movies_path, sep=",", usecols=movies_column_names)
        allmovies['vote_count'] = pd.to_numeric(allmovies['vote_count'], errors='coerce')
        movies = allmovies.sort_values(by='vote_count')
        return movies

    #         adult [0];  "homepage"   [1]; "id"       [2]; "imdb_id" [3]; "original_language"  [4]; "original_title"  [5]; "overview"      [6];"popularity" [7]
    # "poster_path" [8]; "release_date"[9];"runtime"  [10]; "status" [11]; "tagline"           [12]; "title"          [13]; "vote_average" [14];"vote_count" [15]
    # "Animation"  [16]; "Adventure"  [17];"Romance"  [18]; "Comedy" [19]; "Action"            [20]; "Family"         [21]; "History"      [22];"Drama"      [23]
    #  "Crime"     [24]; "Fantasy"    [25];"Si-Fi"    [26];"Thriller"[27]; "Music"             [28]; "Horror"         [29]; "Documentary"  [30];"Mystery"    [31]
    # "Western"    [32]; "TV Movie"   [33];"War"      [34];"Foreign" [35]; "ColectionId"       [36]; "Colection"      [37]; "English"      [38];"Deutsh"     [39]
    # "Français"  [40]; "Espanhol"   [41];
    # "userId", "movieId", "rating", "timestamp"
    def transfer(self,movies_path):
        ifile = open(movies_path, "r")
        users = csv.reader(ifile, delimiter=",")
        row = 0
        list = "["
        id = -1
        films = ""
        for user in users:
            print(user)
            '''
            if row == 0:
                row=0
            elif id == -1 and row > 0:
                id = user["userId"]
                films = "{" + user["movieId"] + "}"
            elif row == 60:
                break
            elif id == user["userId"]:
                films += ",{" + user["movieId"] + "," + user["rating"] + "}"
            else:
                string = "{\"userId\" : " + str(user["userId"]) + ", \"movieId\" :" + str(user["movieId"]),""str(user["movieId"]),""str(user["movieId"]),"","" "}"
                list += strin g
                print(string,"\n\n")
                if (row < 9):
                    list += ","
            row += 1
        list += "]"
        print(list)
        filmsList.insert_many(list)
            '''
