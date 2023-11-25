from sqlalchemy import String, Column, Date, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from database import engine

#Base is a class derived by using a mapper called declarative_base 
Base = declarative_base()



class UserInputDetails(Base):
    __tablename__ = "basic_details"
    
    id = Column(Integer, primary_key = True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(100), nullable=False)
    image_url = Column(String(100), nullable=False)
    summary = Column(String(100), nullable=False)
    
class UserAddressDetails(Base):
    __tablename__="location_details"
    id = Column(Integer, primary_key = True)
    basic_details_id = Column(Integer, ForeignKey('basic_details.id', ondelete='CASCADE'))
    address = Column(String(100), nullable=False)
    street = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    pincode = Column(String(100), nullable=False)
    
    #defining the relationship with parent table
    job_seeker = relationship("UserInputDetails", backref=backref("location_details",passive_deletes=True))

class UserSocialMediaDetails(Base):
    __tablename__ = "social_media"
    
    id = Column(Integer, primary_key = True)
    basic_details_id = Column(Integer, ForeignKey('basic_details.id', ondelete='CASCADE'))
    network = Column(String(100), nullable=True)
    user_name = Column(String(100), nullable=True)
    url = Column(String(100), nullable=True)

     #defining the relationship with parent table
    job_seeker = relationship("UserInputDetails", backref=backref("social_media",passive_deletes=True))
    
class UserWorkDetails(Base):
    __tablename__ = "work"
    
    id = Column(Integer, primary_key = True)
    basic_details_id = Column(Integer, ForeignKey('basic_details.id', ondelete='CASCADE'))
    organisation = Column(String(100), nullable=True)
    job_role = Column(String(100), nullable=True)
    job_location = Column(String(100), nullable=True)
    key_roles = Column(String(100), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
     #defining the relationship with parent table
    job_seeker = relationship("UserInputDetails", backref=backref("work",passive_deletes=True))
    
class UserEducationDetails(Base):
    __tablename__  = "education"
    
    id = Column(Integer, primary_key = True)
    basic_details_id = Column(Integer, ForeignKey('basic_details.id', ondelete='CASCADE'))
    qualification = Column(String(100), nullable=False)
    course_name = Column(String(100), nullable=False)
    institute_name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    academic_year_start = Column(Date, nullable=False)
    academic_year_end = Column(Date, nullable=False)   
    
     #defining the relationship with parent table
    job_seeker = relationship("UserInputDetails", backref=backref("education",passive_deletes=True))

class UserSkillDetails(Base):
    __tablename__  = "skills"
    
    id = Column(Integer, primary_key = True)
    basic_details_id = Column(Integer, ForeignKey('basic_details.id', ondelete='CASCADE'))
    skill_name = Column(String(100), nullable=True)
    level = Column(String(100), nullable=True)

     #defining the relationship with parent table
    job_seeker = relationship("UserInputDetails", backref=backref("skills",passive_deletes=True))
    
class UserProjectDetails(Base):
    __tablename__  = "project_details"
    
    id = Column(Integer, primary_key = True)
    basic_details_id = Column(Integer, ForeignKey('basic_details.id', ondelete='CASCADE'))
    project_title = Column(String(100), nullable=True)
    skills_earned = Column(String(100), nullable=True)
    description = Column(String(100), nullable=True)   
    
     #defining the relationship with parent table
    job_seeker = relationship("UserInputDetails", backref=backref("project_details",passive_deletes=True))

#creating tables in database 
Base.metadata.create_all(bind=engine, checkfirst = True)
#similar to migration in django