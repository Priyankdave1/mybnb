from datetime import datetime, timedelta
import click
import mysql.connector
import haversine as hs
import tabulate as tb
import helpers
import search

def get_db_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='Password1$',
            database='Airbnb'
        )
    except Exception as e:
        click.echo("Error: "+e)
        return None


def getAvailableListingsForBooking(start_date, end_date, sin):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()

    # Add WHERE SIN != %s to exclude the user's own listings
    getNumAvailibilityInRange= """
         SELECT listingId
FROM (
    SELECT listingId
    FROM Availability
    WHERE dateAvailable BETWEEN %s AND %s AND isAvailable=1
    GROUP BY listingId
    HAVING COUNT(DISTINCT dateAvailable) = DATEDIFF(%s, %s) + 1
) AS availableListings
NATURAL JOIN UserCreatesListing;
    """
   
    db_cursor.execute(getNumAvailibilityInRange, (start_date, end_date, end_date, start_date))
    availableListings = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()
    return availableListings



@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj["db_connection"] = get_db_connection()
    ctx.obj["username"] = None
    ctx.obj["is_logged_in"] = False
    ctx.obj["userSIN"] = None
    ctx.obj["amenities"] = []
    ctx.obj["price_min"] = None
    ctx.obj["price_max"] = None
    ctx.obj["start_date"] = None
    ctx.obj["end_date"] = None
    ctx.obj["sortByPrice"]=None
    user_Logged_in(ctx)


# --------------delete account----------------
@cli.command()
@click.pass_context
def delete_account(ctx):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    delete_account_sql_query = "DELETE FROM User WHERE SIN = %s"
    db_cursor.execute(delete_account_sql_query, (ctx.obj["userSIN"],))
    db_connection.commit()
    ctx.invoke(logout)
    click.echo("User deleted.")
    db_cursor.close()
    return


# --------------register----------------
@cli.command()
def register():
    firstname = click.prompt("First name")
    if not firstname.isalpha() or len(firstname) == 0:
        click.echo('First name must not be empty, and must not contain numbers.')
        return
    lastname = click.prompt("Last name")
    if not lastname.isalpha() or len(lastname) == 0:
        click.echo("Last name must not be empty, and must not contain numbers.")
        return
    date_of_birth = click.prompt("Date of birth (YYYY-MM-DD)")
    if (
        len(date_of_birth) != 10
        or date_of_birth[4] != "-"
        or date_of_birth[7] != "-"
        or not date_of_birth[:4].isdigit()
        or not date_of_birth[5:7].isdigit()
        or not date_of_birth[8:].isdigit()
        or int(date_of_birth[5:7]) > 12
        or int(date_of_birth[8:]) > 31
    ):
        click.echo("Date of birth must be in the format YYYY-MM-DD.")
        return
    if(not helpers.is_over_18(date_of_birth)):
        click.echo("User must be 18 or older")
        return
    occupation = click.prompt("Occupation")
    if len(occupation) == 0:
        click.echo("Occupation must not be empty.")
        return
    address = click.prompt("Address")
    if len(address) == 0:
        click.echo(
            "Address must not be empty, and must not contain special characters."
        )
        return
    sin = click.prompt("SIN (9 digits)")
    # if len(sin) != 9 or not sin.isdigit():
    #     click.echo('SIN must be 9 digits long.')
    #     return
    username = click.prompt("Username")
    if len(username) == 0:
        click.echo("Username must not be empty.")
        return
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    if len(password) == 0:
        click.echo("Password must not be empty.")
        return
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    sql_query = 'INSERT INTO User (SIN, address, occupation, dob, firstName, lastName, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    db_cursor.execute(sql_query, (sin, address, occupation, date_of_birth, firstname, lastname, username, password))
    db_connection.commit()
    click.echo("User registration successful.")
    # Keep user logged in after registration
    db_cursor.close()
    return


def save_login_info(username, sin):
    filename = "login_info.txt"
    with open(filename, "a") as file:
        file.write(f"Username:{username}\nSIN:{sin}\n")
        file.close()
    return

def user_Logged_in(ctx):
    filename = 'login_info.txt'
    try:
        with open(filename, 'r') as file:
            for line in file:
                if 'Username' in line:
                    username = line.split(':')[1].strip()
                    ctx.obj['username'] = username
                if 'SIN' in line:
                    sin = line.split(':')[1].strip()
                    ctx.obj['is_logged_in'] = True
                    ctx.obj['userSIN'] = sin
                    return
    except FileNotFoundError:
        click.echo("file not found.")
    except Exception as e:
        click.echo("Error: "+e)
    return


# --------------login----------------
@cli.command()
@click.pass_context
def login(ctx):
    if ctx.obj["is_logged_in"] == True:
        click.echo("You are already logged in as " + ctx.obj["username"] + ".")
        return
    username = click.prompt("Username")
    if len(username) == 0:
        click.echo("Username must not be empty.")
        return
    password = click.prompt("Password", hide_input=True)
    if len(password) == 0:
        click.echo("Password must not be empty.")
        return
    sin = click.prompt("SIN")
    if len(sin) != 9 or not sin.isdigit():
        click.echo("SIN must be 9 digits long.")
        return
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    login_query = (
        "SELECT * FROM User WHERE username = %s AND password = %s and SIN = %s"
    )

    db_cursor.execute(login_query, (username, password, sin))
    result = db_cursor.fetchall()

    if len(result) == 0:
        click.echo("Invalid username, password, or SIN.")
        db_cursor.close()
        return
    elif len(result) == 1:
        click.echo("Login successful.")
        ctx.obj["is_logged_in"] = True
        ctx.obj["userSIN"] = sin
        save_login_info(username, sin)
        db_cursor.close()
        return
    else:
        click.echo("Something went wrong.")
        db_cursor.close()
        return




# --------------logout----------------


@cli.command()
@click.pass_context
def logout(ctx):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    ctx.obj["is_logged_in"] = False
    ctx.obj["userSIN"] = None
    filename = "login_info.txt"
    with open(filename, "w") as file:
        file.write("")
        file.close()
    click.echo("Logout successful.")
    return



def checkAmenitiesList(amenities):
    if len(amenities) == 0:
        return True
    for amenity in amenities:
        if amenity not in ['Dishwasher','Stove','Oven','Dryer']:
            return False
    return True
# --------------search----------------
#add option for ascending or descending sort
@click.option("--sortByPrice", "-s", help="Sort by price.",type=click.Choice(['asc','desc'],case_sensitive=False),default='asc')
@click.option("--amenity", "-a", multiple=True, help="Amenity to filter by.",type=click.Choice(['Dishwasher','Stove','Oven','Dryer'],case_sensitive=False),default=[])
@click.option("--price_min", "-pmin", help="Minimum price to filter by.")
@click.option("--price_max", "-pmax", help="Maximum price to filter by.")
@click.option("--start_date", help="Start date to filter by.", required=True,prompt=True)
@click.option("--end_date", help="End date to filter by.", required=True,prompt=True)
@cli.command()
@click.pass_context
def search_with_filters(ctx, amenity, price_min, price_max, start_date, end_date, sortbyprice):
    #search filters 
    click.echo(sortbyprice)
    ctx.obj['sortByPrice'] = sortbyprice
    ctx.obj['amenities'] = list(amenity)
    ctx.obj['price_min'] = price_min
    ctx.obj['price_max'] = price_max
    ctx.obj['start_date'] = start_date
    ctx.obj['end_date'] = end_date
    if not helpers.is_valid_date(start_date):
        click.echo('Invalid Start Date format. Please use the format YYYY-MM-DD.')
        return
    if not helpers.is_valid_date(end_date):
        click.echo('Invalid End Date format. Please use the format YYYY-MM-DD.')
        return
    if start_date > end_date:
        click.echo('Invalid date range. Start Date should be earlier than or equal to End Date.')
        return
    while True:
        click.echo('1. Search by postal code')
        click.echo('2. Search by address')
        click.echo('3. Search listing within range')
        click.echo('4. Add/Change filters')
        click.echo('5. Clear filters')
        click.echo('6. Back')
        choice = click.prompt('Please select an option', type=int)
        if choice == 1:
            search.search_listing_by_SimilarpostalCode()
        elif choice == 2:
            search.search_by_address()
        elif choice == 3:
            search.listingsInRange()
        elif choice == 4:
            amenitiesINP = click.prompt('Please enter amenities (comma-separated), :', type=click.STRING)
            amenities = amenitiesINP.split(',')
            if not checkAmenitiesList(amenities):
                click.echo('Invalid amenities list. Please use the correct formant.')
                return
            ctx.obj['amenities'] = amenities.split(',')
            ctx.obj['price_min'] = click.prompt('Please enter minimum price (Default = 0):', type=click.INT)
            ctx.obj['price_max'] = click.prompt('Please enter maximum price (Default = MAX):', type=click.INT)
            ctx.obj['start_date'] = click.prompt('Please enter start date (YYYY-MM-DD):', type=click.STRING)
            ctx.obj['end_date'] = click.prompt('Please enter end date (YYYY-MM-DD):', type=click.STRING)
            if not helpers.is_valid_date(start_date):
                click.echo('Invalid Start Date format. Please use the format YYYY-MM-DD.')
                return
            if not helpers.is_valid_date(end_date):
                click.echo('Invalid End Date format. Please use the format YYYY-MM-DD.')
                return
            if start_date > end_date:
                click.echo('Invalid date range. Start Date should be earlier than or equal to End Date.')
                return
            ctx.obj['sortByPrice'] = click.prompt('Please enter sort order (asc/desc):', type=click.Choice(['asc','desc'],case_sensitive=False),default='asc') 
        elif choice == 5:
            ctx.obj['sortByPrice'] = 'asc'
            ctx.obj['amenities'] = []
            ctx.obj['price_min'] = 0
            ctx.obj['price_max'] = None
            click.echo('Filters cleared. Start Date and End Date are still in effect, please change them if needed using option 4.')
        elif choice == 6:
            return
        else:
            click.echo('Invalid option.')
            continue

@click.command()
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(name):
    click.echo('Hello %s!' % name)

@cli.command()
@click.pass_context
def create_listing(ctx):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    address = click.prompt("Address (Number Street)")
    addressArr = address.split(' ')
    if addressArr[0].isdigit() == False or addressArr[1].isalnum() == False:
        click.echo('Address must be in the format: Number Street')
        return
    
    Ltype = click.prompt("Type", type=click.Choice(['Apartment', 'House', 'Room'], case_sensitive=False))

    Ltype = Ltype.lower()
    if Ltype not in ['apartment', 'house', 'room']:
        click.echo('Invalid type. Type must be one of: Apartment, House, Room.')
        return
    if Ltype == 'apartment':
        aptNum = click.prompt("Apartment Number")
        if len(aptNum) == 0:
            click.echo('Apartment Number must not be empty.')
            return
        elif not aptNum.isdigit():
            click.echo('Apartment Number must be a number.')
            return
        address = address + ',' + aptNum
    city = click.prompt("City")
    country = click.prompt("Country")
    postalCode = click.prompt("Postal Code")
    if len(postalCode) != 6:
        click.echo('Postal Code must be 6 characters long.')
        return
    latitude = click.prompt("Latitude", type=float)
    if not helpers.is_valid_latitude(latitude):
        click.echo('Invalid latitude. Latitude should be a decimal number between -90 and 90.')
        return
    longitude = click.prompt("Longitude", type=float)
    if not helpers.is_valid_longitude(longitude):
        click.echo('Invalid longitude. Longitude should be a decimal number between -180 and 180.')
        return
    bedrooms = click.prompt("Number of Bedrooms", type=int)

    bathrooms = click.prompt("Number of Bathrooms", type=int)
    
    price = click.prompt("Per Night Price", type=float)

    click.echo('Availability Range')
    start_date = click.prompt("Start Date (YYYY-MM-DD)")
    if not helpers.is_valid_date(start_date):
        click.echo('Invalid Start Date format. Please use the format YYYY-MM-DD.')
        return
    end_date = click.prompt("End Date (YYYY-MM-DD)")
    if not helpers.is_valid_date(end_date):
        click.echo('Invalid End Date format. Please use the format YYYY-MM-DD.')
        return
    
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()

    getAllAmenities_query = "SELECT name FROM Amenities"
    db_cursor.execute(getAllAmenities_query)

    result = db_cursor.fetchall()
    choices = []

    click.echo("Available amenities:")
    for row in result:
        choices.append(row[0])
        click.echo(row[0])
    
    for idx, choice in enumerate(choices, start=1):
        click.echo(f"  [{idx}] {choice}")
    
    
    selected_indexes = click.prompt('Please select one or more options (comma-separated):', type=click.STRING)
    selected_indexes = [int(idx.strip()) for idx in selected_indexes.split(',')]

    selected_choices = [choices[idx - 1] for idx in selected_indexes if 1 <= idx <= len(choices)]
    click.echo(f'You selected: {", ".join(selected_choices)}')
    
    
  

    
    # Convert the strings to datetime objects for further comparison
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    if start_date > end_date:
        click.echo('Invalid date range. Start Date should be earlier than or equal to End Date.')
        return

    

    createListing_query = "INSERT INTO Listing (city, latitude, longitude, postalCode, country, type, address, bedrooms, bathrooms) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"  # Use %s for all placeholders
    db_cursor.execute(createListing_query, (city, latitude, longitude, postalCode, country, Ltype, address, bedrooms, bathrooms))

    

    sin = ctx.obj["userSIN"]
    listing_id = db_cursor.lastrowid

    print("Sin: " + str(sin))

    print("Listing ID: " + str(listing_id))

    for choice in selected_choices:
        addAmenities_query = "INSERT INTO ListingToAmenities (listingId, amenity) VALUES (%s, %s)"
        db_cursor.execute(addAmenities_query, (listing_id, choice))

    hostToListing_query = "INSERT INTO UserCreatesListing (hostSIN, listingId) VALUES (%s, %s)"
    db_cursor.execute(hostToListing_query, (sin, listing_id))

    current_date = start_date
    while current_date <= end_date:
        createAvailability_query = "INSERT INTO Availability (dateAvailable, price, listingId) VALUES (%s, %s, %s)"
        db_cursor.execute(createAvailability_query, (current_date, price, listing_id ))
        current_date += timedelta(days=1)
    
    db_connection.commit()

# Close the cursor and connection
    db_cursor.close()
    db_connection.close()
    # print("Inserted listing ID:", listing_id)

@cli.command()
@click.option('--all', is_flag=True, help='Delete all of your listings')
@click.pass_context
def delete_listing(ctx, all):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    sin = ctx.obj["userSIN"]
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    if all:
        deleteListing_query = "DELETE FROM Listing WHERE listingId IN (SELECT listingId FROM UserCreatesListing WHERE hostSIN = %s)"
        db_cursor.execute(deleteListing_query, (sin,))
        db_connection.commit()
        db_cursor.close()
        db_connection.close()
        print("Deleted all listings created by Username:", ctx.obj["username"])
        return
    
    getAllListings_query = "SELECT listingId,city,latitude,longitude,postalCode,country,type,address FROM UserCreatesListing NATURAL JOIN Listing WHERE hostSIN = %s"
    db_cursor.execute(getAllListings_query, (sin,))
    result = db_cursor.fetchall()
    if len(result) == 0:
        click.echo("You have no listings.")
        return
    click.echo("Your listings:")
    print(tb.tabulate(result, headers=["listingId", "city", "latitude", "longitude", "postalCode", "country", "type", "address"], tablefmt="grid"))
    
    keys=[]
    for row in result:
        keys.append(row[0])

    print(keys)
    
    listing_id = click.prompt("Please enter the ID of the listing you want to delete", type=int)

    if listing_id not in keys:
        click.echo("Invalid listing ID.")
        return
    
    deleteListing_query = "DELETE FROM Listing WHERE listingId = %s"
    db_cursor.execute(deleteListing_query, (listing_id,))
    print("Deleted listing ID:", str(listing_id))
    db_connection.commit()
    db_cursor.close()
    db_connection.close()

@cli.command()
@click.pass_context
def create_booking(ctx):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    sin = ctx.obj["userSIN"]
    listingId = click.prompt("Listing ID of listing you want to book", type=int)
    start_date = click.prompt("Start Date (YYYY-MM-DD)")
    if(not helpers.is_valid_date(start_date)):
        click.echo('Invalid Start Date format. Please use the format YYYY-MM-DD.')
        return
    end_date = click.prompt("End Date (YYYY-MM-DD)")
    if(not helpers.is_valid_date(end_date)):
        click.echo('Invalid End Date format. Please use the format YYYY-MM-DD.')
        return
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    if start_date > end_date:
        click.echo('Invalid date range. Start Date should be earlier than or equal to End Date.')
        return
    
    gap=helpers.get_number_of_days_between(start_date, end_date)
    print("Gap: " + str(gap))

    result = getAvailableListingsForBooking(start_date, end_date, sin)
    # print(result)

    if len(result) == 0:
        click.echo("No listings available in that date range.")
        return
    
    keys=[]
    for row in result:
        keys.append(row[0])
    
    if listingId not in keys:
        click.echo("Invalid listing ID.")
        return


    #add booking to bookings table
    createBooking_query = "INSERT INTO BookedBy (startDate, endDate, renterSIN, listingId) VALUES (%s, %s, %s, %s)"
    db_cursor.execute(createBooking_query, (start_date, end_date, sin, listingId))
    booking_id = db_cursor.lastrowid
    

    #Update those availabilities from the availability table to be booked
    updateAvailabilityToFalse_query = "UPDATE Availability SET isAvailable = 0 WHERE listingId = %s AND dateAvailable BETWEEN %s AND %s"
    # removeAvailability_query = "DELETE FROM Availability WHERE listingId = %s AND dateAvailable BETWEEN %s AND %s"
    db_cursor.execute(updateAvailabilityToFalse_query, (listingId, start_date, end_date))

    db_connection.commit()
        
    db_cursor.close()
    db_connection.close()
    print("Congratulations! You have successfully booked this listing.")
    print("Booking ID:", booking_id)



@cli.command()
@click.pass_context
def delete_booking(ctx):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    sin = ctx.obj["userSIN"]
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    getAllBookings_query = "SELECT bookingId,startDate,endDate,listingId FROM BookedBy WHERE renterSIN = %s"
    db_cursor.execute(getAllBookings_query, (sin,))
    result = db_cursor.fetchall()
    if len(result) == 0:
        click.echo("You have no bookings.")
        return
    click.echo("Your bookings:")
    print(tb.tabulate(result, headers=["bookingId", "startDate", "endDate", "renterSIN", "listingId"], tablefmt="grid"))
    
    keys=[]
    for row in result:
        keys.append(row[0])

    # print(keys)
    
    booking_id = click.prompt("Please enter the ID of the booking you want to delete", type=int)

    if booking_id not in keys:
        click.echo("Invalid booking ID.")
        return
    
        #add those availabilities back to the availability table
    getBooking_query = "SELECT startDate, endDate, listingId FROM BookedBy WHERE bookingId = %s"
    db_cursor.execute(getBooking_query, (booking_id,))
    result = db_cursor.fetchone()

    if result is None:
        click.echo("Invalid booking ID.")
        return


    # print(result)

    startDate = result[0]

    endDate = result[1]

    listingId = result[2]
    # print("Listing ID: " + str(listingId))
    # print("Start Date: " + str(startDate))
    # print("End Date: " + str(endDate))


    addAvailabilityToTrue_query = "UPDATE Availability SET isAvailable = 1 WHERE listingId = %s AND dateAvailable BETWEEN %s AND %s"
    db_cursor.execute(addAvailabilityToTrue_query, (listingId, startDate, endDate))
    
    deleteBooking_query = "DELETE FROM BookedBy WHERE bookingId = %s"
    db_cursor.execute(deleteBooking_query , (booking_id,))
    print("Deleted booking ID:", str(booking_id))
    db_connection.commit()
    db_cursor.close()
    db_connection.close()

    
@cli.command()
@click.option("--listingId","-l", prompt="Listing ID", help="The listing ID of the listing you want to rate and comment on.",required=True,type=int)
@click.pass_context
def Rate_and_Comment_on_listing(ctx, listingid):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    sin = ctx.obj["userSIN"]
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    checkListing_query = "SELECT * FROM Listing WHERE listingId = %s"
    db_cursor.execute(checkListing_query, (listingid,))
    result = db_cursor.fetchone()
    if result is None:
        click.echo("Not a valid listingId.")
        return
    checkBooking_query = "SELECT * FROM BookedBy WHERE listingId = %s AND renterSIN = %s"
    db_cursor.execute(checkBooking_query, (listingid,sin))
    result = db_cursor.fetchone()
    if result is None:
        click.echo("This listing had never been booked by you.")
        return
    checkRating_query = "SELECT * FROM ListingReviewAndComments WHERE listingId = %s AND renterSIN = %s"
    db_cursor.execute(checkRating_query, (listingid,sin))
    result = db_cursor.fetchone()
    if result is not None:
        click.echo("You have already rated or commented on this listing.")
        return
    rating = click.prompt("Please enter a rating from 1 to 5")
    if rating == "":
        rating = None
    elif rating < 1 or rating > 5:
        click.echo("Invalid rating.")
        return
    comment = click.prompt("Please enter a comment about the listing.")
    if comment == "":
        comment = None
    addRating_query = "INSERT INTO ListingReviewAndComments (listingId, renterSIN, rating, comment) VALUES (%s, %s, %s, %s)"
    db_cursor.execute(addRating_query, (listingid,sin,rating,comment))
    db_connection.commit()
    db_cursor.close()
    db_connection.close()
    click.echo("Thank you for your rating and comment.")
    return




    






@cli.command()
@click.option("--name", prompt="Your name", help="The person to greet.")
@click.pass_context
def hello(ctx, name):
    click.echo("Hello %s!" % name)


if __name__ == "__main__":
    cli(obj={})
