import click
from db import get_db_connection

@click.pass_context
def report_wrapper(ctx):
    with click.Context(report1) as ctx:
        report1.invoke(ctx)

@click.pass_context
@click.option('--start_date', help='Start date', required=True)
@click.option('--end_date', help='End date', required=True)
@click.option('--searchBy', default='city',type = click.Choice(['city','postalcode']), help='Search by city or postal code', required=True)
@click.option('--city', default=None, help='City, used only if searchBy is city', required=False)
@click.option('--postalcode', default=None, help='Postal Code, used only if searchBy is postalcode', required=False)
def report1(ctx, start_date, end_date, searchby, city, postalcode):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    if (searchby == 'city'):
        query = "select count(b.bookingId) from BookedBy as b join Listing as l on b.listingId = l.listingId where startDate >= %s and endDate <= %s and city = %s group by city;"
        db_cursor.execute(query, (start_date, end_date, city))
    else:
        query = "select count(b.bookingId) from BookedBy as b join Listing as l on b.listingId = l.listingId where startDate >= %s and endDate <= %s and postalcode = %s group by city;"
        db_cursor.execute(query, (start_date, end_date, postalcode))
    result = db_cursor.fetchall()
    for row in result:
        click.echo(row[0])
    db_cursor.close()
    return

@click.pass_context
@click.option('--country', help='Country', required=True)
@click.option('--city', default=None, help='City', required=False)
@click.option('--postalcode', default=None, help='Postal Code', required=False)
def report2(ctx, country, city, postalcode):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    if (city == None and postalcode == None):
        query = "select count(listingId) from Listing where country = %s group by country;"
        db_cursor.execute(query, (country))
    elif (postalcode == None):
        query = "select count(listingId) from Listing where country = %s and city = %s group by country, city;"
        db_cursor.execute(query, (country, city))
    else:
        query = "select count(listingId) from Listing where country = %s and city = %s and postalcode = %s group by country, city, postalcode;"
        db_cursor.execute(query, (country, city, postalcode))

    result = db_cursor.fetchall()
    for row in result:
        click.echo(row[0])
    db_cursor.close()
    return

@click.pass_context
@click.option('--country', help='Country', required=True)
@click.option('--city', default=None, help='City', required=False)
def report3(ctx, country, city ):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    if (city == None):
        query = "select hostSIN, count(l.listingId) from Listing as l join UserCreatesListing as u where country = %s and l.listingId = u.listingId group by hostSIN order by hostSIN;"
        db_cursor.execute(query, (country))
    else:
        query = "select hostSIN, count(l.listingId) from Listing as l join UserCreatesListing as u where country = %s and l.listingId = u.listingId and city = %s group by hostSIN order by hostSIN;"
        db_cursor.execute(query, (country, city))
    result = db_cursor.fetchall()
    for row in result:
        click.echo(row[0])
    db_cursor.close()
    return


@click.pass_context
@click.option('--country', help='Country', required=True)
@click.option('--city', default=None, help='City', required=False)
def report4(ctx, country, city ):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    if (city == None ):
        query = "select u.hostSIN, count(l.listingId) as num_listings from Listing as l join UserCreatesListing as u on l.listingId = u.listingId join (select count(listingId) as listings, city, country from Listing where country = %s group by country, city) as m on l.country = m.country and l.city = m.city group by u.hostSIN, m.listings having count(l.listingId) >= (m.listings * 0.1) order by u.hostSIN;"
        db_cursor.execute(query, (country))
    else:
        query = "select u.hostSIN, count(l.listingId) as num_listings from Listing as l join UserCreatesListing as u on l.listingId = u.listingId join (select count(listingId) as listings, city, country from Listing where country = %s and city = %s group by country, city) as m on l.country = m.country and l.city = m.city group by u.hostSIN, m.listings having count(l.listingId) >= (m.listings * 0.1) order by u.hostSIN;"
        db_cursor.execute(query, (country, city))
    result = db_cursor.fetchall()
    for row in result:
        click.echo(row[0])
    db_cursor.close()
    return


@click.pass_context
@click.option('--start_date', help='Start Date', required=True)
@click.option('--end_date', help='End Date', required=True)
@click.option('--city', default=None, help='City', required=False)
def report5(ctx, start_date, end_date, city):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    if (city == None):
        query = "select firstName, lastName, count(b.bookingId) as 'Number of Bookings' from BookedBy as b join User as l on b.renterSIN = l.SIN where startDate >= %s and endDate <= %s group by renterSIN order by 'Number of Bookings';"
        db_cursor.execute(query, (start_date, end_date))
    else:
        query = "select firstName, lastName, count(b.bookingId) as 'Number of Bookings' from BookedBy as b join User as u on b.renterSIN = u.SIN join Listing as l on b.listingId = l.listingId where startDate >= %s and endDate <= %s and city = %s group by renterSIN order by 'Number of Bookings';"
        db_cursor.execute(query, (start_date, end_date, city))
    result = db_cursor.fetchall()
    for row in result:
        click.echo(row[0])
    db_cursor.close()
    return


@click.pass_context
@click.option('--run_for', help='Run For', required=True, type=click.Choice(['host', 'renter']))
def report5(ctx, run_for):
    db_connection = get_db_connection()
    db_cursor = db_connection.cursor()
    if (run_for == 'renter'):
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

