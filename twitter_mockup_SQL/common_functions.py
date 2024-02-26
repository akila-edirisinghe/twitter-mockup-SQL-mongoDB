import sqlite3
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

def count_following(cursor, usr):
    '''
    return the number of users 'usr' follows.
    <usr> is a unique id.
    '''
    cursor.execute('   SELECT COUNT(*) FROM follows WHERE flwer =:username;  ', {"username": int(usr)})
    flwees = cursor.fetchone()
    return flwees[0]

def count_followers(cursor, usr):
    '''
    return the number of users following 'usr'
    <usr> is a unique id.
    '''
    cursor.execute('   SELECT COUNT(*) FROM follows WHERE flwee =:username;  ', {"username": int(usr)})
    flwers = cursor.fetchone()
    return flwers[0]

def count_tweets(cursor, usr):
    '''
    return the numer of tweets 'usr' has written
    <usr> is a unique id.
    '''
    cursor.execute('   SELECT COUNT(*) FROM tweets WHERE writer =:username;  ', {"username": int(usr)})
    tweets = cursor.fetchone()
    return tweets[0]

def follow(connection, cursor, flwer, flwee):
    '''
    updates the follows table and adds a 'follows' relationship between two users
    <flwer> is a unique user id.
    <flwee> is a unique user id that is different from <flwer>.
    '''
    # users cannot follow themselves
    if flwer == flwee:
        print("Error, users cannot follow themselves.")
        return
    else:
        cursor.execute('   SELECT COUNT(*) FROM follows WHERE flwer=? AND flwee=?;   ', (flwer, flwee))
        instance = cursor.fetchone()
        if instance[0] == 0:
            cursor.execute('   INSERT INTO follows VALUES (:follower, :followee, CURRENT_DATE);   ', {"follower": flwer, "followee": flwee})
            connection.commit()
        else:
            print("You are already following this user.")
        return

def num_retweets(cursor,tweet_tid):
    '''
    finds the number of retweets a tweet has
    <tweet_tid> is a unique tweet id
    '''
    cursor.execute('''
                   select count(*)
                   from retweets
                   where tid = :tweet_tid;
                   ''', {'tweet_tid': int(tweet_tid)})
    num_ret = cursor.fetchone()
    return num_ret[0]

def num_replies(cursor,tweet_tid):
    '''
    finds the number of replies a specific tweet has
    <tweet_tid> is a unique tweet id
    '''
    cursor.execute('''
                   select count(*)
                   from tweets
                   where replyto = :tweet_tid;
                   ''', {'tweet_tid': int(tweet_tid)})
    num_rep = cursor.fetchone()
    return num_rep[0]

def list_of_followers(cursor, user_id):
    '''
    returns a list of followers of user_id containing tuples that has (follower_id, follower_name)
    <user_id> is a unique user id
    '''
    cursor.execute('''
                    SELECT follows.flwer, users.name
                    FROM follows inner join users on (follows.flwer = users.usr)
                    WHERE follows.flwee = :user
                    ORDER BY follows.start_date DESC;
                    ''', {"user": int(user_id)})
    follower_list = cursor.fetchall()
    return follower_list

def list_of_tweets(cursor, user_id):
    '''
    returns a list of tweets (latest to oldest) that the user has made
    <user_id> is a unique user id
    '''
    cursor.execute('''
                    SELECT tdate, text
                    FROM tweets
                    WHERE writer = :user
                    ORDER BY tweets.tdate DESC;
                    ''', {"user": int(user_id)})
    tweet_list = cursor.fetchall()

    return tweet_list

'''
# displays up to n recent tweets
# - <list> tweets_list: list of tuples. Each tuple contain a tweet text
# - <int> n: up to how many you want to display
def display_up_to_n_most_recent_tweets(cursor, tweets_list, n):
    index = 0
    status = True
    
    while status:
        for i in tweets_list[index:index+n]:
            print(i)
        # print(tweets_list[index:index+n])
        userin = input("type one of the following: next, prev, q: ")
        if userin.lower() == "next":
            if (index+n) < len(tweets_list):
                index += n
            else:
                print("No more next")
        elif userin.lower() == "prev":
            if (index-n) >= 0:
                index -= n
            else:
                print("No more previous")
        elif userin.lower() == "q":
            print("Exiting..")
            status = False
        else:
            print("Invalid output")
    return 

'''

def display_stuff(whatever_list, n, select_option):
    begin = 0
    end = n
    if len(whatever_list)==0:
        print("\nno items to display\n")
        return -1
    not_done = True
    while not_done:
        
        for i in whatever_list[begin:end]:
            list_string = ' '.join(map(str,i))
            print(list_string)
        
        if select_option == 1:
            print("\ntype:\nnext(next page)\nprevious(previous page)\nselect(select an item on the screen)\nquit")
        elif select_option == 0:
            print("\ntype: \nnext(next page)\nprevious(previous page)\nquit")
        user_input = input("\noption: ")

        if user_input.lower() == "next" and not user_input.isdigit():
            if begin +n > len(whatever_list):
                print("\n/////////no more pages////////////\n")
                
            else:
                begin += n
                end += n
           
        elif user_input.lower() == "previous" and not user_input.isdigit():
            if (begin -n) < 0:
                print("\n////////no more pages//////////\n")
                
            else:
                begin -= n
                end -= n
        
        elif user_input.lower() == "quit" and not user_input.isdigit():
            not_done = False
            return -1
        
        elif select_option == 1:
            if user_input.isdigit():
                exist = check_select(whatever_list,user_input)
                if exist:
                    return user_input
                else:
                    print("\nselected item doesn't exist in the given options\n")
        else:
            print("\ninvalid option\n")


def check_select(whatever_list, user_input):  
    exist = False
    for i in whatever_list:
        if i[0] == int(user_input):
            exist = True
            return exist 
    return exist

def retweeting(cursor, connection, tweet_tid,usr_id):
    cursor.execute('''
                    select tid,usr
                    from retweets
                    where tid = :tweet_tid 
                    and usr = :usr_id
                    ''', {'tweet_tid': tweet_tid, 'usr_id': usr_id})
    retweet_checker = cursor.fetchone()
    if retweet_checker != None:
        print("\nyou have already retweeted this tweet\n")
        
    else:
        cursor.execute('''
                        insert into retweets
                        values(:usr_id, :tweet_tid, CURRENT_DATE)
                        ''', {'usr_id': usr_id, 'tweet_tid': tweet_tid})
        connection.commit()
        print("\nretweet successful\n")
            

        
    

     
            

def tweet_stats(cursor, tid):
    '''
    displays the number of retweets and replies each tweet has
    <tid> is a unique tweet id
    '''
    # number of retweets
    cursor.execute('''
                SELECT count(*)
                FROM retweets
                WHERE tid = :tid;
                ''', {'tid': tid})
    num_retweets = cursor.fetchone()[0]
    print("Number of retweets: " + str(num_retweets))

    # number of replies of tweet
    cursor.execute('''
                SELECT count(*)
                FROM tweets
                WHERE replyto = :tid;
                ''', {'tid': tid})
    num_replies = cursor.fetchone()[0]
    print("Number of replies: " + str(num_replies))
    return
