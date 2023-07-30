import click
import mysql.connector

db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Password1$',
    database='Airbnb'
)

@click.command()
def register():
    firstname = click.prompt("First name")
    lastname = click.prompt("Last name")
    date_of_birth = click.prompt("Date of birth (YYYY-MM-DD)")
    occupation = click.prompt("Occupation")
    adress = click.prompt("Address")
    sin = click.prompt("SIN")
    username = click.prompt("Username")
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    db_cursor = db_connection.cursor()
    sql_query = 'INSERT INTO User (SIN, adress, ocupation, dob, firstName, lastName, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    db_cursor.execute(sql_query, (sin, adress, occupation, date_of_birth, firstname, lastname, username, password))
    db_connection.commit()
    click.echo('User registration successful.')
    db_cursor.close()
    db_connection.close()

    




@click.command()
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(name):
    click.echo('Hello %s!' % name)



if __name__ == '__main__':
    register()
