from loader import loader

def main():

    #top_10()                    #funcional
    #personalized_theam_loader() #funcional
    users_colab()               #funcional
    #language_filter()           #funcional
    #best_20Peers()              #funcional
    #cold_start()                #funcional

def top_10():
    l = loader()
    csv = l.orderedLoader("movies_metadata.csv");
    print(csv[:10])

def personalized_theam_loader():
    l = loader()
    userId = 10
    preferences = l.theme_loader(userId,"small_ratings.csv","movies_metadata.csv")
    print("\n\n##-------## Preparing Response ##-------##\n\n")
    print(preferences[:10])

def users_colab():
    l = loader()
    col = l.colab_filtering("small_ratings.csv","movies_metadata.csv")
    print(col[:10])


def language_filter():
    l = loader()
    language = 'English'
    preferences = l.movie_per_language(language,"movies_metadata.csv")
    print(preferences[:10])


def best_20Peers():
    l = loader()
    userId = 10
    x = l.best_20Peers(userId,"small_ratings.csv","movies_metadata.csv")
    print(x[:10])

def cold_start():
    l = loader()
    user_preferences = ['1','0','0','1','0','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1']
    preferences = l.cold_start_users(user_preferences,'movies_metadata.csv')
    print(preferences[:10])

if __name__ == "__main__":
  main()
