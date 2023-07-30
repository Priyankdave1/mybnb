import click
import mysql.connector

db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Password1$',
    database='Airbnb'
)
is_logged_in = False
user_sin = None
@click.group()
def cli():
    pass

@cli.command()
def register():
    firstname = click.prompt("First name")
    if firstname.isalpha() or len(firstname) == 0:
        click.echo('First name must not be empty, and must not contain numbers.')
        return
    lastname = click.prompt("Last name")
    if lastname.isalpha() or len(lastname) == 0:
        click.echo('Last name must not be empty, and must not contain numbers.')
        return
    date_of_birth = click.prompt("Date of birth (YYYY-MM-DD)")
    if len(date_of_birth) != 10 or date_of_birth[4] != '-' or date_of_birth[7] != '-' or not date_of_birth[:4].isdigit() or not date_of_birth[5:7].isdigit() or not date_of_birth[8:].isdigit() or int(date_of_birth[5:7]) > 12 or int(date_of_birth[8:]) > 31: 
        click.echo('Date of birth must be in the format YYYY-MM-DD.')
        return
    occupation = click.prompt("Occupation")
    if  len(occupation) == 0:
        click.echo('Occupation must not be empty.')
        return
    adress = click.prompt("Address")
    if  len(adress) == 0 or adress.isalphanum():
        click.echo('Address must not be empty, and must not contain special characters.')
        return
    sin = click.prompt("SIN (9 digits)")
    if len(sin) != 9 or not sin.isdigit():
        click.echo('SIN must be 9 digits long.')
        return
    username = click.prompt("Username")
    if len(username) == 0:
        click.echo('Username must not be empty.')
        return
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    if len(password) == 0:
        click.echo('Password must not be empty.')
        return
    db_cursor = db_connection.cursor()
    sql_query = 'INSERT INTO User (SIN, adress, ocupation, dob, firstName, lastName, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    db_cursor.execute(sql_query, (sin, adress, occupation, date_of_birth, firstname, lastname, username, password))
    db_connection.commit()
    click.echo('User registration successful.')
    db_cursor.close()
    return

@cli.command()
@click.option('--username', prompt='Username', help='Your username')
@click.option('--sin', prompt='SIN', help='Your SIN')
@click.password_option(confirmation_prompt=False)
def login(username, sin, password):
    global is_logged_in 
    global user_sin
    if is_logged_in == True:
        click.echo('You are already logged in.')
        return
    
    db_cursor = db_connection.cursor()
    login_query = 'SELECT * FROM User WHERE username = %s AND password = %s and SIN = %s'
    db_cursor.execute(login_query, (username, password, sin))
    result = db_cursor.fetchall()
    if len(result) == 0:
        click.echo('Invalid username, password or SIN.')
        return
    elif len(result) == 1:
        click.echo('Login successful.')
        is_logged_in = True
        user_sin = sin
        
    else:
        click.echo('Something went wrong.')
        return





    




@click.command()
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(name):
    click.echo('Hello %s!' % name)



if __name__ == '__main__':
     cli()
     db_connection.close()
