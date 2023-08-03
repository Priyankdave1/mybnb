import click
import tabulate as tb
import  mysql.connector
import haversine as hs


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
    
@click.pass_context
def returnListingsWithAmenities(ctx):
    amenities = ctx.obj['amenities']
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()  
    if(amenities!= []):
        query = "SELECT listingId FROM ListingToAmenities WHERE amenity IN ({}) GROUP BY listingId HAVING COUNT(amenity) >= {};"
        amenities_commaSEP = ', '.join(['%s'] * len(amenities))
        sql_query = query.format(amenities_commaSEP, len(amenities))
        db_cursor.execute(sql_query, tuple(amenities))

        result = db_cursor.fetchall()
        listingIds = []
        for row in result:
            listingIds.append(row[0])
        if len(listingIds) == 0:
            click.echo('No listings found.')
            db_cursor.close()
            return
        return listingIds

@click.pass_context
def search_listing_by_SimilarpostalCode(ctx):
    amenities = ctx.obj['amenities']
    price_min = ctx.obj['price_min']
    price_max = ctx.obj['price_max']
    start_date = ctx.obj['start_date']
    end_date = ctx.obj['end_date']
    postal_code = click.prompt("Postal Code")
    if len(postal_code) == 0:
        click.echo('Postal Code must not be empty.')
        return
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()    

    if(amenities!= []):
        listingIds = returnListingsWithAmenities()
        sql_query = 'SELECT * FROM Listing WHERE postalCode LIKE %s AND listingId IN (' + ', '.join(list(map(str, listingIds))) + ')'
        db_cursor.execute(sql_query, (postal_code[0:3]+'%',))
        result = db_cursor.fetchall()
        click.echo('Listings found:')
        click.echo(tb.tabulate(result, headers=['id','city','latitude','longitude','postal code','country','type','address']))



        
@click.pass_context
def search_by_address(ctx):
    amenities = ctx.obj['amenities']
    price_min = ctx.obj['price_min']
    price_max = ctx.obj['price_max']
    start_date = ctx.obj['start_date']
    end_date = ctx.obj['end_date']
    address = click.prompt("Address")
    if len(address) == 0:
        click.echo('Address must not be empty.')
        return
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    sql_query = 'SELECT * FROM Listing WHERE address = %s'    
    if (amenities != []):
        listingIds = returnListingsWithAmenities()
        sql_query = 'SELECT * FROM Listing WHERE address = %s AND listingId IN (' + ', '.join(list(map(str, listingIds))) + ')'
    
    db_cursor.execute(sql_query, (address,))
    result = db_cursor.fetchall()
    answer =[]
    for row in result:
        answer.append(row[1:])
    if len(result) == 0:
        click.echo('No listings found.')
        db_cursor.close()
        return
    elif len(result) > 1:
        click.echo('Something went wrong.')
        db_cursor.close()
        return
    else:
        click.echo('Listings found:')
        click.echo(tb.tabulate(answer, headers=['city','latitude','longitude','postal code','country','type','address']))
        db_cursor.close()
        return
    
    


@click.pass_context
def listingsInRange(ctx):
    amenities = ctx.obj['amenities']
    price_min = ctx.obj['price_min']
    price_max = ctx.obj['price_max']
    start_date = ctx.obj['start_date']
    end_date = ctx.obj['end_date']
    sortby = click.prompt("Sort by price or distance? (P/D)")
    while sortby != 'P' or sortby != 'D':
        click.echo('Please enter P or D.')
        sortby = click.prompt("Sort by price or distance? (P/D)")
    ascend_or_descend = click.prompt("Ascending or descending? (A/D)")
    while ascend_or_descend != 'A' or ascend_or_descend != 'D':
        click.echo('Please enter A or D.')
        ascend_or_descend = click.prompt("Ascending or descending? (A/D)")
    

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
    if (amenities != []):
        listingIds = returnListingsWithAmenities()
        sql_query = 'SELECT * FROM Listing WHERE listingId IN (' + ', '.join(list(map(str, listingIds))) + ')' 
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
        if sortby == 'P':
            if ascend_or_descend == 'A':
                listings_in_range_by_distance.sort(key=lambda x: x[4])
            elif ascend_or_descend == 'D':
                listings_in_range_by_distance.sort(key=lambda x: x[4], reverse=True)
        elif sortby == 'D':
            if ascend_or_descend == 'A':
                listings_in_range_by_distance.sort(key=lambda x: x[7])
            else: 
                listings_in_range_by_distance.sort(key=lambda x: x[7], reverse=True)              
    #remove
        listings_in_range_by_distance.sort(key=lambda x: x[7])
        click.echo(tb.tabulate(listings_in_range_by_distance, headers=['city','latitude','longitude','postal code','country','type','address','distance']))
        db_cursor.close()
        return

def haversine(lat1, lon1, lat2, lon2):
    location1 = (lat1, lon1)
    location2 = (lat2, lon2)
    distance = hs.haversine(location1, location2)
    return distance


