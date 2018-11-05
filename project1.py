import getpass
import sqlite3
import sys
import random
from datetime import datetime

user_email = None

def connect(path):
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return


#These functions are serveing for login and signup functionalities
#########################################################################################################################################
def login():
    global connection, cursor
    input_email = input('Please enter your email. ')
    input_email = input_email.lower()
    input_password = getpass.getpass(prompt='Please enter your password. ')
    # prevent injections using regular expression
    # but when using re.match even partical matching will pass
    cursor.execute("select pwd from members where email=:input_email",
                       {"input_email": input_email})
    user_password = cursor.fetchone()
    user_password = str(user_password[0])
    connection.commit()

    if user_password == input_password:
        print('Successfully login')
        # and need to display all inbox unseen
        cursor.execute("select * from inbox where email=:input_email and seen = 'n' ",
                           {"input_email": input_email})
        message = cursor.fetchall()
        if len(message) != 0:
            print('Your unread messages.')
            print(message)
        # update all unseen to seen
        cursor.execute("update inbox set seen = 'y' ")
        connection.commit()

    return input_email


def SignUP():
    global connection, cursor
    # check for unique
    # create a set to store all eamil add for later checking uniquess
    email_list = []
    cursor.execute("select email from members;")
    all_email = cursor.fetchall()
    for i in range(len(all_email)):
        email_list.append(all_email[i])
    #print(email_list)

    # need to try until get the unique pwd

    while True:

        signup_email = str(input('Enter a email address to create a new account.')).lower()

            # and need to comma at the end
        signup_email = signup_email,
        if signup_email in email_list:
            print('This email already exist, try another one. ')
            continue
        else:
            signup_name = input('Please enter your name. ')
            signup_phone  = input('Please enter your phone. ')
            signup_pass = input('Enter your password. ')

            # cursor.execute("insert into members values(email=:e,name=:n,phone=:ph,pwd=pd",
            # {"e":signup_email,"n":signup_name,"p":sighup_phone, "pd":sighup_pass})
            task = (str(signup_email), str(signup_name), str(signup_phone), str(signup_pass))
            cursor.execute("insert into members values (?,?,?,?)",task)
            print("New Account have been created!")
            break
    return signup_email
#########################################################################################################################################



#These functions are subfunctions for offerinng a ride functionality
#########################################################################################################################################
#  FindLocations find all locations information which contains given keywords
def Findlocations(inputkeyword):

    input_query = 'SELECT * FROM locations WHERE lcode  LIKE "' + inputkeyword + '%" ''UNION SELECT * FROM locations WHERE prov LIKE "' + inputkeyword + '%" ''UNION SELECT * FROM locations WHERE city LIKE "' + inputkeyword + '%" ''UNION SELECT * FROM locations WHERE address LIKE "' + inputkeyword + '%"'
    location_query = 'SELECT * FROM locations WHERE lcode ==   "' + inputkeyword + '" '
    locationsInRides = getData(location_query)
    locationsInRidesLists = list(locationsInRides)
    if isLcode(inputkeyword, list(locationsInRidesLists)) == False:
        output = getData(input_query)
        return output

    else:
        output = getData(location_query)

    return output

# SelectionLocation prompts user to select the location lcode he or his want
def selectionLocation(content):
       while True:
            inputkeywords = input(content)
            inputkeywordlist = inputkeywords.split(' ')
            outputlists = []
            for item in inputkeywordlist:
                output = Findlocations(item)
                outputlists.append(output)
            outputlist = [item for sublist in outputlists for item in sublist]
            if len(outputlist) != 0:
                break
            else:
                print("We Can Not Find any Locations, Please enter another one")
                continue
       index = 0


       for item in outputlist[:5]:
            index += 1
            print(str(index) + ": ", end='')
            print(item)

       if index >= 5:

            optionM = input("Do You Want To See More Matches? Say No If you want to select now Y/N\n")

            if optionM.lower() == 'y':
                for element in outputlist[5:]:
                    index += 1
                    print(str(index) + ": ", end='')
                    print(element)
                while True:
                    try:
                        postion = int(input("Enter The Code To Select The Location\n"))
                        break
                    except ValueError:
                        print("Invalid Code")
            elif optionM.lower() == 'n':
                while True:
                    try:
                        postion = int(input("Enter The Code To Select The Location\n"))
                        break
                    except ValueError:
                        print("Invalid Code")
            else:
                print("Invalid Option")
       else:
            while True:
                try:
                    postion = int(input("Enter The Code To Select The Location\n"))
                    break
                except ValueError:
                    print("Invalid Code")
       print("You have Chosen: ", end='')
       insertTuple = outputlist[postion - 1]
       print(outputlist[postion - 1])
       return insertTuple

# extract data from sql database by given a query
def getData(input_query):
    global connection, cursor
    outputTuple =()
    cursor.execute(input_query)
    outputTuple = cursor.fetchall()
    connection.commit()
    return outputTuple

#check inputkeyword is location or not
def isLcode(inputKeyWord,inputList):
    isLcode = False
    for item in inputList:
        if inputKeyWord == item[0]:
            isLcode = True
            break
        else:
            continue
    return isLcode

#########################################################################################################################################



def NextStepRide(i, group, key):
    print("----------------------------------")
    print("Enter quit to go to main manual. ")
    print("Enter 1 for select a " + key + " from above and message the posting member. ")
    if i + 1 < group:
        print("Enter 2 to see more " + key + " request. ")
    while True:
        check = input("Enter here: ")
        if check.upper() == "QUIT":
            print("----------------------------------")
            return 3
        elif IsInt(check):
            if int(check) == 1 or int(check) == 2:
                break
            else:
                print("invalid index! Try again! ")
        else:
            print("invalid input!")
    print("----------------------------------")
    return int(check)

def GetThreeLocationKeywords():
    valid = False
    while not valid:
        #get a list
        print("Please enter at most 3 key words associated with ride.")
        temp = input("Use space to sepereate the key words :")
        # check validation
        try:
            temp = temp.split(" ")
            if len(temp) < 1 or len(temp) > 3 :
                raise Exception
            valid = True
        except Exception as e:
            print("Empty input or too many input!"+ str(e.args))
    return temp

def FindRidelcode(inputkeyword):
    location_query = 'SELECT DISTINCT lcode FROM locations WHERE lcode ==   "' + inputkeyword + '" '
    keyword_query = 'SELECT DISTINCT lcode FROM locations WHERE lcode  LIKE "' + inputkeyword + '%" ''UNION SELECT * FROM locations WHERE prov LIKE "' + inputkeyword + '%" ''UNION SELECT * FROM locations WHERE city LIKE "' + inputkeyword + '%" ''UNION SELECT * FROM locations WHERE address LIKE "' + inputkeyword + '%"'
    locationcodeList = getData(location_query);
    if len(locationcodeList) == 0:
        keywordLocation = getData(keyword_query)
        return keywordLocation
    else:
        return locationcodeList







def ListAllBookings(user_email):
    global connection, cursor

    print("The following is all the bookings match your email.")
    cursor.execute("select * from bookings b where b.email =:email",
                   {'email': user_email})
    connection.commit()
    rows = cursor.fetchall()
    for i in range(len(rows)):
        print(rows[i])


def CancelBooking(user_email):
    global conection, cursor
    cancel_num = input('Please enter the booking number you want to cancle:')
    cancel_num = int(cancel_num)
    # first get the rno of current ride base on the bno you provide
    # and then delete it from table
    # and need to query the rno from booking table
    cursor.execute("select rno from bookings where bno=:bno",
                   {"bno": cancel_num})

    inbox_rno = cursor.fetchone()
    inbox_rno = inbox_rno[0]

    connection.commit()

    # delete the booking record
    connection.execute('delete from bookings where bno =:bno', {"bno": cancel_num})
    connection.commit()
    print("The booking is deleted!")

    # sent the message to the member that .. just mean insert a new row into the inbox table
    # get time
    cursor.execute("select datetime('now','localtime');")

    timestamp = cursor.fetchone()
    timestamp = str(timestamp)
    timestamp = timestamp[2:13]
    connection.commit()
    #print(timestamp)

    content = 'System successfully delete the record!'
    sender = user_email
    seen = 'n'
    # print(inbox_rno)

    # when delete system will send a message to the user
    # cursor.execute("insert into inbox values (email=:email, msgTimestamp=:timestamp, 'system', content=:content, rno=:rno, 'n')",
    #           {"email":user_email,"timestamp":timestamp,"content":content,"rno":inbox_rno})
    connection.execute("insert into inbox values (?,?,?,?,?,?)",
                       (user_email, timestamp, sender, content, inbox_rno, seen))

    # what the hell is the rno in the message??
    # you can get this rno from bookings table
    connection.commit()


# Also the member should be able to book other members on the rides they offer
# list all rides the member offers with the number of available seats for each ride
def ListRides():
    global conection, cursor

    print('List all rides the member offers with he number of available seats')
    print('Want to see more than 5 matching rides?(y/n)')
    cond = input()
    cond = cond.lower()
    if cond == 'n':
        cursor.execute('''select driver,r.rno, (r.seats-b.seats) as available
                       from rides r
                       left outer join bookings b on r.rno = b.rno
                       limit 5;
                       ''')
        rows = cursor.fetchall()
        print(rows)
        connection.commit()

    else:
        cursor.execute('''select driver, r.rno, (r.seats-b.seats) as available
                       from rides r
                       left outer join bookings b on r.rno = b.rno
                       ;
                       ''')
        rows = cursor.fetchall()
        for i in range(len(rows)):
            print(rows[i])

        connection.commit()

def BookMember(user_email):
    global conection, cursor

    rno_select = int(input('Please enter the rno you want to select.'))
    member_email = input('Please enter the member email you want to book.')
    member_email = member_email.lower()
    num_seat = int(input('Please enter the number of seats booked.'))
    cost_per_seat = int(input('Please enter cost per seat.'))
    print('Please enter pickup and drop off location code.')
    pickup, dropoff = input().split()
    pickup = pickup.lower()
    dropoff = dropoff.lower()

    # assign a unique book number
    # first create a set with all bno in it
    bno_set = set()
    cursor.execute("select bno from bookings;")
    rows = cursor.fetchall()
    for i in range(len(rows)):
        bno_set.add(rows[i])
    # unique bno
    while True:
        temp_bno = random.randint(1, 5000)
        if temp_bno not in bno_set:
            break
    new_bno = temp_bno

    # give warning if overbook the seat
    cursor.execute('select seats from rides where rno=:rno', {"rno": rno_select})
    row = cursor.fetchone()
    if num_seat > row[0]:
        print('Warning: the seats are overbooked. Do you want to comfirm?(y/n)')
        key = input()
        key = key.lower()

        if key == 'y':
            # comfirm this booking
            connection.execute(
                "insert into bookings values(bno=:bno, email=:email,rno=:rno,cost=:cost,seats=:seats,pickup=:pickup,dropoff=:dropoff)",
                {"bno": new_bno, "email": member_email, "rno": rno_select, "cost": cost_per_seat, "seats": num_seat,
                 "pickup": pickup, "dropoff": dropoff})
        else:
            print('Overbooked, booking not complete.')

    # After a successful booking, a proper message should be sent to the other member that s/he is booked on the ride.
    # first find the emil of member base on rno user input
    # fetchone return a list, list[0] to get the date
    cursor.execute("select date('now','localtime');")
    time = cursor.fetchone()
    time = time[0]
    # cursor.execute("insert into inbox values(email=:eamil,msgTimestamp=:time,sender=:sender,'you are booked', rno=:rno,'n')",
    # {"email":member_email, "time":time,"sender":user_email,"rno":rno_select})
    connection.execute("insert into inbox values (?,?,?,?,?,?)",
                       (member_email, time, user_email, 'you are booked', rno_select, 'n'))
    connection.commit()
    print("Insert a new message into inbox.")

'''
The member should be able to select a ride and book a member for that ride
'''


def GetDate(content):
    check = "N"
    while check.upper() != "Y":
        from_user = input(content)
        try:
            date_object = datetime.strptime(from_user, "%Y-%m-%d")
            s = str(date_object)[:-8]
            print("Your ride will be on " + s)
            check = input("Enter y to indicate it is correct: ")
        except Exception as f:
            print("invalid input" + str(f.args))
    return date_object


# get a valid location code from user and then return it
def GetLocation(content):
    global cursor, connect
    check = "N"
    while check.upper() != "Y":
        from_user = input(content)
        try:
            cursor.execute("select * from locations where lcode = ?", (from_user,))
            location_infor = cursor.fetchone()
            if location_infor == None:
                raise Exception
            s = ""
            for item in location_infor:
                s += str(item) + " "
            print("The location code is as following\n" + s)
            check = input("Enter y to indicate it is correct: ")
        except Exception as f:
            print("invalid input!" + str(f.args))
    return location_infor[0]


# get a float from user and return it
def GetFloat(content):
    check = "N"
    while check.upper() != "Y":
        temp = input(content)
        try:
            temp = round(float(temp), 2)
            print("Is the amount " + str(temp) + " correct? ")
            check = input("Enter y to indicate it is: ")
        except Exception as e:
            print("invalid input! " + str(e.args))
    return temp

# check whether passed parameter is an int
# used in q5
def IsInt(sth):
    try:
        sth = int(sth)
        return True
    except:
        return False


# this function is to get an exited rno from user
# first get the input and check the invalidation
# used in q5 part 2
def GetRno():
    global connection, cursor
    check = "N"
    while check.upper() != "Y":
        temp = input("Please enter an ride number associate with the message: ")
        try:
            temp = int(temp)
            cursor.execute("select rno from rides where rno = ?", (temp,))
            rno = cursor.fetchone()[0]
            print("Ride number is " + str(rno))
            check = input("Enter y to indicate it is correct: ")
        except Exception as e:
            print("invalid rno!" + str(e.args))

    return rno


# this function is to get text message from user
# used in q5 part 2
def GetText():
    check = "N"
    while check.upper() != "Y":
        print("Please enter the text message that you want to sent: ")
        text = input("Enter here: ")
        print("The text you want to send is as following: ")
        print(text)
        check = input("Enter y to send the message: ")

    return text



# This fuction create a unique rno for new rides
# rno is either within a gap bewteen continuous existing rno
# or one larger than the max existing rno
def AssignRideno():
    global connection, cursor
    try:
        gap_in_rno = '''select * from
        (select distinct r1.rno 
        from rides r1, rides r2 
        where r1.rno - r2.rno > 1

        except 

        select distinct r1.rno from rides r1, rides r2 
        where r1.rno - r2.rno = 1) 
        order by rno ASC
        limit 1;
        '''
        cursor.execute(gap_in_rno)
        rno = (cursor.fetchone())[0] - 1

    except Exception as e:
        max_in_rno = "select max (rno) from rides;"
        cursor.execute(max_in_rno)
        rno = (cursor.fetchone())[0] + 1
    return rno


# This fuction create a unique rid for new request
# new rid is either a number
# within a gap bewteen continuous existing rno
# or a number which is one larger than the max existing rno
def AssignRequestNo():
    global connection, cursor
    try:
        gap_in_rno = '''select * from
        (select distinct r1.rid 
        from requests r1, requests r2 
        where r1.rid - r2.rid > 1

        except 

        select distinct r1.rid 
        from requests r1, requests r2 
        where r1.rid - r2.rid = 1) 
        order by rid ASC
        limit 1;
        '''
        cursor.execute(gap_in_rno)
        rid = (cursor.fetchone()[0]) - 1

    except Exception as e:
        max_in_rno = "select max (rid) from requests;"
        cursor.execute(max_in_rno)
        rid = cursor.fetchone()[0] + 1

    return rid

# ------------------------------------question 5
# This function show all the requests that currentlog-in user makes
# User can delete the requests shown here
# email should be a string whose len < 15
def SeeMyRequests(user_eamil):
    global connect, cursor


    while True:
        # check current requests
        cursor.execute("select * from requests where email = ?;", (user_eamil,))
        requests = cursor.fetchall()

        # if there is nothing, prompt user to quit
        if len(requests) == 0:
            input("You do not have any requests. Press any key to go to previous menu.")
            MainMenu(user_email)

            # otherwise print all the request that user has
        print("----------------------------------")
        print("So far, You have the following requests: ")
        for i in range(0, len(requests)):
            print(str(i) + " : " + str(requests[i])[1:-1])

        # ask user if want to quit or delete current request
        while True:
            check = input("Enter quit to go to previous menu or enter index to delete ride: ")
            if check.upper() == "QUIT":
                MainMenu(user_email)
            elif IsInt(check) and int(check) not in range(0, len(requests)):
                print("invalid index!")
            elif IsInt(check) and int(check) in range(0, len(requests)):
                print("Are you sure to delete the following: ")
                print(str(requests[int(check)])[1:-1])
                double_check = input("Enter y to indicate yes: ")
                if double_check.upper() == "Y":
                    break
            else:
                print("invalid word! Try again! ")

        cursor.execute("delete from requests where rid = ?;", (requests[int(check)][0],))
        connection.commit()

    return


# Also the member should be able to provide a location code or a city
# and see a listing of all requests with a pickup location matching the location code or the city entered.
# If there are more than 5 matches, at most 5 matches will be shown at a time.
# The member should be able to select a request and message the posting member,
# for example asking the member to check out a ride.


# email should be a string whose len < 15
def SeeOtherRequests(user_email):
    global connection, cursor

    while True:
        # get users input and find requests whose pick up location matched the input
        key = input("Please enter a location code or a city name: ")
        cursor.execute('''select r.rid, r.email, r.rdate, r.pickup,r.dropoff, r.amount
                  from requests r, locations l
                  where r.pickup = l.lcode and l.lcode like "%''' + key + '''%"
                  union 
                  select r.rid, r.email, r.rdate, r.pickup,r.dropoff, r.amount
                  from requests r, locations l
                  where r.pickup = l.lcode and l.city like "%''' + key + '''%";''')
        rows = cursor.fetchall()

        # if nothing find, promp user to try again or quit to main manual
        if len(rows) == 0:
            print("Find nothing! ")
            check = input("Enter quit to go to main manual or enter other words to check other keywords: ")
            if check.upper() == "QUIT":
                MainMenu(user_email)

                # print output 5 rows a time and see what user want to do
        else:
            group = len(rows) // 5 + 1
            for i in range(0, group):
                print("----------------------------------")
                for j in range(i * 5, min((i + 1) * 5, len(rows))):
                    print(str(j) + " : " + str(rows[j])[1:-1])

                # get valid input to see if user want to go to man or see more requests or send message
                check = NextStepRide(i, group, "request")
                if check == 3:
                    MainMenu(user_email)

                # send message if user wants
                while int(check) == 1:
                    print("----------------------------------")
                    # get email from requests
                    index = 100000
                    while True:
                        temp = input(
                            "enter the index before a request whose posting member that you want to mail: ")
                        if IsInt(temp):
                            index = int(temp)
                            if index in range(0, len(rows)):
                                to = rows[index][1]
                                print("You want to send message to " + str(to))
                                double_check = input("Enter y to indecate it is correct: ")
                                if double_check.upper() == "Y":
                                    break
                            else:
                                print("index out of range!")
                        else:
                            print("Please enter an valid index.")

                    # get date for today
                    cursor.execute("select date('now','localtime');")
                    date = cursor.fetchone()[0]
                    # sender is passing when the function is called
                    # content is depending on user
                    content = GetText()
                    # get rno from user and test it
                    rno = GetRno()
                    # seen is 0 in default (False)
                    cursor.execute("insert into inbox values (?,?,?,?,?,?);", (to, date, user_email, content, rno, 0))
                    print("Your message has been sent successfully!")
                    connection.commit()

                    check = NextStepRide(i, group, "request")
                    if check == 3:
                        MainMenu(user_email)




def LoginOrSignUp():
    while True:
        try:
            decision = str(input("Are you a new member?(y/n or type q to quit)\n")).lower()
            if decision in ['n', 'y', 'q']:
                break
            else:
                print('Wrong code, please try again.')
                continue
        except ValueError:
            print('Wrong code, please try again.')

    user_email = None
    if decision == 'n':
        user_email = login()
        MainMenu(user_email)
        
    elif decision == 'y':
        user_email = SignUP()
        MainMenu(user_email)

    elif decision == 'q':
        pass
    else:
        print('Wrong code, please try again.')
    return user_email


#Control Flow for the Offer a ride function
def OfferRide(user_email):
    global connection,cursor

    given_rno = None
    given_price = None
    given_rdate = None
    given_seats = None
    given_lug_desc = None
    given_src = None
    given_dst = None
    given_driver = None
    given_cno = None
    given_rno = AssignRideno()


    given_price = GetFloat("Please enter price\n")

    given_rdate = GetDate("Please enter date(YYYY-MM-DD)\n")
    given_rdate = given_rdate.date()
    
    while True:
        try:
            given_seats = int(input("Please enter seats\n"))
            break
        except ValueError:
            print("Invalid Seats Format")

    while True:
        try:
            given_lug_desc = str(input("Please enter luggage description\n"))
            break
        except ValueError:
            print("Invadlid Luggage Description")
    while True:
        try:
            text_src = "Please enter staring Location\n"
            srclcode = selectionLocation(text_src)[0]

            break
        except ValueError:
            print('Invalid Source Location')
    while True:
        try:
            text_dst = "Please enter ending location\n"
            dstlcode = selectionLocation(text_dst)[0]
            break
        except ValueError:
            print("Invalid Destination Location")

    option = input("Do you want to add any set of enrouted locations?  Y/N\n")

  

    
    if option2.lower() == 'y':
        while True:
            try:
                given_cno = int(input("Enter The Car Number(Optional):"))
                break
            except ValueError:
                print("Invalid Car Number")
        cursor.execute("SELECT owner FROM cars WHERE cno == '%d';"%given_cno)
        carsList = cursor.fetchall()
        given_driver = carsList[0][0]
    else:
        pass

    task = (given_rno, given_price, given_rdate, given_seats, given_lug_desc, srclcode, dstlcode, given_driver, given_cno)
    cursor.execute("INSERT INTO rides(rno,price,rdate,seats,lugDesc,src,dst,driver,cno) VALUES(?,?,?,?,?,?,?,?,?)",task)
    connection.commit()
    option2 = input("Do You Want to Add the Car Number Y/N")
    if option.lower() == 'y':
        text_enroute = "Please enter keywords for enroute locations:\n"
        enroutedlcode = selectionLocation(text_enroute)[0]
       
        enroute_task = (int(given_rno),str(enroutedlcode))
        connection.execute('INSERT INTO enroute VALUES(?, ?)',enroute_task)
        connection.commit()                
                
    elif option.lower() == 'n':
        pass    
    MainMenu(user_email)


##Logic Flow for The BookMemers Or CancelBookings
def BookMembersOrCancelBookings(user_email):
    while True:
        try:
            print('Choose the following operations: ')
            print('1: list all bookings.')
            print('2: cancel bokings. ')
            print('3: list all the rides.')
            print('4: book a member on ride.')
            print('Or you can enter q to quit.')
            option = input('Please enter your option code: ')
            option = option.lower()

            if option == '1':
                ListAllBookings(user_email)

            elif option == '2':
                CancelBooking(user_email)

            elif option == '3':
                ListRides()

            elif option == '4':
                BookMember(user_email)

            elif option == 'q':
                MainMenu(user_email)

        except ValueError:
                print('Wrong code, try again.')


def SearchRide(user_eamil):
    global connection, cursor

    check = 2
    while True:
    # get location key word
        key_list = GetThreeLocationKeywords()
    # find location matches the key word
        ride = []
        for key in key_list:
            cursor.execute("""select distinct r.rno, r.price, r.rdate, r.seats, 
                                   r.lugDesc, r.seats, r.src, r.dst, r.driver, r.cno
                                   from locations l, rides r, enroute e
                                   where (r.src = l.lcode or r.dst = l.lcode or e.lcode) 
                                   and 
                                   (l.lcode like "%""" + key + """%"
                                   or l.city like "%""" + key + """%"
                                   or l.prov like "%""" + key + """%"
                                   or l.address like "%""" + key + """%")
                                   ;                        
                                   """)
        row = cursor.fetchall()
        if ride != []:
            ride = [value for value in ride if value in row]
        else:
            ride = row
    # list all the ride and get car infor
    # if nothing find, prompt user to do it again
        if len(ride) == 0:
            print("Find nothing! ")
            check = input("Enter quit to go to main manual or enter other words to check other keywords: ")
            if check.upper() == "QUIT":
                MainMenu(user_email)

        else:
            group = len(ride) // 5 + 1
            for i in range(0, group):
                print("----------------------------------")
                for j in range(i * 5, min((i + 1) * 5, len(ride))):
                    print(str(j) + " : " + str(ride[j])[1:-1])
                    try:
                        cursor.execute("select * from cars where cno = " + str(ride[j][9]) + ";")
                        car_infor = cursor.fetchall()
                        print("  car information: " + str(car_infor[0])[1:-1])

                    except Exception as e:
                        print(e.args)
                        car_infor = []

            # get valid input to see if user want to go to man or see more requests or send message
                check = NextStepRide(i, group, "ride")
                if check == 3:
                    MainMenu(user_email)

            # send message if user wants
                while int(check) == 1:
                    # get email from requests
                    index = 100000
                    while True:
                        temp = input("enter the index before a ride whose posting member that you want to mail: ")
                        if IsInt(temp):
                            index = int(temp)
                            if index in range(0, len(ride)):
                                to = ride[index][8]
                                print("You want to send message to " + str(to))
                                double_check = input("Enter y to indecate it is correct: ")
                                if double_check.upper() == "Y":
                                    break
                            else:
                                print("index out of range!")
                        else:
                            print("Please enter an valid index.")

                # get date for today
                    cursor.execute("select date('now','localtime');")
                    date = cursor.fetchone()[0]
                # content is depending on user
                    content = GetText()
                # get rno from user and test it
                    rno = ride[index][0]
                # seen is 0 in default (False), sender is passing when the function is called
                    cursor.execute("insert into inbox values (?,?,?,?,?,?);", (to, date, user_email, content, rno, 0))
                    print("Your message has been sent successfully!")
                    connection.commit()
                # check whether user want to go to main manaul,see more rides or sent more messege
                    check = NextStepRide(i, group, "ride")
                    if check == 3:
                        MainMenu(user_email)


# ------------------------------------question 4
# this function is to post a ride request
# email should be a string whose lenghth is < 15
def PostRideRequests(user_email):
    global connection, cursor


    # get valid input from user
    print("----------------------------------")
    date = GetDate("Please enter your date for travelling (YYYY-MM-DD) : ")
    print("----------------------------------")
    pick_up = GetLocation("Please enter your pick up location code: ")
    print("----------------------------------")
    drop_off = GetLocation("Please enter your drop off location code: ")
    print("----------------------------------")
    amount = GetFloat("Please enter the amount you are willing to pay per seat: ")
    print("----------------------------------")

    # flush data into database
    rid = AssignRequestNo()
    cursor.execute("insert into requests values (?,?,?,?,?,?);", (rid, user_email, date.date(), 'ab1', 'ab2', int(amount)))
    connection.commit()
    print("Your request is posted successfully!")

    MainMenu(user_email)

#Control Flow For the Search and Delete ride requests funcatinality
def SearchAndDeleteRideRequests(user_email):
    while True:
        try:
            option = int(input("Enter 1 If You Want To See Your Ride Requests. \nOtherwise Enter 2 To See Others' Requests\n"))
            if option == 1:
                SeeMyRequests(user_email)
                break
            elif option == 2:
                SeeOtherRequests(user_email)
                break
            else:
                print("Invalid Code, Pleases Try Again")
                continue
        except:
            print("Invalid Input, Pleases Try Again")


def MainMenu(user_email):
    while True:
        try:
            operation = str(input("Eneter Operation Code To Select:\n"
                                  "1: Offer A Ride\n"
                                  "2: Search For Ride\n"
                                  "3: Book Members Or Cancel Bookings\n"
                                  "4: Post Ride Request\n"
                                  "5: Search And Delete Ride Requests\n"
                                  "QUIT: Enter QUIT to Exit Program\n"
                                  "Code:"))

            if operation in ['1', '2', '3', '4', '5', '6', 'QUIT']:
                break
            else:
                print("Invalid Operation Code")
                continue
        except ValueError:
            print("Invalid Operation Code")

    if operation == '1':
        OfferRide(user_email)
    elif operation == '2':
        SearchRide(user_email)
    elif operation == '3':
        BookMembersOrCancelBookings(user_email)
    elif operation == '4':
        PostRideRequests(user_email)
    elif operation == '5':
        SearchAndDeleteRideRequests(user_email)
    elif operation == 'QUIT':
        ExitProgram()
    else:
        print("Invalid Code")

def ExitProgram():
    while True:
        option = int(input("Enter 1 if You Want To Exit Program\n Enter 2 if You Want To Logout "))
        if option in [1,2]:
            if option == 1:
                sys.exit(0)
            elif option == 2:
                user_email = None
                LoginOrSignUp()
                break
        else:
            print("Invalid Code, Please Try Again")
            continue



def main():
        global connection,cursor
        path = "./project1.db"
        connect(path)
        LoginOrSignUp()
        
        


        connection.commit()
        connection.close()
        return


if __name__ == "__main__":
    main()