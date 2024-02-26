import sqlite3
import random
from getpass import getpass
from system_functions import *
from common_functions import *
from common_functions import *
import os

connection = None
cursor = None 

def connect():
    '''
    connect asks for the database path and connects to it checks if the database exists. If not, reasks the prompt.
    '''
    global connection, cursor
    try:
        path = input("type in database path: ")
        if os.path.exists(path):
            connection = sqlite3.connect(path)
            cursor = connection.cursor()
            cursor.execute(' PRAGMA foreign_keys=ON; ')
            connection.commit()
        else:
            print("database not found")
            connect()
    except sqlite3.OperationalError  as e:
        print(e)
        connect()
    except sqlite3.Error as e:
        print(e, " \nshows except block is working")
        connect()

def registered_users():
    #do input checking 
    '''
    asks for the user's id and pass. if the password or usr_id is wrong, it asks again.
    THis is done by running a query to find if the usr_id and password is in the users table
    if it returns nothing, then the usr_id or password doesn't exist hence error msg.
    '''
    not_pass = True
    while not_pass:
        usr_id = input("\nuser_id: ")
        password = getpass("password: ")
        
        
        cursor.execute(''' 
                    select usr
                    from users
                    where usr = :usr_id and pwd = :password
                    ''', {'usr_id': usr_id, 'password': password})
        user_id = cursor.fetchone()
        
        if user_id is None:
            print("\nwrong username or password")
        else:
            not_pass = False
            user_id = user_id[0]
            
            return user_id
        

def unregistered_user():
    '''
    asks the user for input on all the details. All is optional except for password.
    if the password is empty, asks for a password again.
    once all the data is inputted, insert it to the users table.
    AT THE SAME TIME, it calls the avaliable_id function to find the next avaliable usr_id
    and prints the new user_id
    '''
    name = input("name: ")
    email = input("email: ")
    city = input("city: ")
    timezone = input("timezone: ")
    password_good = False
    while not password_good:
        password = getpass("password: ")
        if password == "":
            print("\nplease type in password\n")
        else:
            password_good = True
                
    new_id = avaliable_id()
    cursor.execute('''
                    insert into users
                    values (:new_id, :password, :name, :email, :city, :timezone)
                    ''', {'new_id': new_id, 'password': password, 'name': name, 'email': email, 'city': city, 'timezone': timezone})
    
    print("\nyour new user id is: ", new_id)
    connection.commit()
        
    return new_id

'''
using set difference to find list of avaliable usr_id
for this, I need to know the range of usr_id
'''
def range_usr_id():
    '''
    gets the range of already existing user ids
    '''
    cursor.execute('''
                   select max(usr)
                   from users
                   ''')
    max_id = cursor.fetchone()
    
    cursor.execute('''
                   select min(usr)
                   from users
                   ''')
    min_id = cursor.fetchone()
    return min_id[0], max_id[0]

def avaliable_id():
    '''
    use set difference to get the list of avaliable usr_id. if the set is empty,
    then just plus 1 to the max_id
    '''
    full_range_id = []
    
    min_id, max_id = range_usr_id()
    full_range_id.extend(range(min_id, max_id+1))
   
    full_range_id = set(full_range_id)
    
    cursor.execute('''
                   select usr
                   from users
                   ''')
    used_id = cursor.fetchall()
 
    used_id = set(used_id)
    avaliable_id = full_range_id.difference([id[0] for id in used_id])
    avaliable_id = list(avaliable_id)

    if len(avaliable_id) == 0:
        return max_id + 1
    random_id = random.choice(avaliable_id)
 
    return random_id

def display(usr_id):
    '''
    handles displaying tweets and retweets
    
    '''
    not_done = True
    while not_done:
        log3 = {"1": "see tweets", "2": "see retweets", "3": "return to main option"}
        print("\n1.see tweets\n2.see retweets\n3.return to main option")
        option = input("\noption: ")
        if option in log3:
            if option == "1":
                print("///// tweets /////")
                tweets = tweets_table(usr_id)
                tweet_select = display_stuff(tweets, 5, 1)
                if tweet_select != -1:
                    tweet_selection(tweets,tweet_select, usr_id)
                
                
            elif option == "2":
                print("///// retweets /////")
                retweets = retweets_table(usr_id)
                display_stuff(retweets, 5, 0)
                
            elif option == "3":
                not_done = False
        else:
            print("\ninvalid option\n")
    
            
            
            
def tweet_selection(tweets_list, user_input, usr_id):
    '''
    this functions is mainly for if the user selects a tweet, and then display
    the necessary stuff like stats, ability to compose a reply, retweet or go back to the previous menu
    for compose a reply, using one of the system functions
    for retweet, using one of the common functions that are made for retweeting stuff
    '''
    
    tweet_tid = int(user_input)
    
    #changes were made here. calling the 2 functions under from common functions
    num_ret = num_retweets(cursor,tweet_tid)
    num_rep = num_replies(cursor, tweet_tid)
    
    for i in tweets_list:
        if i[0] == tweet_tid:
            list_string = ' '.join(map(str,i))
            print("\ntweet: ", list_string)
    print("\ntweet stats: ")
    print("number of retweets: ", num_ret)
    print("number of replies: ", num_rep)
    
    not_done2 = True
    while not_done2:
        print("\n1.compose a reply\n2.retweet it\n3.go back to previous menu")
        user_input2 = input("option: ")
        
        if user_input2 == "1":
            compose_tweet(connection, cursor, usr_id,tweet_tid )
            
        elif user_input2 == "2":
            retweeting(cursor, connection, tweet_tid,usr_id)
            
        elif user_input2 == "3":
            not_done2 = False
        else:
            print("\ninvalid option\n")

def tweets_table(usr_id):
    '''
    gets the tweets list based on the user_id
    '''
    
    cursor.execute("""
                   select distinct t.tid, t.writer, t.tdate, t.text
                   from tweets t, follows f
                   where f.flwer = :usr_id
                   and f.flwee = t.writer
                   order by t.tdate desc
                   """, {'usr_id': usr_id})
     
    tweets = cursor.fetchall()
    return tweets

def retweets_table(usr_id):
    '''
    gets the retweet list based on the user_id
    '''
    
    cursor.execute('''
                   select distinct r.usr, r.tid, r.rdate
                   from retweets r, follows f
                   where f.flwer = :usr_id
                   and f.flwee = r.usr
                   order by r.rdate desc
                   ''', {'usr_id': usr_id})
    
    retweets = cursor.fetchall()
    return retweets
                   
def system_f2(usr_id):
    '''
    main menu showing the system functions
    '''
    running = True
    while running:
        print("\n////SYSTEM FUNCTIONS////\n")
        log3 = {"1": "search for tweets", "2": "search for users", "3": "compose a tweet", "4": "list_followers", "5": "log out","6": "return to main menu"}
        print("1.search for tweets\n2.search for users\n3.compose a tweet\n4.list_followers\n5.log out\n6.return to main menu")
        picking_system = input("\noption: ")
        if picking_system in log3:
            if picking_system == "1":
                search_for_tweets(connection,cursor, usr_id)
            elif picking_system == "2":
                search_users(connection,cursor,usr_id)
            elif picking_system == "3":
                compose_tweet(connection, cursor, usr_id, None)
            elif picking_system == "4":
                list_followers(connection,cursor, usr_id)
            elif picking_system == "5":
                running = False
                log()
                
            elif picking_system == "6":
                running = False

def system_f1(usr_id):
    '''
    main main menu showing the main options
    
    '''
    choosing_main_options = True
    while choosing_main_options:
        log2 = {"1": "see tweets or retweets", "2": "other system functions", "3": "log_out", "4":"exit"}
        print("\n////MAIN MENU////\n\noptions:\n1.see tweets or retweets\n2.other system functions\n3.log out\n4.exit")
        picking_action = input("\noption: ")
        if picking_action in log2:
            if picking_action == "1":
                display(usr_id)
                choosing_main_options = True
            elif picking_action == "2":
                system_f2(usr_id)
            elif picking_action == "3":
                choosing_main_options = False
                log()
            elif picking_action == "4":
                quit()
        else:
            print("\ninvalid option\n")

def log():
    '''
    login screen
    '''
    print("\n////////LOG SCREEN/////////")
    log = {"1": "login in", "2": "sign up", "3": "exit"}
    running = True
    usr_id = None
    while running:
        print("\n1.login in \n2.sign up\n3.quit")
        option = input("\noption: ")
        if option.lower() in log:
            if option == "1":
                usr_id = registered_users()
                print("\nwelcome back\n")
                running = False
                
            elif option == "2":
                #check this 
                usr_id = unregistered_user()
                running = False

            elif option == "3":
                running = False
                return exit()
        else:
            print("\ninvalid option\n")
    
    system_f1(usr_id)
                        
def main():
    connect()
    log()
        
         
    return
main()


