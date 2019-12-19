from loader import loader

def main():

    #top_10()                    #funcional
    #personalized_theam_loader() #funcional
    #users_colab()               #funcional
    language_filter()

def top_10():
    l = loader()
    csv = l.orderedLoader("movies_metadata.csv");
    print(csv)

def personalized_theam_loader():
    l = loader()
    userId = 10
    preferences = l.theme_loader(userId,"small_ratings.csv","movies_metadata.csv")
    print("\n\n##-------## Preparing Response ##-------##\n\n");
    for i in range(1,11):
        print(preferences[i])

def users_colab():
    l = loader()
    l.colab_filtering("small_ratings.csv","movies_metadata.csv")


def language_filter():
    l = loader()
    language = 'English'
    preferences = l.movie_per_language(language,"movies_metadata.csv")
    print(preferences)

def cold_start():    
    l = loader()
    #language = 'English'
    preferences = l.cold_start(['1','0','0','1','0','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],'movies_metadata.csv')
    print(preferences[:10])

if __name__ == "__main__":
  main()
