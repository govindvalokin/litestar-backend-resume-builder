from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#declaring engine for databse
#format: databse, username, password, IP adress, port number, database_name
#echo = True is for displaying the changes made in the database in console 
engine = create_engine("postgresql://postgres:123456789@127.0.0.1:5432/resume_builder")

# Creating session object to interact with DB or manage transaction
Session = sessionmaker(bind=engine)
# Creating session instance
session = Session()