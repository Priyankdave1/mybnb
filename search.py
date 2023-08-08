import click
import tabulate as tb
import  mysql.connector
import haversine as hs
from db import get_db_connection

def merge2Lists(list1, list2):   
    set1 = set(list1)
    set2 = set(list2)
    set3 = set1.intersection(set2)
    return list(set3)
    
@click.pass_context
def returnListingsWithPriceAndAvailability(ctx):
    price_min = ctx.obj['price_min']
    price_max = ctx.obj['price_max']
    start_date = ctx.obj['start_date']
    end_date = ctx.obj['end_date']
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    
    query = "SELECT listingId, SUM(price) AS total_price FROM Availability WHERE dateAvailable BETWEEN %s AND %s and isAvailable = true GROUP BY listingId HAVING COUNT(DISTINCT dateAvailable) = DATEDIFF(%s, %s) + 1;"
    db_cursor.execute(query, (start_date, end_date, end_date, start_date))
    result = db_cursor.fetchall()
    listingIds = []
    total_prices = []
    for row in result:
        
        if(price_min !=None and price_max != None):
            if(row[1] >= price_min and row[1] <= price_max):
                listingIds.append(row[0])
                total_prices.append(row[1])
        elif(price_min != None):
            if(row[1] >= price_min):
                listingIds.append(row[0])
                total_prices.append(row[1])
        elif(price_max != None):
            if(row[1] <= price_max):
                listingIds.append(row[0])
                total_prices.append(row[1])
        else:
            listingIds.append(row[0])
            total_prices.append(row[1])
    if len(listingIds) == 0:
        click.echo('-------------No listings found.-------------')
        db_cursor.close()
        return [],[]
    return listingIds, total_prices

    
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
            click.echo('-------------No listings found.-------------')
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
    listingIds = []
    price_list = []
    listingIds, price_list = returnListingsWithPriceAndAvailability()
    dict = {}
    
    if(listingIds == None or listingIds == []):
        return
    for i in range(len(listingIds)):
        dict[listingIds[i]] = price_list[i] 
    sql_query = 'SELECT * FROM Listing WHERE postalCode LIKE %s AND listingId IN (' + ', '.join(list(map(str, listingIds))) + ')'
    
    if(amenities!= []):
        listingIds = returnListingsWithAmenities()
        if listingIds == []:
            click.echo('-------------No listings found.-------------')
            return
        listingIds = merge2Lists(listingIds, returnListingsWithPriceAndAvailability()[0])
        if(listingIds == []):
            click.echo('-------------No listings found.-------------')
            return
        sql_query = 'SELECT * FROM Listing WHERE postalCode LIKE %s AND listingId IN (' + ', '.join(list(map(str, listingIds))) + ')'
    
    db_cursor.execute(sql_query, (postal_code[0:3]+'%',))
    result = db_cursor.fetchall()
    answer =[]
    if len(result) == 0:
        click.echo('-------------No listings found.-------------')
        db_cursor.close()
        return
    else:
        for row in result:
            row1 = list(row)
            row1.append(float(dict[row[0]]))
            answer.append(row1)
        click.echo('Listings found:')
        if (ctx.obj['sortByPrice']=='asc'):
            answer = sorted(answer, key=lambda x: x[9])
        elif (ctx.obj['sortByPrice']=='desc'):
            answer = sorted(answer, key=lambda x: x[9], reverse=True)
        click.echo(tb.tabulate(answer, headers=['id','city','latitude','longitude','postal code','country','type','address','bedrooms','bathrooms','total price']))

        
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
    listingIds = []
    price_list = []
    listingIds, price_list = returnListingsWithPriceAndAvailability()
    dict = {}

    if(listingIds == None):
        return
    for i in range(len(listingIds)):
        dict[listingIds[i]] = price_list[i]
    sql_query = 'SELECT * FROM Listing WHERE address = %s AND listingId IN (' + ', '.join(list(map(str, listingIds))) + ')'
    if (amenities != []):
        listingIds = returnListingsWithAmenities()
        listingIds = merge2Lists(listingIds, returnListingsWithPriceAndAvailability()[0])
        sql_query = 'SELECT * FROM Listing WHERE address = %s AND listingId IN (' + ', '.join(list(map(str, listingIds))) + ')'
    db_cursor.execute(sql_query, (address,))
    result = db_cursor.fetchall()
    answer =[]
    
    if len(result) == 0:
        click.echo('-------------No listings found.-------------')
        db_cursor.close()
        return
    elif len(result) > 1:
        click.echo('Something went wrong.')
        db_cursor.close()
        return
    else:
        for row in result:
            row1=list(row)
            row1.append(float(dict[row[0]]))
            answer.append(row1)
        if (ctx.obj['sortByPrice']=='asc'):
            answer = sorted(answer, key=lambda x: x[9])
        elif (ctx.obj['sortByPrice']=='desc'):
            answer = sorted(answer, key=lambda x: x[9], reverse=True)
        click.echo('Listings found:')
        click.echo(tb.tabulate(answer, headers=['id','city','latitude','longitude','postal code','country','type','address','bedrooms','bathrooms','total price']))
        db_cursor.close()
        return
     
@click.pass_context
def listingsInRange(ctx):
    amenities = ctx.obj['amenities']
    price_min = ctx.obj['price_min']
    price_max = ctx.obj['price_max']
    start_date = ctx.obj['start_date']
    end_date = ctx.obj['end_date']
    sortbyDistance = click.prompt("Sort by distance? (Overides Price Sorting)",default='n',type=click.Choice(['y','n']))
    longitude = click.prompt("Longitude",type=float)
    if float(longitude) < -180 or float(longitude) > 180:
        click.echo('Longitude must be a number between -180 and 180.')
        return
    latitude = click.prompt("Latitude",type=float)
    if float(latitude) < -90 or float(latitude) > 90:
        click.echo('Latitude must be a number between -90 and 90.')
        return
    rangeInKM = click.prompt("Range in Km (default: 500 Km)",default='500')
    if rangeInKM.isdigit() == False or float(rangeInKM) < 0: 
        click.echo('Range must be a number greater than 0.')
        return
    
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    listingIds = []
    price_list = []
    listingIds,price_list = returnListingsWithPriceAndAvailability()
    if(listingIds == None):
        return
    dict = {}
    for i in range(len(listingIds)):
        dict[listingIds[i]] = price_list[i]
    sql_query = 'SELECT * FROM Listing WHERE listingId IN (' + ', '.join(list(map(str, listingIds))) + ')'
    
    if (amenities != []):
        listingIds = returnListingsWithAmenities()
        listingIds = merge2Lists(listingIds, returnListingsWithPriceAndAvailability()[0])
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
            row1.append(float(dict[row[0]]))
            listings_in_range_by_distance.append(row1)
    if len(listings_in_range_by_distance) == 0:
        click.echo('No listings found within range.')
        db_cursor.close()
        return
    else:
        if (sortbyDistance == 'y'):
            
            listings_in_range_by_distance = sorted(listings_in_range_by_distance, key=lambda x: x[10])

        elif (ctx.obj['sortByPrice']=='asc'):
            listings_in_range_by_distance = sorted(listings_in_range_by_distance, key=lambda x: x[11])
        elif (ctx.obj['sortByPrice']=='desc'):
            listings_in_range_by_distance = sorted(listings_in_range_by_distance, key=lambda x: x[11], reverse=True)
        click.echo('Listings found within range:')
        click.echo(tb.tabulate(listings_in_range_by_distance, headers=['id','city','latitude','longitude','postal code','country','type','address','bedrooms','bathrooms','distance','total price']))
        db_cursor.close()
        return

def haversine(lat1, lon1, lat2, lon2):
    location1 = (lat1, lon1)
    location2 = (lat2, lon2)
    distance = hs.haversine(location1, location2)
    return distance


