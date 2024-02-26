import pymongo
from pymongo.collation import Collation
from datetime import datetime

def search_tweets(tweetscollection):
    '''
    he user should be able to provide one or more keywords, \
    and the system should retrieve all tweets that match all those keywords (AND semantics). 
    A keyword matches if it appears in the content field. For each matching tweet, display the id, date, content, and username of the person who posted it.
    The user should be able to select a tweet and see all fields.


    '''
    print("\n//////// SEARCH FOR TWEETS ////////\n")
    words = input("Enter keyword(s): ").lower().split()
    #split words based on the spacing
    #if the string isn't empty
    if len(words) != 0:
        query = {'$and': [{'content': {'$regex': word, '$options': 'i'}} for word in words]}
        #creates a bunch of regex queries and if they all work, then select the specific document.
        search = tweetscollection.find(query, collation=Collation(locale='en', strength=4))
        count = tweetscollection.count_documents(query, collation=Collation(locale='en', strength=4))
        #gets the count of the documents 
        search = list(search)
        if count != 0:        
            for tweet in search:
                if tweet["id"] is None :
                    print("\n")
                    print("tweet_id: ","\ndate: ", tweet["date"], "\ncontent: ", tweet["content"], "\nusername: ", tweet["user"]["username"], "\n")
                else:
                    print("\n")
                    print("tweet_id: ", tweet["id"],"\ndate: ", tweet["date"], "\ncontent: ", tweet["content"], "\nusername: ", tweet["user"]["username"], "\n")
                
            running = True
            while running:
                tweet_selected = input("\nEnter tweet_id  or q to go back to menu: ")
                if tweet_selected == "q":
                    running = False
                else:
                    #checks if the selected input is in the list displayed above
                    if check_tweet_select(search, tweet_selected):
                        tweet_info = tweetscollection.find_one({"id":int(tweet_selected)})
                        print("\ntweet_info:" , tweet_info, "\n")
                        running = False
                    else:
                        
                        print("\ntweet id doesn't exist in the current searchh\n")
        else:
            print("\nNo tweets found\n")
    else:
        print("\nno tweets\n")
        
def search_users(tweetscollection):
    '''
    The user should be able to provide a keyword  
    and see all users whose displayname or location contain the keyword. 
    For each user, list the username, displayname, and location with no duplicates. 
    The user should be able to select a user and see full information about the user.

    '''
    print("\n//////// SEARCH FOR USERS ////////\n")
    words = input("Enter one keyword: ").lower().split()
    if len(words) != 0:
        word = words[0]
        #the queries search for one word using the regex in both displayname and location.
        query = { '$or': [{'user.displayname': {'$regex': word, '$options': 'i'}}, {'user.location': {'$regex': word, '$options': 'i'}}]}
        search = tweetscollection.find(query, collation=Collation(locale='en', strength=4))
        search = list(search)
        seen = []
        #puts users who haven't been seen before to the seen list. if it finds a user with higher followercount, replace it with the one in the seen list
        for user in search:
            seen_usernames = [u["username"] for u in seen]
            if user["user"]["username"] not in seen_usernames:
                seen.append(user["user"])
            elif user["user"]["username"] in seen_usernames:
                index = seen_usernames.index(user["user"]["username"])
                if user["user"]["followersCount"] > seen[index]["followersCount"]:
                    seen[index] = user["user"]
                    
        for user in seen:
            if user["displayname"] is None :
                print("\n")
                print("username:  ", user["username"], "\ndisplayname: ", "\nlocation: ", user["location"], "\n")
            else:
                print("\n")
                print("username:  ", user["username"], "\ndisplayname: ", user["displayname"], "\nlocation: ", user["location"], "\n")
        
        running = True
        while running:
            user_input = input("\nEnter username or q to go back to menu: ")
            if user_input == "q":
                running = False
            else:
                #checks if the selected user is in the items displayed
                if check_user_select(seen,user_input):
                    #searches for a user that is equal to the user input and then sorts by followercount, and limit the document to 1
                    user_info = tweetscollection.find({"user.username":user_input},{"user":1}).sort("user.followersCount", -1).limit(1)
                    for user in user_info:
                        print("\nuser_info:" , user, "\n")
                    running = False
                else:
                    print("\nusername doesn't exist in the current search\n")
    else:
        print("\nno users\n")
    
def list_tweets(collection):
    print("\n//////// LIST TOP TWEETS ////////\n")

    # Get user input for the field and number of tweets to display
    print(("-")*30+"\n"+"1: retweetCount\n2: likeCount\n3: quoteCount"+"\n"+("-")*30)
    running = True
    
    while running:
        user_choice = input("Input: ")

        # Map user's input to the corresponding field
        field_mapping = {"1": "retweetCount", "2": "likeCount", "3": "quoteCount"}
        field = field_mapping.get(user_choice)


        # Validate user input
        if not field:
            print("Invalid choice. Please enter 1, 2, or 3.")
        else:
            running = False
    
    running2 = True
    while running2:
        n = input("Enter the number of tweets to display: ")
        if n.isdigit():
            n = int(n)
            if n < 1:
                print("Invalid choice. Please enter a positive integer.")
            else:
                running2 = False
        else:
            print("Invalid choice. Please enter a positive integer.")
    
    # Define the projection to include only relevant fields
    projection = {
        "_id": 0,
        "id": 1,
        "date": 1,
        "content": 1,
        "user.username": 1,
        field: 1
    }

    # Retrieve the top N tweets based on the selected field, ordered in descending order
    top_tweets_cursor = collection.find({}, projection).sort(field, pymongo.DESCENDING).limit(n)

    # Create a list from the cursor to allow multiple iterations
    top_tweets = list(top_tweets_cursor)


    # Retrieve the top N tweets based on the selected field
    top_tweets = collection.find({}, projection).sort(field, -1).limit(n)
    top_tweets = list(top_tweets)

    print("------------------------")
    # Display the streamlined results
    for tweet in top_tweets:
        if tweet["id"] is None :
            print("\n")
            print("tweet_id: ","\ndate: ", tweet["date"], "\ncontent: ", tweet["content"], "\nusername: ", tweet["user"]["username"], "\n")
            
        else:
            print(f"Tweet ID: {tweet['id']}")
            print(f"Date: {tweet['date']}")
            print(f"Content: {tweet['content']}")
            print(f"Username: {tweet['user']['username']}")
        
        # Print the selected field and its value
        selected_field_value = tweet.get(field, None)
        print(f"Selected Field ({field}): {selected_field_value}")
        
        print("------------------------")


    running3 = True
    while running3:
    # Allow the user to select a tweet and see all fields
        selected_tweet_id = input("\nEnter the ID of the tweet to view all fields (or press q to skip: ").strip()
        if selected_tweet_id == "q":
            running3 =  False
        else:
            if check_tweet_select(top_tweets, selected_tweet_id):
                selected_tweet = collection.find_one({"id": int(selected_tweet_id)})
                if selected_tweet:
                    print("\nSelected Tweet:", selected_tweet)
                    running3 = False
            else:
                print("\nTweet not in the list above.")


def list_users(tweetscollection):
    # This function displays the top n users based on followersCount (n is inputted by the user)

    length = tweetscollection.count_documents({"_id": {"$exists":True}})
    # prompt user for number of accounts they would like to see
    n = input("Enter the number of accounts you would like to see: ")
    # check if the input is valid
    while True:
        # check if an integer is inputted
        try:
            n = int(n)
        except Exception:
            print("Invalid input.")
            n = input("Enter the number of accounts you would like to see:\n ")
            
            continue
        # check if the integers is within range of 0 to the number of documents
        if n > length or n < 0:
            print("Invalid input.")
            n = input("Enter the number of accounts you would like to see: ")
            
        else:
            break
    # sort the documents by followersCount
    results = tweetscollection.find().sort("user.followersCount", -1)
    
    shown = []  # keep track of possible duplicates
    i = 0
    limit = 0
    # display top n accounts
    while limit < n and i < length:
        if results[i]["user"]["username"] not in shown:
            shown.append(results[i]["user"]["username"])
            print("Username: %s" % results[i]["user"]["username"])
            print("Display name: %s" % results[i]["user"]["displayname"])
            print("Followers count: %d" % results[i]["user"]["followersCount"])
            print("")
            limit += 1
        i += 1
    # prompt user for the username of an account they would like to see more information about
    print(shown)
    running = True
    while running:
        select_user = input("Enter a username to see more information or q to go back to menu:  ")
        if select_user == "q":
            running = False
            return
        else:
            if select_user in shown :
                user_info = tweetscollection.find({"user.username":select_user},{"user":1}).sort("user.followersCount", -1).limit(1)
                for user in user_info:
                    print("\nuser_info:" , user, "\n")
                running = False  
            else:
                print("\nusername doesn't exist in the current search\n")      
    return

def compose_tweet(tweetscollection):
    # This function allows the user to create a tweet and inserts the tweet into the database

    # prompt the user to input content
    content = input("Enter your tweet: ")
    # get system date and time
    date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    # create the new tweet document
    new_tweet = {
    "date": date,
    "content": content,
    "renderedContent": content,
    "id": None,
    "user": {
        "username": "291user",
        "displayname": None,
        "id": None,
        "description": None,
        "rawDescription": None,
        "descriptionUrls": [],
        "verified": False,
        "created": None,
        "followersCount": 0,
        "friendsCount": 0,
        "statusesCount": 0,
        "favouritesCount": 0,
        "listedCount": 0,
        "mediaCount": 0,
        "location": "",
        "protected": False,
        "linkUrl": None,
        "linkTcourl": None,
        "profileImageUrl": None,
        "profileBannerUrl": None,
        "url": None
    },
    "outlinks": [],
    "tcooutlinks": [],
    "replyCount": 0,
    "retweetCount": 0,
    "likeCount": 0,
    "quoteCount": 0,
    "conversationId": None,
    "lang": None,
    "source": None,
    "sourceUrl": None,
    "sourceLabel": None,
    "media": [
        {
        "previewUrl": None,
        "fullUrl": None,
        "type": None
        }
    ],
    "retweetedTweet": None,
    "quotedTweet": None,
    "mentionedUsers": None
    }
    # insert into database
    tweetscollection.insert_one(new_tweet)
    return


def check_tweet_select(list_items, user_input):
    exist = False
    if user_input.isdigit() == False:
        return exist
    else:
        for i in list(list_items):
            if i["id"] == int(user_input):
                exist = True 
                return exist
        
    return exist

def check_user_select(list_items, user_input):
    exist = False
    for i in list_items:
        if i["username"] == user_input:
            exist = True
            return exist
    return exist
    
    

