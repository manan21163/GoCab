import getpass
import mysql.connector
from mysql.connector import Error
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from geopy import distance as haha
from geopy.exc import GeocoderTimedOut
import random

def get_coordinates(location_string):
    geolocator = Nominatim(user_agent="geo_distance_calculator")
    try:
        location = geolocator.geocode(location_string)
        if location is not None:
            return location.latitude, location.longitude
        else:
            print(f"Could not find coordinates for {location_string}.")
            return None
    except GeocoderTimedOut:
        print("Geocoder service timed out. Please try again later.")
        return None

def calculate_distance(location1, location2):
    coordinates1 = get_coordinates(location1)
    coordinates2 = get_coordinates(location2)
    # lat1, long1 = get_coordinates(location1)
    # lat2, long2 = get_coordinates(location2)

    # coordinates1 = (lat1,long1)
    # coordinates2 = (lat2,long2)
    
    if coordinates1 is not None and coordinates2 is not None:
        # distance = great_circle(coordinates1, coordinates2).kilometers
        distance1 = haha.distance(coordinates1, coordinates2).km
        # print(type(distance1))
        # print(distance1)
        distance1 = round(distance1,2)
        return distance1
    else:
        return None

def getpayment ():
    while(True):
        print("""How would you like to pay for the trip?
1. cash
2. wallet
3. upi
4. debit card
5. paytm
6. CANCEL PAYMENT AND RIDE""")
        paychoice = int(input("Payment choice: "))

        if (paychoice == 1):
            return "cash"
        elif (paychoice == 2):
            return "wallet"
        elif (paychoice == 3):
            return "upi"
        elif (paychoice == 4):
            return "debit card"
        elif (paychoice == 5):
            return "paytm"
        elif (paychoice == 6):
            return "cancel"
        else:
            print("Please choose a valid option.")
            return

def tripandpaymententry (tripid, pickup, droploc, fare, driverid, riderid, paymentid, method):
    query = "insert into trip (trip_id, pickup, droploc, fare, driver_id, rider_id) values (%s,%s,%s,%s,%s,%s);"
    vals = (tripid, pickup, droploc, fare, driverid, riderid)
    cursor.execute(query,vals)
    connection.commit()

    query = "insert into payment (payment_id, method, amount, rider_id, trip_id) values (%s,%s,%s,%s,%s);"
    vals = (paymentid, method, fare, riderid, tripid)
    cursor.execute(query,vals)
    connection.commit()
    return
    

def getcurdriverrating(driverid):
    # query5 = "select * from driver where driver id = %s;"
    # val5 = (driverid,)
    # cursor.execute(query5, val5)
    cursor.execute("select * from driver;")
    x = cursor.fetchall()
    # return x[0][-1]
    for i in x:
        if (i[0] == driverid):
            return i[-1]
        
def getcurdrivertrips(driverid):
    cursor.execute("""SELECT d.*, COUNT(*) AS total_rides FROM trip t
JOIN driver d ON t.driver_id = d.driver_id
GROUP BY t.driver_id;""")
    x = cursor.fetchall()
    for i in x:
        if (i[0] == driverid):
            return i[-1]

def updatedriverrating(driverid):
    print("\nOn a scale of 1 to 10, how much would you rate your ride (Please prove an integer rating)?")
    rating = int(input("Rating: "))
    currating = getcurdriverrating(driverid)
    curtrips = getcurdrivertrips(driverid) - 1
    rating1 = ((currating * curtrips) + rating)/ (curtrips + 1)
    query = "update driver set rating = %s where driver_id = %s"
    vals = (rating1, driverid)
    cursor.execute(query,vals)
    connection.commit()
    return

def showprevinfo(riderid):
    query = "select * from trip where rider_id = %s;"
    vals = (riderid,)
    cursor.execute(query, vals)
    ans = cursor.fetchall()
    # print(ans)
    if(len(ans) != 0):
        for i in range (len(ans)):
            query1 = "select * from driver where driver_id = %s"
            vals1 = (ans[i][4],)
            cursor.execute(query1, vals1)
            ans1 = cursor.fetchall()

            query2 = "select * from payment where trip_id = %s"
            vals2 = (ans[i][0],)
            cursor.execute(query2, vals2)
            ans2 = cursor.fetchall()

            query3 = "select * from vehicle where driver_id = %s;"
            vals3 = (ans[i][4],)
            cursor.execute(query3, vals3)
            ans3 = cursor.fetchall()

            print(f"""Ride {i+1}:
pickup location : {ans[i][1]},
drop location : {ans[i][2]},
ride fare : Rs {ans[i][3]},
payment method used: {ans2[0][1]},
driver name : {ans1[0][1]} {ans1[0][2]} {ans1[0][3]},
driver contact : {ans1[0][4]},
Vehicle : {ans3[0][1]}{ans1[0][3]},
Vehicle Type: {ans3[0][2]},
Vehicle No. : {ans3[0][5]}""")
                  
            return
    else:
        print("You have not done any ride till now.")
        return

def displaydriverdetails(driverid):
    query = "select * from driver where driver_id = %s;"
    vals = (driverid,)
    cursor.execute(query, vals)
    ans = cursor.fetchall()
    query1 = "select * from vehicle where driver_id = %s;"
    vals1 = (driverid,)
    cursor.execute(query1, vals1)
    ans1 = cursor.fetchall()
    print(f"""\nDriver id: {ans[0][0]},
Driver Name: {ans[0][1]} {ans[0][2]} {ans[0][3]},
Driver Contact : {ans[0][4]},
Vehicle : {ans1[0][1]} {ans1[0][3]},
Vehicle Type: {ans1[0][2]},
Vehicle No. : {ans1[0][5]},
Your Cab will be Here Soon..""")

    return

try:
    connection = mysql.connector.connect(host='localhost',
                                         database='dead6_last',
                                         user='root',
                                         password='vivek@123')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server")
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

        cursor.execute("select * from rider")
        x = cursor.fetchall()
        riderid = x[-1][0] + 1

        cursor.execute("select * from trip")
        x = cursor.fetchall()
        tripid = x[-1][0] + 1

        cursor.execute("select * from payment")
        x = cursor.fetchall()
        paymentid = x[-1][0] + 1
        y = 0
        t1 = 0

        basefareride = 9
        basefaresedan = 12
        basefaresuv = 15

        cursor.execute("SHOW TRIGGERS;")
        ans = cursor.fetchall()
        for i in ans:
            if i[0] == "trigger1":
                t1 = 1

        while True:
            print("""\nAV Cabs\n
1. Sign Up
2. Login
3. Exit
Press 0 for Admin Login""")
            a = int(input("Enter your choice: "))
            p = 0
            if a == 3:
                break
            
            elif a == 1:
                firstname = input("First Name: ")
                mid_name = input("Middle Name: ")
                lastname = input("Last Name: ")
                ridercontact = int(input("Contact: "))
                ridermail = input("Email: ")
                cursor.execute("""SELECT * FROM rider""")
                ans = cursor.fetchall()
                for i in ans:
                    if i[5] == ridermail:
                        print("Email already exists. Either use a different mail or login.")
                        y = 1
                        break
                    if i[4] == ridercontact:
                        print("Phone number already exists. Either use a different number or login.")
                        y = 1
                        break
                if(y == 1):
                    continue
                
                query = "insert into rider (rider_id, first_name, middle_name, last_name, contact, email) values (%s,%s,%s,%s,%s,%s);"
                vals = (riderid, firstname, mid_name, lastname, ridercontact, ridermail)
                cursor.execute(query,vals)
                connection.commit()
                riderid += 1

                # cursor.execute("select * from rider where rider_id = 202")
                # print(cursor.fetchall())
                # cursor.execute("delete from rider where rider_id = 202")
                # connection.commit()

            
            elif a == 2:
                mailyes = 0
                contactyes = 0
                y = 0
                ridermail = input("Email: ")
                ridercontact = int(input("Contact: "))
                cursor.execute("""SELECT * FROM rider""")
                ans = cursor.fetchall()
                for i in ans:
                    if i[5] == ridermail and i[4] == ridercontact:
                        mailyes = 1
                        contactyes = 1
                        y = 1
                        curriderid = i[0]
                        break
                
                if(y == 0):
                    print("user not found. either try again or signup")
                    continue
                else:
                    print(f"Welcome, ",i[1],i[2],i[3])

                bookcab = -1
                
                while(True):
                    print("""\n1. Book a Cab
2. View Previous Rides Information
3. Logout""")
                    bookcabchoice = int(input("choice: "))
                    print()

                    if(bookcabchoice == 1):
                        location1 = input("pickup location: ")
                        location2 = input("drop location: ")
                                        
                        distance = calculate_distance(location1, location2)

                        if distance is not None:
                            ridefare = distance * basefareride
                            sedanfare = distance * basefaresedan
                            suvfare = distance * basefaresuv
                            ridefare = round(ridefare,2)
                            sedanfare = round(sedanfare,2)
                            suvfare = round(suvfare,2)
                            cabtypechoice = -1
                            print("Distance :",distance,"km")
                            print(f"Choose the type of ride: \n1. Ride, fare = {ridefare}\n2. Sedan, fare = {sedanfare}\n3. SUV, fare = {suvfare}\nPress 0 to cancel booking")
                            cabtypechoice = int(input("Cab Choice: "))
                            # driverselected = random.randint(1,150)
                            query = "select * from vehicle where vehicletype = %s"

                            if(cabtypechoice == 0):
                                print("Ride Cancelled.")
                                continue
                            
                            elif(cabtypechoice == 1):
                                val = ("ride",)
                                cursor.execute(query, val)
                                ans = cursor.fetchall()
                                ds = len(ans)
                                ds1 = random.randint(1,ds)
                                driverselected = ans[ds1][-1]
                                print(f"\nBooking Ride from {location1} to {location2} with a fare of Rs. {ridefare}\n")
                                
                                paymentchoice = getpayment()
                                displaydriverdetails(driverselected)
                                if (paymentchoice == "cancel"):
                                    print("Ride Cancelled.")
                                    continue
                                else:
                                    tripandpaymententry(tripid, location1, location2, ridefare, driverselected, curriderid, paymentid, paymentchoice)
                                    tripid += 1
                                    paymentid += 1
                                    updatedriverrating(driverselected)
                                
                            
                            elif(cabtypechoice == 2):
                                val = ("sedan",)
                                cursor.execute(query, val)
                                ans = cursor.fetchall()
                                ds = len(ans)
                                ds1 = random.randint(1,ds)
                                driverselected = ans[ds1][-1]
                                print(f"\nBooking Ride from {location1} to {location2} with a fare of Rs. {sedanfare}\n")
                                paymentchoice = getpayment()
                                displaydriverdetails(driverselected)
                                if (paymentchoice == "cancel"):
                                    print("Ride Cancelled.")
                                    continue
                                else:
                                    tripandpaymententry(tripid, location1, location2, sedanfare, driverselected, curriderid, paymentid, paymentchoice)
                                    tripid += 1
                                    paymentid += 1
                                    updatedriverrating(driverselected)
                                

                            elif(cabtypechoice == 3):
                                val = ("suv",)
                                cursor.execute(query, val)
                                ans = cursor.fetchall()
                                ds = len(ans)
                                ds1 = random.randint(1,ds)
                                driverselected = ans[ds1][-1]
                                print(f"\nBooking Ride from {location1} to {location2} with a fare of Rs. {suvfare}\n")
                                paymentchoice = getpayment()
                                displaydriverdetails(driverselected)
                                if (paymentchoice == "cancel"):
                                    print("Ride Cancelled.")
                                    continue
                                else:
                                    tripandpaymententry(tripid, location1, location2, suvfare, driverselected, curriderid, paymentid, paymentchoice)
                                    tripid += 1
                                    paymentid += 1
                                    updatedriverrating(driverselected)

                        else:
                            print("Could not calculate distance due to missing coordinates. Please Try Again.")

                    elif(bookcabchoice == 2):
                        showprevinfo(curriderid)                            

                    elif(bookcabchoice == 3):
                        print("Thank You for using our application. Have a Good Day.")
                        break
                    
                
            elif a==0:
                admail = input("Admin Mail: ")
                adpass = input("Password: ")
                cursor.execute("select * from admin")
                ans = cursor.fetchall()
                y = 0
                for i in ans:
                    if(i[4] == admail and i[-1]== adpass):
                        y = 1
                        break
                if(y==0):
                    print("wrong email or password. try again.")
                elif y == 1:
                    print(f"Welcome Admin {i[1]} {i[2]} {i[3]}")
                    while(True):

                        print("""Menu:
1. Query-1 : Average Fare.
2. Query-2 : Drivers who have not done any trips.
3. Query-3 : Drivers with highest ratings.
4. Query-4 : Number of rides by all drivers.
5. Query-5 : All Details of Distinct Drivers with whom rider with rider_id = 1 has taken a trip with.
6. Query-6 : Drivers with low ratings (between 1 to 5).
7. Query-7 : Details of vehicles whose brand name starts with letter 'm'
8. OLAP-1 : Average Amount groupped by payment method.
9. OLAP-2 : Trips where the fare is greater than or equal to the overall average fare for all trips groupped by rider_id
10. OLAP-3 : CUBE OLAP query on trip table
11. OLAP-4 : Roll Up OLAP query on vehicle table
12. Logout from admin""")
                        
                        a = int(input("Select your query: "))
                        p = 0
                        if a == 12:
                            break
                        elif a == 1:
                            cursor.execute("""SELECT AVG(fare)
AS average_fare FROM trip;""")
                            p = 1
                    
                        elif a == 2:
                            cursor.execute("""SELECT driver.* FROM driver 
WHERE driver.driver_id NOT IN (
    SELECT driver.driver_id 
    FROM driver 
    INNER JOIN trip ON driver.driver_id = trip.driver_id 
    WHERE trip.fare > 0
) ;""")
                            p = 1

                        elif a == 3:
                            cursor.execute("""SELECT * FROM driver
WHERE rating = (
SELECT MAX(rating)
FROM driver
);""")
                            p = 1

                        elif a == 4:
                            cursor.execute("""SELECT d.*, COUNT(*) AS total_rides FROM trip t
JOIN driver d ON t.driver_id = d.driver_id
GROUP BY t.driver_id;""")
                            p = 1

                        elif a == 5:
                            cursor.execute("""SELECT DISTINCT driver.*
FROM driver
JOIN trip ON driver.driver_id = trip.driver_id
WHERE trip.rider_id = 1;""")
                            p = 1

                        elif a == 6:
                            cursor.execute("""SELECT * FROM driver
WHERE driver.rating BETWEEN 1 and 5;""")
                            p = 1

                        elif a == 7:
                            cursor.execute("""SELECT * FROM vehicle
WHERE brand LIKE 'm%';""")
                            p = 1

                        elif a == 8:
                            cursor.execute("""SELECT method, AVG(amount), COUNT(*) as total                        
FROM payment
GROUP BY method""")
                            p = 1

                        elif a == 9:
                            cursor.execute("""SELECT rider_id, AVG(fare)
FROM trip
WHERE trip.fare >= (SELECT AVG(fare) FROM trip)
GROUP BY rider_id""")
                            p = 1

                        elif a == 10:
                            cursor.execute("""SELECT
pickup, droploc, COUNT(*) as total_rides, AVG(fare) as average_fare
FROM trip
GROUP BY pickup,droploc
union all
SELECT
pickup, NULL,COUNT(*) as total_rides, AVG(fare) as average_fare
FROM trip
GROUP BY pickup
union all
SELECT
NULL ,droploc ,COUNT(*) as total_rides, AVG(fare) as average_fare
FROM trip
GROUP BY droploc
union all
SELECT
NULL, NULL, COUNT(*) as total_rides, AVG(fare) as average_fare
FROM trip;""")
                            p = 1

                        elif a == 11:
                            cursor.execute("""SELECT
vehicletype, model, AVG(seatingcap) as sc, COUNT(*) as c
FROM vehicle
GROUP BY vehicletype ,model
union all
SELECT
vehicletype, NULL, AVG(seatingcap) as sc, COUNT(*) as c
FROM vehicle
GROUP BY vehicletype
union all
SELECT
NULL, NULL, AVG(seatingcap) as c, COUNT(*) as c
FROM vehicle;""")
                            p = 1
                                        

            
                        else:
                            print("Make a Valid Choice.")

                        if p == 1:
                            ans = cursor.fetchall()
                            for i in ans:
                                print(i)
                                print()

                            print()
                            print()
             

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")