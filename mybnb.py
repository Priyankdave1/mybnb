from datetime import datetime, timedelta
import click
import mysql.connector
import haversine as hs
import tabulate as tb
import helpers


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


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj["db_connection"] = get_db_connection()
    ctx.obj["username"] = None
    ctx.obj["is_logged_in"] = False
    ctx.obj["userSIN"] = None
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


# SQL queries



delete_listing = "DELETE FROM Listing VALUES (%s, %s, %s, %s, %s, %s)"


check_is_available_on_date = "SELECT * FROM Availability WHERE date_available = %s AND password = %s and SIN = %s"


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

#--------------search for listing in range----------------
@cli.command()
@click.pass_context
def listingsInRange(ctx):
    if not ctx.obj['is_logged_in']:
        click.echo('You are not logged in.')
        return
    longitude = click.prompt("Longitude")
    if longitude.isdigit() == False or float(longitude) < -180 or float(longitude) > 180:
        click.echo('Longitude must be a number between -180 and 180.')
        return
    latitude = click.prompt("Latitude")
    if latitude.isdigit() == False or float(latitude) < -90 or float(latitude) > 90:
        click.echo('Latitude must be a number between -90 and 90.')
        return
    rangeInKM = click.prompt("Range in Km (default: 500 Km)",default='500')
    if rangeInKM.isdigit() == False or float(rangeInKM) < 0: 
        click.echo('Range must be a number greater than 0.')
        return
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    sql_query = 'SELECT * FROM Listing'    
    db_cursor.execute(sql_query)
    result = db_cursor.fetchall()
    listings_in_range_by_distance = []
    for row in result:      
        latitude_listing = row[2]
        longitude_listing= row[3]
        distance = haversine(float(latitude), float(longitude), float(latitude_listing),float(longitude_listing))
        if distance <= float(rangeInKM):
            row1 = list(row)
            row1.append(distance)
            listings_in_range_by_distance.append(row1[1:])
    if len(listings_in_range_by_distance) == 0:
        click.echo('No listings found within range.')
        db_cursor.close()
        return
    else:
        click.echo('Listings found within range:')
        listings_in_range_by_distance.sort(key=lambda x: x[7])
        click.echo(tb.tabulate(listings_in_range_by_distance, headers=['city','latitude','longitude','postal code','country','type','address','distance']))
        db_cursor.close()
        return

def haversine(lat1, lon1, lat2, lon2):
    location1 = (lat1, lon1)
    location2 = (lat2, lon2)
    distance = hs.haversine(location1, location2)
    return distance


@click.command()
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(name):
    click.echo('Hello %s!' % name)

if __name__ == '__main__':
    cli(obj={})

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
    
    Ltype = click.prompt("Type")

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
    latitude = click.prompt("Latitude")
    if not helpers.is_valid_latitude(latitude):
        click.echo('Invalid latitude. Latitude should be a decimal number between -90 and 90.')
        return
    longitude = click.prompt("Longitude")
    if not helpers.is_valid_longitude(longitude):
        click.echo('Invalid longitude. Longitude should be a decimal number between -180 and 180.')
        return
    
    price = click.prompt("Per Night Price")

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

    

    createListing_query = "INSERT INTO Listing (city, latitude, longitude, postalCode, country, type, address) VALUES (%s, %s, %s, %s, %s, %s, %s)"  # Use %s for all placeholders
    db_cursor.execute(createListing_query, (city, latitude, longitude, postalCode, country, Ltype, address))

    db_connection.commit()

    sin = ctx.obj["userSIN"]
    listing_id = db_cursor.lastrowid

    print("Sin: " + str(sin))

    print("Listing ID: " + str(listing_id))

    for choice in selected_choices:
        addAmenities_query = "INSERT INTO ListingToAmenities (listingId, amenity) VALUES (%s, %s)"
        db_cursor.execute(addAmenities_query, (listing_id, choice))

    hostToListing_query = "INSERT INTO HostCreatesListing (hostSIN, listingId) VALUES (%s, %s)"
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
        deleteListing_query = "DELETE FROM Listing WHERE listingId IN (SELECT listingId FROM HostCreatesListing WHERE hostSIN = %s)"
        db_cursor.execute(deleteListing_query, (sin,))
        db_connection.commit()
        db_cursor.close()
        db_connection.close()
        click.echo("Deleted all listings created by Username:", ctx.obj["username"])
        return
    
    getAllListings_query = "SELECT * FROM HostCreatesListing NATURAL JOIN Listing WHERE hostSIN = %s"
    db_cursor.execute(getAllListings_query, (sin,))
    result = db_cursor.fetchall()
    if len(result) == 0:
        click.echo("You have no listings.")
        return
    click.echo("Your listings:")
    # Show table here
    print(result)
    keys=[]
    for row in result:
        keys.append(row[0])

    print(keys)
    
    listing_id = click.prompt("Please enter the ID of the listing you want to delete", type=int )

    if listing_id not in keys:
        click.echo("Invalid listing ID.")
        return
    
    deleteListing_query = "DELETE FROM Listing WHERE listingId = %s"
    db_cursor.execute(deleteListing_query, (listing_id,))
    db_connection.commit()
    db_cursor.close()
    db_connection.close()
    click.echo("Deleted listing ID:", listing_id)
  




@cli.command()
@click.option("--name", prompt="Your name", help="The person to greet.", type=int)
@click.pass_context
def hello(ctx, name):
    click.echo("Hello %s!" % name)


if __name__ == "__main__":
    cli(obj={})
