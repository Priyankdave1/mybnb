from datetime import datetime, timedelta
import click
import mysql.connector
import haversine as hs
import tabulate as tb
import helpers
import search
from db import get_db_connection
import rateAndComment
import hostToolKit
import spacy



# Queries
getAllYourListings_query = "SELECT listingId,city,latitude,longitude,postalCode,country,type,address FROM UserCreatesListing NATURAL JOIN Listing WHERE hostSIN = %s"
isListingAvailable = """SELECT listingId
    FROM Availability
    WHERE dateAvailable BETWEEN %s AND %s AND isAvailable=1 AND listingId = %s
    GROUP BY listingId
    HAVING COUNT(DISTINCT dateAvailable) = DATEDIFF(%s, %s) + 1"""


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
    ctx.obj["sortByPrice"] = None
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
        click.echo("First name must not be empty, and must not contain numbers.")
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
    if not helpers.is_over_18(date_of_birth):
        click.echo("User must be 18 or older")
        return
    occupation = click.prompt("Occupation")
    address = click.prompt("Address")
    if len(address) == 0:
        click.echo(
            "Address must not be empty, and must not contain special characters."
        )
        return
    sin = click.prompt("SIN (9 digits)")
    if len(sin) != 9 or not sin.isdigit():
        click.echo("SIN must be 9 digits long.")
        return
    username = click.prompt("Username")

    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)

    creditCardNumber = click.prompt("Credit Card Number")

    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    sql_query = "INSERT INTO User (SIN, address, occupation, dob, firstName, lastName, username, password, creditCardNO) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    db_cursor.execute(
        sql_query,
        (
            sin,
            address,
            occupation,
            date_of_birth,
            firstname,
            lastname,
            username,
            password,
            creditCardNumber,
        ),
    )
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
    filename = "login_info.txt"
    try:
        with open(filename, "r") as file:
            for line in file:
                if "Username" in line:
                    username = line.split(":")[1].strip()
                    ctx.obj["username"] = username
                if "SIN" in line:
                    sin = line.split(":")[1].strip()
                    ctx.obj["is_logged_in"] = True
                    ctx.obj["userSIN"] = sin
                    return
    except FileNotFoundError:
        click.echo("file not found.")
    except Exception as e:
        click.echo("Error: " + e)
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
    query = "SELECT * FROM Amenity"
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    db_cursor.execute(query)
    result = db_cursor.fetchall()
    db_cursor.close()
    for amenity in amenities:
        if amenity not in result:
            return False
    return True


# --------------search----------------
# add option for ascending or descending sort
@click.option(
    "--sortByPrice",
    "-s",
    help="Sort by price.",
    type=click.Choice(["asc", "desc"], case_sensitive=False),
    default="asc",
)
@click.option(
    "--amenity",
    "-a",
    multiple=True,
    help="Amenity to filter by.",
    default=[],
)
@click.option("--price_min", "-pmin", help="Minimum price to filter by.")
@click.option("--price_max", "-pmax", help="Maximum price to filter by.")
@click.option(
    "--start_date", help="Start date to filter by.", required=True, prompt=True
)
@click.option("--end_date", help="End date to filter by.", required=True, prompt=True)
@cli.command()
@click.pass_context
def search_with_filters(
    ctx, amenity, price_min, price_max, start_date, end_date, sortbyprice
):
    # search filters
    click.echo(sortbyprice)
    ctx.obj["sortByPrice"] = sortbyprice
    ctx.obj["amenities"] = list(amenity)
    ctx.obj["price_min"] = price_min
    ctx.obj["price_max"] = price_max
    ctx.obj["start_date"] = start_date
    ctx.obj["end_date"] = end_date
    
    if checkAmenitiesList(ctx.obj["amenities"]) == False:
        click.echo("Invalid amenity.")
        return
    if not helpers.is_valid_date(start_date):
        click.echo("Invalid Start Date format. Please use the format YYYY-MM-DD.")
        return
    if not helpers.is_valid_date(end_date):
        click.echo("Invalid End Date format. Please use the format YYYY-MM-DD.")
        return
    if start_date > end_date:
        click.echo(
            "Invalid date range. Start Date should be earlier than or equal to End Date."
        )
        return
    while True:
        click.echo("1. Search by postal code")
        click.echo("2. Search by address")
        click.echo("3. Search listing within range")
        click.echo("4. Add/Change filters")
        click.echo("5. Clear filters")
        click.echo("6. Back")
        choice = click.prompt("Please select an option", type=int)
        if choice == 1:
            search.search_listing_by_SimilarpostalCode()
        elif choice == 2:
            search.search_by_address()
        elif choice == 3:
            search.listingsInRange()
        elif choice == 4:
            amenitiesINP = click.prompt(
                "Please enter amenities (comma-separated), :", type=click.STRING
            )
            amenities = amenitiesINP.split(",")
            if not checkAmenitiesList(amenities):
                click.echo("Invalid amenities list. Please use the correct formant.")
                return
            ctx.obj["amenities"] = amenities.split(",")
            ctx.obj["price_min"] = click.prompt(
                "Please enter minimum price (Default = 0):", type=click.INT
            )
            ctx.obj["price_max"] = click.prompt(
                "Please enter maximum price (Default = MAX):", type=click.INT
            )
            ctx.obj["start_date"] = click.prompt(
                "Please enter start date (YYYY-MM-DD):", type=click.STRING
            )
            ctx.obj["end_date"] = click.prompt(
                "Please enter end date (YYYY-MM-DD):", type=click.STRING
            )
            if not helpers.is_valid_date(start_date):
                click.echo(
                    "Invalid Start Date format. Please use the format YYYY-MM-DD."
                )
                return
            if not helpers.is_valid_date(end_date):
                click.echo("Invalid End Date format. Please use the format YYYY-MM-DD.")
                return
            if start_date > end_date:
                click.echo(
                    "Invalid date range. Start Date should be earlier than or equal to End Date."
                )
                return
            ctx.obj["sortByPrice"] = click.prompt(
                "Please enter sort order (asc/desc):",
                type=click.Choice(["asc", "desc"], case_sensitive=False),
                default="asc",
            )
        elif choice == 5:
            ctx.obj["sortByPrice"] = "asc"
            ctx.obj["amenities"] = []
            ctx.obj["price_min"] = 0
            ctx.obj["price_max"] = None
            click.echo(
                "Filters cleared. Start Date and End Date are still in effect, please change them if needed using option 4."
            )
        elif choice == 6:
            return
        else:
            click.echo("Invalid option.")
            continue


@click.command()
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(name):
    click.echo("Hello %s!" % name)


@cli.command()
@click.pass_context
def create_listing(ctx):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    address = click.prompt("Address (Number Street)", type=str)
    # addressArr = address.split(' ')
    # if addressArr[0].isdigit() == False or addressArr[1].isalnum() == False:
    #     click.echo('Address must be in the format: Number Street')
    #     return

    Ltype = click.prompt(
        "Type", type=click.Choice(["Apartment", "House", "Room"], case_sensitive=False)
    )

    Ltype = Ltype.lower()
    # if Ltype not in ["apartment", "house", "room"]:
    #     click.echo("Invalid type. Type must be one of: Apartment, House, Room.")
    #     return
    if Ltype == "apartment":
        aptNum = click.prompt("Apartment Number")
        if len(aptNum) == 0:
            click.echo("Apartment Number must not be empty.")
            return
        elif not aptNum.isdigit():
            click.echo("Apartment Number must be a number.")
            return
        address = address + "," + aptNum
    city = click.prompt("City")
    country = click.prompt("Country")
    postalCode = click.prompt("Postal Code")
    if len(postalCode) != 6:
        click.echo("Postal Code must be 6 characters long.")
        return
    latitude = click.prompt("Latitude", type=float)
    if not helpers.is_valid_latitude(latitude):
        click.echo(
            "Invalid latitude. Latitude should be a decimal number between -90 and 90."
        )
        return
    longitude = click.prompt("Longitude", type=float)
    if not helpers.is_valid_longitude(longitude):
        click.echo(
            "Invalid longitude. Longitude should be a decimal number between -180 and 180."
        )
        return

    bedrooms = 1
    bathrooms = 1
    if Ltype != "room":
        bedrooms = click.prompt("Number of Bedrooms", type=int)

        bathrooms = click.prompt("Number of Bathrooms", type=int)

    price = click.prompt("Per Night Price", type=float)
    if price < 0:
        click.echo("Invalid price.")
        return

    click.echo("Availability Range")
    start_date = click.prompt("Start Date (YYYY-MM-DD)")
    if not helpers.is_valid_date(start_date):
        click.echo(
            "Invalid Start Date. Please use the format YYYY-MM-DD and make sure the date is not in the past"
        )
        return
    end_date = click.prompt("End Date (YYYY-MM-DD)")
    if not helpers.is_valid_date(end_date):
        click.echo("Invalid End Date format. Please use the format YYYY-MM-DD.")
        return
    # Convert the strings to datetime objects for further comparison
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    if start_date > end_date:
        click.echo(
            "Invalid date range. Start Date should be earlier than or equal to End Date."
        )
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
        

    for idx, choice in enumerate(choices, start=1):
        click.echo(f"  [{idx}] {choice}")

    selected_indexes = click.prompt(
        "Please select one or more options (comma-separated)", type=click.STRING
    )
    if selected_indexes.isalnum():
        click.echo("Invalid input. Please enter a comma-separated list of numbers.")
        return
    selected_indexes = [int(idx.strip()) for idx in selected_indexes.split(",")]

    selected_choices = [
        choices[idx - 1] for idx in selected_indexes if 1 <= idx <= len(choices)
    ]
    click.echo(f'You selected: {", ".join(selected_choices)}')

    createListing_query = "INSERT INTO Listing (city, latitude, longitude, postalCode, country, type, address, bedrooms, bathrooms) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"  # Use %s for all placeholders
    db_cursor.execute(
        createListing_query,
        (
            city,
            latitude,
            longitude,
            postalCode,
            country,
            Ltype,
            address,
            bedrooms,
            bathrooms,
        ),
    )

    sin = ctx.obj["userSIN"]
    listing_id = db_cursor.lastrowid


    for choice in selected_choices:
        addAmenities_query = (
            "INSERT INTO ListingToAmenities (listingId, amenity) VALUES (%s, %s)"
        )
        db_cursor.execute(addAmenities_query, (listing_id, choice))

    hostToListing_query = (
        "INSERT INTO UserCreatesListing (hostSIN, listingId) VALUES (%s, %s)"
    )
    db_cursor.execute(hostToListing_query, (sin, listing_id))

    current_date = start_date
    while current_date <= end_date:
        createAvailability_query = "INSERT INTO Availability (dateAvailable, price, listingId) VALUES (%s, %s, %s)"
        db_cursor.execute(createAvailability_query, (current_date, price, listing_id))
        current_date += timedelta(days=1)

    db_connection.commit()

    # Close the cursor and connection
    db_cursor.close()
    db_connection.close()
    print("Inserted listing ID:", listing_id)


@cli.command()
@click.option("--all", is_flag=True, help="Delete all of your listings")
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

    db_cursor.execute(getAllYourListings_query, (sin,))
    result = db_cursor.fetchall()
    if len(result) == 0:
        click.echo("You have no listings.")
        return
    click.echo("Your listings:")
    print(
        tb.tabulate(
            result,
            headers=[
                "listingId",
                "city",
                "latitude",
                "longitude",
                "postalCode",
                "country",
                "type",
                "address",
            ],
        )
    )

    keys = []
    for row in result:
        keys.append(row[0])

    print(keys)

    listing_id = click.prompt(
        "Please enter the ID of the listing you want to delete", type=int
    )

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

    start_date = click.prompt("Start Date (YYYY-MM-DD)")
    if not helpers.is_valid_date(start_date):
        click.echo(
            "Invalid Start Date. Please use the format YYYY-MM-DD and make sure the date is not in the past"
        )
        return
    end_date = click.prompt("End Date (YYYY-MM-DD)")
    if not helpers.is_valid_date(end_date):
        click.echo("Invalid End Date format. Please use the format YYYY-MM-DD.")
        return

    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()

    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    if start_date > end_date:
        click.echo(
            "Invalid date range. Start Date should be earlier than or equal to End Date."
        )
        return
    


    # doesn't include the users listings
    getNumAvailibilityInRange = """
    SELECT L.listingId, L.city, L.latitude, L.longitude, L.postalCode, L.country, L.type, L.address, L.bedrooms, L.bathrooms
    FROM (
        SELECT listingId
        FROM Availability
        WHERE dateAvailable BETWEEN %s AND %s AND isAvailable = 1
        GROUP BY listingId
        HAVING COUNT(DISTINCT dateAvailable) = DATEDIFF(%s, %s) + 1
    ) AS availableListings
    NATURAL JOIN UserCreatesListing AS UCL
    JOIN Listing AS L ON UCL.listingId = L.listingId
    WHERE UCL.hostSIN != %s;
    """



    db_cursor.execute(
        getNumAvailibilityInRange, (start_date, end_date, end_date, start_date, sin)
    )
    result = db_cursor.fetchall()

    if len(result) == 0:
        click.echo("No listings available in that date range.")
        return
    
    print("Available listings:")
    #view the listings
    print(
        tb.tabulate(
            result,
            headers=[
                "listingId",
                "city",
                "latitude",
                "longitude",
                "postalCode",
                "country",
                "type",
                "address",
                "bedrooms",
                "bathrooms"
            ],
        )
    )


    keys = []
    for row in result:
        keys.append(row[0])

    listingId = click.prompt("Listing ID of listing you want to book", type=int)

    if listingId not in keys:
        click.echo("Invalid listing ID.")
        return

    # add booking to bookings table
    createBooking_query = "INSERT INTO BookedBy (startDate, endDate, renterSIN, listingId) VALUES (%s, %s, %s, %s)"
    db_cursor.execute(createBooking_query, (start_date, end_date, sin, listingId))
    booking_id = db_cursor.lastrowid

    # Update those availabilities from the availability table to be booked
    updateAvailabilityToFalse_query = "UPDATE Availability SET isAvailable = 0 WHERE listingId = %s AND dateAvailable BETWEEN %s AND %s"
    # removeAvailability_query = "DELETE FROM Availability WHERE listingId = %s AND dateAvailable BETWEEN %s AND %s"
    db_cursor.execute(
        updateAvailabilityToFalse_query, (listingId, start_date, end_date)
    )

    db_connection.commit()

    db_cursor.close()
    db_connection.close()
    print("Congratulations! You have successfully booked this listing.")
    print("Booking ID:", booking_id)


@cli.command()
@click.pass_context
def cancel_booking(ctx):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    sin = ctx.obj["userSIN"]
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    cancel_as = click.prompt("Cancel booking as (host or renter)", type=str)
    if cancel_as.lower() not in ["host", "renter"]:
        click.echo("Invalid option.")
        return
    if cancel_as.lower() == "host":
        getAllBookings_query = "SELECT bookingId,startDate,endDate,listingId FROM BookedBy NATURAL JOIN UserCreatesListing WHERE hostSIN = %s AND isCancelled = 0 AND startdate>CURDATE()"

    else:
        getAllBookings_query = "SELECT bookingId,startDate,endDate,listingId FROM BookedBy WHERE renterSIN = %s AND isCancelled = 0 AND startdate>CURDATE()"

    db_cursor.execute(getAllBookings_query, (sin,))
    result = db_cursor.fetchall()
    if len(result) == 0:
        click.echo("You have no bookings.")
        return
    click.echo("Your bookings:")
    print(
        tb.tabulate(result, headers=["bookingId", "startDate", "endDate", "listingId"])
    )

    keys = []
    for row in result:
        keys.append(row[0])

    booking_id = click.prompt(
        "Please enter the ID of the booking you want to delete", type=int
    )

    if booking_id not in keys:
        click.echo("Invalid booking ID.")
        return

    listingId = None
    startDate = None
    endDate = None

    for row in result:
        if row[0] == booking_id:
            listingId = row[3]
            startDate = row[1]
            endDate = row[2]
            break

        # add those availabilities back to the availability table
    getBooking_query = (
        "SELECT startDate, endDate, listingId FROM BookedBy WHERE bookingId = %s"
    )
    db_cursor.execute(getBooking_query, (booking_id,))
    result = db_cursor.fetchone()

    if result is None:
        click.echo("Invalid booking ID.")
        return

    startDate = result[0]
    endDate = result[1]
    listingId = result[2]

    addAvailabilityToTrue_query = "UPDATE Availability SET isAvailable = 1 WHERE listingId = %s AND dateAvailable BETWEEN %s AND %s"
    db_cursor.execute(addAvailabilityToTrue_query, (listingId, startDate, endDate))

    deleteBooking_query = (
        "UPDATE BookedBy SET isCancelled = 1, cancelledBy=%s WHERE bookingId = %s"
    )
    db_cursor.execute(deleteBooking_query, (sin, booking_id))
    print("Deleted booking ID:", str(booking_id))
    db_connection.commit()
    db_cursor.close()
    db_connection.close()


@cli.command()
@click.option(
    "--bookingId",
    "-l",
    prompt="Booking ID",
    help="The booking ID of the listing you want to rate and comment on.",
    required=True,
    type=int,
)
@click.pass_context
def Rate_and_Comment_on_listing(ctx, bookingid):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    rateAndComment.rate(bookingid)


@cli.command()
@click.pass_context
@click.option(
    "--accType",
    "-a",
    prompt="Comment or rate as a host or renter?",
    help="The type of account you want to comment or rate as.",
    type=click.Choice(["host", "renter"], case_sensitive=False),
)
@click.option(
    "--bookingId",
    "-b",
    prompt="Booking ID",
    help="The booking ID of the booking you want to rate and comment on.",
    type=int,
)
def rate_and_comment_user(ctx, acctype, bookingid):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    sin = ctx.obj["userSIN"]
    if acctype == "host":
        rateAndComment.view_booking_as_host(sin)
        rateAndComment.comment_as_host(bookingid)
    elif acctype == "renter":
        rateAndComment.view_booking_as_renter(sin)
        rateAndComment.comment_as_renter(bookingid)
    else:
        click.echo("Invalid account type.")
        return


@cli.command()
@click.pass_context
def view_booking_as_renter(ctx):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    sin = ctx.obj["userSIN"]
    rateAndComment.view_booking_as_renter(sin)

@cli.command()
@click.pass_context
def view_booking_as_host(ctx):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    sin = ctx.obj["userSIN"]
    rateAndComment.view_booking_as_host(sin)


@cli.command()
@click.pass_context
@click.option(
    "--accType",
    "-a",
    prompt="Comment or rate as a host or renter?",
    help="The type of account you want to comment or rate as.",
    type=click.Choice(["host", "renter"], case_sensitive=False),
)
@click.option(
    "--bookingId",
    "-b",
    prompt="Booking ID",
    help="The booking ID of the booking you want to rate and comment on.",
    type=int,
)
def rate_and_comment_user(ctx, acctype, bookingid):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    if acctype == "host":
        rateAndComment.comment_as_host(bookingid)
    elif acctype == "renter":
        rateAndComment.comment_as_renter(bookingid)
    else:
        click.echo("Invalid account type.")
        return


@cli.command()
@click.pass_context
def update_availability(ctx):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    sin = ctx.obj["userSIN"]

    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()

    db_cursor.execute(getAllYourListings_query, (sin,))
    result = db_cursor.fetchall()
    if len(result) == 0:
        click.echo("You have no listings.")
        return
    click.echo("Your listings:")
    print(
        tb.tabulate(
            result,
            headers=[
                "listingId",
                "city",
                "latitude",
                "longitude",
                "postalCode",
                "country",
                "type",
                "address",
            ],
        )
    )

    keys = []
    for row in result:
        keys.append(row[0])


    listing_id = click.prompt(
        "Please enter the ID of the listing you want to update the availability",
        type=int,
    )

    if listing_id not in keys:
        click.echo("Invalid listing ID.")
        return

    type = click.prompt(
        "Would you like to remove or insert availability? (Remove or Insert)", type=str
    )
    type = type.lower()
    if type not in ["remove", "insert"]:
        click.echo("Invalid type.")
        return

    start_date = click.prompt("Start Date (YYYY-MM-DD)")
    if not helpers.is_valid_date(start_date):
        click.echo(
            "Invalid Start Date. Please use the format YYYY-MM-DD"
        )
        return
    end_date = click.prompt("End Date (YYYY-MM-DD)")
    if not helpers.is_valid_date(end_date):
        click.echo("Invalid End Date format. Please use the format YYYY-MM-DD.")
        return
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    if start_date > end_date:
        click.echo(
            "Invalid date range. Start Date should be earlier than or equal to End Date."
        )
        return

    isBooked_query = """
            SELECT *
            FROM BookedBy
            WHERE
                listingId = %s
                AND isCancelled = 0
                AND (
                    (startDate <= %s AND endDate >= %s)
                    OR (startDate BETWEEN %s AND %s)
                    OR (endDate BETWEEN %s AND %s)
                )
            """
    db_cursor.execute(
        isBooked_query,
        (listing_id, start_date, end_date, start_date, end_date, start_date, end_date),
    )
    result = db_cursor.fetchall()
    if len(result) > 0:
        click.echo(
            "Listing is booked during this time. Please cancel the booking first."
        )
        return

    if type == "remove":
        db_cursor.execute(
            isListingAvailable, (start_date, end_date, listing_id, end_date, start_date)
        )
        result = db_cursor.fetchall()
        if len(result) == 0:
            click.echo("Listing is unavailable at this time already.")
            return
        removeAvailability_query = "UPDATE Availability SET isAvailable = 0 WHERE dateAvailable BETWEEN %s AND %s AND listingId = %s"
        db_cursor.execute(removeAvailability_query, (start_date, end_date, listing_id))
        print("Removed availability for listing ID:", str(listing_id))
    else:
        # check if the listing is booked during this time
        new_price = click.prompt("New Price", type=float)
        if new_price < 0:
            click.echo("Invalid price.")
            return
        current_date = start_date
        while current_date <= end_date:
            addAvailability_query = "INSERT INTO Availability (listingId, dateAvailable, price, isAvailable) VALUES (%s, %s, %s, 1) ON DUPLICATE KEY UPDATE isAvailable = 1, price = %s"
            db_cursor.execute(
                addAvailability_query, (listing_id, current_date, new_price, new_price)
            )
            current_date += timedelta(days=1)
        print("Added availability for listing ID:", str(listing_id))
    db_connection.commit()
    db_cursor.close()
    db_connection.close()


@cli.command()
@click.pass_context
def update_price(ctx):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return

    sin = ctx.obj["userSIN"]

    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()

    db_cursor.execute(getAllYourListings_query, (sin,))
    result = db_cursor.fetchall()
    if len(result) == 0:
        click.echo("You have no listings.")
        return
    click.echo("Your listings:")
    print(
        tb.tabulate(
            result,
            headers=[
                "listingId",
                "city",
                "latitude",
                "longitude",
                "postalCode",
                "country",
                "type",
                "address",
            ],
        )
    )

    keys = []
    for row in result:
        keys.append(row[0])

    print(keys)

    listing_id = click.prompt(
        "Please enter the ID of the listing you want to update the price", type=int
    )

    if listing_id not in keys:
        click.echo("Invalid listing ID.")
        return

    start_date = click.prompt("Start Date (YYYY-MM-DD)")
    if not helpers.is_valid_date(start_date):
        click.echo(
            "Invalid Start Date. Please use the format YYYY-MM-DD and make sure the date is not in the past"
        )
        return
    end_date = click.prompt("End Date (YYYY-MM-DD)")
    if not helpers.is_valid_date(end_date):
        click.echo("Invalid End Date format. Please use the format YYYY-MM-DD.")
        return
    if start_date > end_date:
        click.echo(
            "Invalid date range. Start Date should be earlier than or equal to End Date."
        )
        return

    # Write a query to check if that listing is Available during those dates

    db_cursor.execute(
        isListingAvailable, (start_date, end_date, listing_id, end_date, start_date)
    )
    result = db_cursor.fetchall()
    if len(result) == 0:
        click.echo("Listing is not available during those dates.")
        return

    # if it is available then update price or tell the user it's not available
    new_price = click.prompt("New Price", type=float)
    if new_price < 0:
        click.echo("Invalid price.")
        return
    updatePrice_query = "UPDATE Availability SET price = %s WHERE listingId = %s AND dateAvailable BETWEEN %s AND %s"
    db_cursor.execute(updatePrice_query, (new_price, listing_id, start_date, end_date))

    db_connection.commit()
    db_cursor.close()
    db_connection.close()
    click.echo("Price updated.")


@click.option(
    "--start_date",
    help="Start date",
    required=True,
    type=click.DateTime(["%Y-%m-%d"]),
    prompt=True,
)
@click.option(
    "--end_date",
    help="End date",
    required=True,
    type=click.DateTime(["%Y-%m-%d"]),
    prompt=True,
)
@click.option(
    "--searchBy",
    default="city",
    type=click.Choice(["city", "postalcode"], case_sensitive=False),
    help="Search by city or postal code",
    required=True,
    prompt=True,
)
@cli.command()
def report1_num_bookings_by_city_postalcode(start_date, end_date, searchby):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    if searchby == "city":
        city = click.prompt("Please enter the city", type=str)
        query = "select count(b.bookingId) from BookedBy as b join Listing as l on b.listingId = l.listingId where startDate >= %s and endDate <= %s and city = %s group by city;"
        db_cursor.execute(query, (start_date, end_date, city))
    else:
        postalcode = click.prompt("Please enter the postal code", type=str)
        if (
            len(postalcode) != 6
            or not postalcode[0].isalpha()
            or not postalcode[1].isdigit()
            or not postalcode[2].isalpha()
            or not postalcode[3].isdigit()
            or not postalcode[4].isalpha()
            or not postalcode[5].isdigit()
        ):
            click.echo("Invalid postal code.")
            return
        query = "select count(b.bookingId) from BookedBy as b join Listing as l on b.listingId = l.listingId where startDate >= %s and endDate <= %s and postalcode = %s group by city;"
        db_cursor.execute(query, (start_date, end_date, postalcode))
    result = db_cursor.fetchall()
    if len(result) == 0:
        click.echo("No results found.")
        return
    for row in result:
        click.echo(row[0])
    db_cursor.close()
    return


@cli.command()
@click.pass_context
@click.option("--country", help="Country", required=True)
@click.option("--city", default=None, help="City", required=False)
@click.option("--postalcode", default=None, help="Postal Code", required=False)
def report2_num_listings_in_area(ctx, country, city, postalcode):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    if city == None and postalcode == None:
        query = (
            "select count(listingId) from Listing where country = %s group by country;"
        )
        db_cursor.execute(query, (country,))
    elif postalcode == None:
        query = "select count(listingId) from Listing where country = %s and city = %s group by country, city;"
        db_cursor.execute(query, (country, city))
    else:
        if (
            len(postalcode) != 6
            or not postalcode[0].isalpha()
            or not postalcode[1].isdigit()
            or not postalcode[2].isalpha()
            or not postalcode[3].isdigit()
            or not postalcode[4].isalpha()
            or not postalcode[5].isdigit()
        ):
            click.echo("Invalid postal code.")
            return
        query = "select count(listingId) from Listing where country = %s and city = %s and postalcode = %s group by country, city, postalcode;"
        db_cursor.execute(query, (country, city, postalcode))

    result = db_cursor.fetchall()
    for row in result:
        click.echo(row[0])
    db_cursor.close()
    return


@cli.command()
@click.pass_context
@click.option("--country", help="Country", required=True)
@click.option("--city", default=None, help="City", required=False)
def report3_host_ranking_by_listings_owned(ctx, country, city):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    if city == None:
        query = "select firstName, lastName, count(l.listingId) from Listing as l join UserCreatesListing as u join User as y where country = %s and l.listingId = u.listingId and y.SIN = u.hostSIN group by hostSIN order by hostSIN;"
        db_cursor.execute(query, (country,))
    else:
        query = "select firstName, lastName, count(l.listingId) from Listing as l join UserCreatesListing as u join User as y where country = %s and l.listingId = u.listingId and city = %s and y.SIN = u.hostSIN group by hostSIN order by hostSIN;"
        db_cursor.execute(query, (country, city))
    result = db_cursor.fetchall()
    for row in result:
        click.echo(row[0] + " " + row[1])
    db_cursor.close()
    return


@cli.command()
@click.pass_context
@click.option("--country", help="Country", required=True)
@click.option("--city", default=None, help="City", required=False)
def report4_possible_commercial_hosts(ctx, country, city):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    if city == None:
        query = "select u.hostSIN, count(l.listingId) as num_listings from Listing as l join UserCreatesListing as u on l.listingId = u.listingId join (select count(listingId) as listings, city, country from Listing where country = %s group by country, city) as m on l.country = m.country and l.city = m.city group by u.hostSIN, m.listings having count(l.listingId) >= (m.listings * 0.1) order by u.hostSIN;"
        db_cursor.execute(query, (country,))
    else:
        query = "select u.hostSIN, count(l.listingId) as num_listings from Listing as l join UserCreatesListing as u on l.listingId = u.listingId join (select count(listingId) as listings, city, country from Listing where country = %s and city = %s group by country, city) as m on l.country = m.country and l.city = m.city group by u.hostSIN, m.listings having count(l.listingId) >= (m.listings * 0.1) order by u.hostSIN;"
        db_cursor.execute(query, (country, city))
    result = db_cursor.fetchall()
    for row in result:
        click.echo(row[0])
    db_cursor.close()
    return


@cli.command()
@click.pass_context
@click.option("--start_date", help="Start Date", required=True)
@click.option("--end_date", help="End Date", required=True)
@click.option("--city", default=None, help="City", required=False)
def report5_rank_renters_by_num_bookings(ctx, start_date, end_date, city):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    if city == None:
        query = "select firstName, lastName, count(b.bookingId) as 'Number of Bookings' from BookedBy as b join User as l on b.renterSIN = l.SIN where startDate >= %s and endDate <= %s group by renterSIN order by 'Number of Bookings';"
        db_cursor.execute(query, (start_date, end_date))
    else:
        query = "select firstName, lastName, count(b.bookingId) as 'Number of Bookings' from BookedBy as b join User as u on b.renterSIN = u.SIN join Listing as l on b.listingId = l.listingId where startDate >= %s and endDate <= %s and city = %s and 'Number of Bookings' >= 2 group by renterSIN order by 'Number of Bookings';"
        db_cursor.execute(query, (start_date, end_date, city))
    result = db_cursor.fetchall()
    for row in result:
        click.echo(row[0])
    db_cursor.close()
    return


@cli.command()
@click.pass_context
@click.option(
    "--run_for", help="Run For", required=True, type=click.Choice(["host", "renter"])
)
def report6_most_cancellations(ctx, run_for):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    if run_for == "renter":
        query = "select distinct firstName, lastName, count(BookingId) as 'Number of Bookings' from BookedBy, User where startDate >= year(curdate()) and isCancelled = true and renterSIN = cancelledBy and cancelledBy = SIN group by cancelledBy order by 'Number of Bookings';"
        db_cursor.execute(query)
    else:
        query = "select distinct firstName, lastName, count(BookingId) as 'Number of Bookings' from BookedBy, User where startDate >= year(curdate()) and isCancelled = true and renterSIN != cancelledBy and cancelledBy = SIN group by cancelledBy order by 'Number of Bookings';"
        db_cursor.execute(query)
    result = db_cursor.fetchall()
    for row in result:
        click.echo(row[0])
    db_cursor.close()
    return

@cli.command()
@click.pass_context
@click.option('--listingId', help='Listing ID', required=True, prompt = True)
def report7_noun(ctx, listingid):
    nlp = spacy.load("en_core_web_sm")
    comments = {}
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    query = "SELECT comment FROM ListingReviewAndComments where listingId = %s;"
    db_cursor.execute(query, (listingid,))
    result = db_cursor.fetchall()
    for row in result:
        text = row[0]
        doc =  nlp(text)
        for noun in doc.noun_chunks:
            if str(noun) in comments:
                comments[str(noun)] += 1
            else:
                comments[str(noun)] = 1
    click.echo("Commom Noun phrases for listing " + listingid + ":")
    answer = []
    for comment in comments:
        if comments[comment] > 1:
            answer.append([comment, comments[comment]])
    answer.sort(key=lambda x: x[1], reverse=True)
    click.echo(tb.tabulate(answer, headers=['Noun Phrase', 'Count']))
    db_cursor.close()
    return

@cli.command()
@click.pass_context
def host_tool_kit(ctx):
    if not ctx.obj["is_logged_in"]:
        click.echo("You are not logged in.")
        return
    sin = ctx.obj["userSIN"]
    hostToolKit.host_tool_kit(sin)



if __name__ == "__main__":
    
    cli(obj={})
