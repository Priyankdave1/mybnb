import click
from db import get_db_connection
import tabulate as tb

def getTypeListingPrices():
    return {
        "house": 100,
        "apartment": 80,
        "room" : 50
    }

BedroomPrice = 20
BathroomPrice = 10




def getListingPrice(listing):
    listingType = listing[6]
    listingPrices = getTypeListingPrices()
    suggestedPrice = listingPrices[listingType.lower()]
    suggestedPrice += listing[8]*BedroomPrice + listing[9]*BathroomPrice
    getAllAmenitiesForListing_query = "SELECT Amenities.name, price FROM ListingToAmenities JOIN Amenities ON ListingToAmenities.amenity = Amenities.name WHERE listingId = %s"
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    db_cursor.execute(getAllAmenitiesForListing_query, (listing[0],))
    result = db_cursor.fetchall()
    if len(result) == 0:
        print("Suggested price: "+str(suggestedPrice))
        return
    for amenity in result:
        suggestedPrice = suggestedPrice + amenity[1]
    return suggestedPrice
    



essential_amenities = {
    "house": [
        "Towels, bed sheets, soap, and toilet paper",
        "Hangers",
        "Bed linens",
        "Extra pillows and blankets",
        "Room-darkening shades",
        "Iron",
        "Smoke alarm",
        "Carbon monoxide alarm",
        "Fire extinguisher",
        "Fast wifi",
        "Refrigerator",
        "Oven",
        "Dining table",
        "Private entrance",
        "Free parking on premises",
    ],
    "apartment": [
        "Towels, bed sheets, soap, and toilet paper",
        "Hangers",
        "Bed linens",
        "Extra pillows and blankets",
        "Room-darkening shades",
        "Iron",
        "Smoke alarm",
        "Carbon monoxide alarm",
        "Fire extinguisher",
        "Fast wifi",
        "Refrigerator",
        "Microwave",
        "Cooking basics",
        "Dishes and silverware",
        "Freezer",
        "Hot water kettle",
        "Coffee maker",
        "Toaster",
        "Dining table",
        "Private entrance",
        "Free parking on premises",
    ],
    "room": [
        "Towels, bed sheets, soap, and toilet paper",
        "Hangers",
        "Room-darkening shades",
        "Smoke alarm",
        "Fast wifi",
        "Hot water kettle",
        "Coffee maker",
        "Private entrance",
        "Free parking on premises",
        "Free street parking",
    ],
}

def getEssentialAmenities(listing):
    type = listing[6]
    click.echo("Essential amenities for a "+type+":")
    click.echo("\n".join(essential_amenities[type.lower()]))
    return


def getPriceWithAmenities(listing):
    getAllAmenitiesNotInListing_query = "SELECT name, price FROM Amenities WHERE name NOT IN (SELECT amenity FROM ListingToAmenities WHERE listingId = %s)"
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    db_cursor.execute(getAllAmenitiesNotInListing_query, (listing[0],))
    result = db_cursor.fetchall()
    if len(result) == 0:
        print("No amenities to add.")
        return
    print("Amenities you can add that are not in your listing:")
    click.echo("Available amenities:")
    choices = []
    for row in result:
        choices.append(row[0])
        
    
    for idx, choice in enumerate(choices, start=1):
        click.echo(f"  [{idx}] {choice}")
    
    
    selected_indexes = click.prompt('Please select one or more options (comma-separated)', type=click.STRING)
    selected_indexes = [int(idx.strip()) for idx in selected_indexes.split(',')]

    selected_choices = [choices[idx - 1] for idx in selected_indexes if 1 <= idx <= len(choices)]
    click.echo(f'You selected: {", ".join(selected_choices)}')
    
    suggestedPrice = getListingPrice(listing)

    print("Suggested original price per day: "+str(suggestedPrice))

    for amenity in result:
        if amenity[0] in selected_choices:
            suggestedPrice = suggestedPrice + amenity[1]
            click.echo("Added "+amenity[0]+" to listing, price increased by "+str(amenity[1])+" per day.")
    return suggestedPrice










def host_tool_kit(sin):
    getAllYourListings_query = "SELECT listingId,city,latitude,longitude,postalCode,country,type,address,bedrooms,bathrooms FROM UserCreatesListing NATURAL JOIN Listing WHERE hostSIN = %s"
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    db_cursor.execute(getAllYourListings_query, (sin,))
    result = db_cursor.fetchall()
    if len(result) == 0:
        click.echo("You have no listings.")
        return
    click.echo("Your listings:")
    print(result)
    print(tb.tabulate(result, headers=["listingId", "city", "latitude", "longitude", "postalCode", "country", "type", "address","bedrooms","bathrooms"]))
    
    keys=[]
    for row in result:
        keys.append(row[0])
    
    listing_id = click.prompt("Please enter the ID of the listing you want to use the Host Toolkit for", type=int)

    if listing_id not in keys:
        click.echo("Invalid listing ID.")
        return
    
    listing = None
    for row in result:
        if row[0] == listing_id:
            listing = row
            break
    
    click.echo("Listing ID: "+str(listing[0]))

    choice = click.prompt("[1] Generate price, [2] Show essential amenities, [3] Generate price using the addition of more amenities", type=int)
    if choice == 1:
        suggestedPrice = getListingPrice(listing)
        # getAllAmensForListing_query = "SELECT name FROM ListingToAmenities NATURAL JOIN Amenities WHERE listingId = %s"
        # db_cursor.execute(getAllAmensForListing_query, (listing[0],))
        # result = db_cursor.fetchall()
        # if len(result) == 0:
        #     print("Suggested price: "+str(suggestedPrice))
        #     return
        # print("Current amenities for this listing:")
        # print(result)
        # for amenity in result:
        #     print(amenity[0])
        
        print("Suggested price per day: "+str(suggestedPrice))
    elif choice == 2:
        getEssentialAmenities(listing)
    elif choice == 3:
        suggestedPrice = getPriceWithAmenities(listing)
        print("Suggested price per day with new amenities included: "+str(suggestedPrice))
    else:
        click.echo("Invalid choice.")
        return
    db_cursor.close()
    db_connection.close()

    
    
    
    


