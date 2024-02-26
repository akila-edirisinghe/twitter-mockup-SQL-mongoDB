import sqlite3
from common_functions import *
'''
if you are going to use any sql thing. U obviously need to connect
to the database and create a cursor. There is already a cursor created in
main_interface.py. So you can just use that one. 
SO when creating a function, simply do:

def example_function(cursor,other_parameters):

NOW you might ask, why don't we just create our own cursor for each file?
well,because we don't know the path file at the start. So in the main file,
I got a prompt asking the person to insert the database path and that's how
i get the path 
'''

def show_profile(cursor, usr):
    '''
    <usr> is a unique id
    display profile information for <usr> including their id, their name,
    number of tweets posted, number of followers and number of users they follow.
    display their 3 most recent tweets.
    '''
    cursor.execute("   SELECT usr, name FROM users WHERE usr =:username;   ", {"username": int(usr)})

    user_info = cursor.fetchone()  # fetches user id and name
    tweet_count = count_tweets(cursor, usr)
    users_flwing = count_following(cursor, usr)
    users_flwers = count_followers(cursor, usr)

    # get the users tweets
    cursor.execute("   SELECT tdate, text FROM tweets WHERE writer =:username ORDER BY tdate DESC;   ", {"username": int(usr)})
    tweets = cursor.fetchall()
    
    print(f"\n{user_info[1]}'s profile \nid: {user_info[0]} \n{tweet_count} posts \nfollowers: {users_flwers}   following: {users_flwing}\n")

    if len(tweets) == 0:
        print("no posts yet.\n")
    else:
        # display 3 tweets
        for twt in tweets[0:3]:
            list_string = ' '.join(map(str,twt))
            print(list_string)

    return tweets  # for displaying more


def search_users(connection, cursor, user_id):
    '''
    Retrieves all users whose names or cities contain a keyword, in an ascending order of name/city length
    <user_id> is the id of the user currently logged in
    '''
    keyword = (input("\nSearch a keyword:")).lower()

    # find users whose name match the keyword
    cursor.execute("   SELECT * FROM users WHERE name LIKE ? ORDER BY LENGTH(name);   ", (f'%{keyword}%',))
    matches_name  =  cursor.fetchall()
    
    # find users whose city but not name match the keyword
    cursor.execute("   SELECT * FROM users WHERE city LIKE ? AND name NOT LIKE ? ORDER BY LENGTH(city);   ", (f'%{keyword}%', f'%{keyword}%'))
    matches_city  =  cursor.fetchall()
    
    # get list of user ids (usr)
    sorted_users = []
    for user in (matches_name + matches_city):
        if user[0] != None: 
            sorted_users.append((user[0], user[2]))  # get first and third column for id and name respectively.

    # display result
    if len(sorted_users) == 0:
        print(f'No results shown for "{keyword}". \n')
    else:
        usr_id = display_stuff(sorted_users, 5, 1)

        # check for valid input
       
        if usr_id != -1:
            
            prompt = True
            while prompt:
                
                tweets = show_profile(cursor, usr_id)

                # check for valid input
                valid = False
                action = None
                while valid == False:
                    action = (input("\nSelect one of the following: \n   (1) follow this user \n   (2) see more tweets \n   (q) quit \n")).lower()
                    if action not in ('1', '2', 'q'):
                        print("Not a valid option. \n")
                    else:
                        valid = True

                if action == '1':
                    follow(connection, cursor, user_id, usr_id)  # user currently logged in will follow 'usr'
                elif action == '2':
                    display_stuff(tweets,3, 0)
                    #display_up_to_n_most_recent_tweets(cursor, tweets, 5) # 5 at a time
                elif action == 'q':
                    print("Exiting...")
                    prompt = False


def compose_tweet(connection ,cursor, user_id, replyto=None):
    # user should be able to compose a tweet and when they do,
    # it should be added to the tweets table. If empty, the table's tid 
    # should be set at one, otherwise take the max tid and add one to it 
    # since it is the primary key of the table.
    text = input("type text: ")
   

    # get tid. if db is empty, set to 1 else add 1 to max
    cursor.execute('''
                    SELECT MAX(tid) 
                    FROM tweets;
                    ''')

    max_tid = cursor.fetchone()[0]
    if max_tid is None:
        max_tid = 1
    else:
        max_tid += 1
    
    # insert tweet
    if replyto != None:
        replyto = int(replyto)
    cursor.execute('''INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES 
                   (:tid, :user, CURRENT_DATE, :text, :reply);''', 
                   {'tid': max_tid, 'user': int(user_id), 'text': text, "reply":replyto})
    
    # A tweet can have hashtags which are marked with a # before each hashtag.
    # information about hashtags must be stored in tables mentions and if needed, in hashtags.
    text = text.replace("#", " #")          # changes '#' to ' #' to seperate double hashtags
    words = text.split()                    # remove space and turns it to a list
    hashtags = []
    for word in words:
        if word[0] == '#':
            hashtags.append(word[1:].lower())
    
    # Insert hashtags into hashtags table if not already there. 
    for hashtag in hashtags:
        cursor.execute('''
                        SELECT * 
                        FROM hashtags 
                        WHERE term = :tag;''', 
                        {'tag': hashtag})
        if cursor.fetchone() is None:
            cursor.execute('''
                            INSERT INTO hashtags VALUES 
                            (:tag);''', 
                            {'tag': hashtag})
        else: 
            print("The hashtag: '{}' already exists.".format(hashtag))
        # Insert into mentions table
        # check to see if it exists somehow
        cursor.execute('''
                        SELECT *
                        FROM mentions
                        WHERE tid =:tid AND term =:tag;''',
                        {"tid":max_tid, "tag": hashtag})
        if cursor.fetchone() is None:
                cursor.execute('''
                                INSERT INTO mentions VALUES 
                                (:tid, :tag);''', 
                                {'tid': max_tid, 'tag': hashtag})
        else: 
            print("The mention: '{}' already exists.".format(hashtag))
                
    # commit changes
    print("\n/////successfully replied//////\n")
    connection.commit()

def list_followers(connection, cursor, user_id):
    # prints list of followers that follows the user
    print("\n///// list_followers /////\n")
    followers_list = list_of_followers(cursor, user_id)
    index = 1
    if len(followers_list) == 0:
        print("\nno followers yet.\n")
        return
    else:
        for follower in followers_list:
            print("{}:({}) follows you".format(follower[0], follower[1]))
            index = index + 1
        
    # ask the current user to select a follower to
    # see more info about the user like
    # number of tweets, number of followers and 3 most recent tweets
    valid_id = False
    while not valid_id:
        option = input("\ntype follower id or type q to quit: ")
        if option.lower() == 'q':
            return
        if option.isdigit() == True:
            if check_select(followers_list, option):
                for follower in followers_list:
                    if follower[0] == int(option):
                        valid_id = True
            else:
                print("Invalid follower id.")
        else:
            print("Not a valid option. Try again.")
            
    print("\nfollower_ id: ", option, "\nstats:")
    number_of_tweets = count_tweets(cursor, option)
    
    print("The number of tweets: {}".format(number_of_tweets))
    followers_number_of_followers = count_followers(cursor,option)
    print("The number of followers this follower has is: {}".format(followers_number_of_followers))
    tweet_list = list_of_tweets(cursor, option)
    print("\n")
    if len(tweet_list) == 0:
        print("\nno posts yet.\n")
    else:
        # display 3 tweets
        for twt in tweet_list[0:3]:
            list_string = ' '.join(map(str,twt))
            print(list_string)
    
    
    # The user should be given an option to follow the selected user or see more tweets.
    
    running = True
    while running:
        question = input("\nSelect one of the following:\n1:follow this user.\n2.See more tweets.\nq. to quit: ")
        print(" ")
        if(question.lower()) in {"1", "2", "q"}: 
            if question == "1":
                # check to see if the user is already following
                cursor.execute('''
                                SELECT *
                                FROM follows
                                WHERE flwer = :flwer AND flwee = :flwee;''',
                                {"flwer": int(user_id), "flwee": int(option)})
                if cursor.fetchone() is None:
                    cursor.execute('''
                            INSERT INTO follows (flwer, flwee, start_date) VALUES
                            (:flwer, :flwee, CURRENT_DATE);''', 
                            {"flwer": int(user_id), "flwee": int(option)})
                    print("/////successfully folowed the user //////")
                
                
                else:
                    print("\n//////You are already following this user//////")
                    
            elif question == "2":
                display_stuff(tweet_list,3, 0)
                
            elif question.lower() == "q":
                print("Exiting...")
                running = False
            
        else:
            print("\nNot a valid option")
            

    # commit changes
    connection.commit()

def search_for_tweets(connection, cursor, self_id):
    '''
    Retrieves all tweets with similar keywords specified by the user; then allows user to see specific stats for the tweet and compose replies and retweets
    <self_id> is the id of the user currently logged in
    '''
    # prompt user input
   
    keyword = input("Enter keyword: ")
    keyword = keyword.split()
    and_clause = ''
    for key in keyword:
        if key[0] == '#':
            and_clause = and_clause + ' OR UPPER(t.term) = ' + "'" + key[1:].upper() + "'"
        else:
            and_clause = and_clause + ' OR UPPER(t.text) LIKE ' "'%" + key.upper() + "%'"

    and_clause = and_clause[4:]

    text = 'SELECT t.tid, t.writer, t.tdate, t.text FROM (select tid, writer, tdate, text,  term from tweets left outer join mentions using (tid)) as t WHERE ' + and_clause + ' ORDER BY t.tdate DESC;'
    cursor.execute(text)
    tweets_list = cursor.fetchall()
    
    tid = display_stuff(tweets_list, 5, 1)
    
    
    for i in tweets_list:
        if i[0] == int(tid):
            list_string = ' '.join(map(str,i))
            print("\ntweet: ", list_string)
    num_ret = num_retweets(cursor,tid)
    num_rep = num_replies(cursor, tid)
    print("\ntweet stats: ")
    print("number of retweets: ", num_ret)
    print("number of replies: ", num_rep)
    

    # the user should be able to compose a reply to a tweet (see the section on composing a tweet), 
    # or retweet it (i.e. repost it to all people who follow the user).
    while True:
        select = input("Select one of the following: 1: reply to a tweet. 2. retweet a tweet. q. to quit: ")
    
        if select == '1':
            #reply to tweet
            compose_tweet(connection ,cursor, self_id, tid)
            
        elif select == '2':
            # retweet a tweet
            retweeting(cursor, connection, tid, self_id)
        elif select == 'q':
            return
        else:
            print("Invalid input.")
    return
