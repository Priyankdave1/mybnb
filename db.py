import mysql.connector
import click
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