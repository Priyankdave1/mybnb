import click
import mysql.connector





@click.command()
@click.option('--user', prompt='Your name', help='Enter your name')
def hello(user):
    click.echo(f'Hello, {user}!')

if __name__ == '__main__':
    hello()
