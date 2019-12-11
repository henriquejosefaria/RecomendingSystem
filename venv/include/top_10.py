from loader import loader

def main():
    # top_10()  # funcional
    personalized_theam_loader()
    #colab()    #funcional

def top_10():
    l = loader()
    csv = l.orderedLoader("movies_metadata.csv");
    print(csv)

def personalized_theam_loader():
    l = loader()
    userId = 10
    preferences = l.theme_loader(userId,"small_ratings.csv","movies_metadata.csv")
    for i in range(1,11):
        print(preferences[i-1])

def colab():
    l = loader()
    l.colab_filtering("small_ratings.csv","movies_metadata.csv")


if __name__ == "__main__":
  main()