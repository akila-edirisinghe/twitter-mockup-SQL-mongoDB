from system_functions import *
from pymongo import MongoClient
import sys





def main():
    client = MongoClient('mongodb://localhost:{}'.format(sys.argv[1]))
    db = client["291db"]
    tweetscollection = db["tweets"]
    main_loop = True
    while main_loop:
        print("\n//////// MAIN_MENU ////////\n")
        print("\n1. search for tweets \n2. search for users \n3. list top tweets \n4. list top users \n5. compose a tweet \n6. log out")
        choices = {"1": "search_tweets", "2": "search_users", "3": "list_top_tweets", "4": "list_top_users", "5": "compose_tweet", "6": "exit"}
        choice = input("\nPlease enter your choice: ")
        if choice in choices:
            if choice == "1":
                search_tweets(tweetscollection)
            elif choice == "2":
                search_users(tweetscollection)
            elif choice == "3":
                list_tweets(tweetscollection)
            elif choice == "4":
                list_users(tweetscollection)
            elif choice == "5":
                compose_tweet(tweetscollection)
            elif choice == "6":
                main_loop = False
                exit()
        else:
            print("\nInvalid choice, please try again.")
            
main()