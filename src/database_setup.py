from pony.orm import Database

db = Database()

db.bind(provider='postgres', user='postgres', password='password', host='localhost', database='expendit')

db.generate_mapping(create_tables=True)

