from litestar import Litestar, get, post, Request, delete, put
from database import session
from models import UserInputDetails, UserSkillDetails, UserSocialMediaDetails, UserWorkDetails, UserEducationDetails, UserProjectDetails, UserAddressDetails
#refer any type of data can be accepted, 
from typing import Any
import json
from litestar.config.cors import CORSConfig

import smtplib


# Function for sending_email
def send_email(data):
    # SMTP address and email port address
    server = smtplib.SMTP('smtp.gmail.com',587)
    #To establish a secure connection using transport layer security(tls) 
    server.starttls()
    server.login('govindve.mec@gmail.com','lpie qlev vtlv rdpq') 
    sender = 'govindve.mec@gmail.com'
    recipient = 'govindv@alokin.in'
    subject = 'Resume Builder'
    body = f'''
    Hello,
    New resume created with following details:
    {data["basic_details"]["name"]},
    {data["basic_details"]["email"]},
    {data["basic_details"]["phone"]},
    {data["basic_details"]["image_url"]},
    {data["basic_details"]["summary"]}
    '''
    message = f'Subject: {subject}\n\n{body}'
    server.sendmail(sender,recipient,message)
    print("mail sent")
    

 #passing  all records of a single user or one row or one record
 
def cleaned_data(resume_record):
    '''Remove sqlalchemy instance state, basic_details_id, and id from getting data'''
    
    for key in ["_sa_instance_state", "basic_details_id", "id"]:
        resume_record.pop(key)
    return resume_record



def final_data(resume_records):
    '''Managing multiple data of a single user'''
    
    final_list=[]
    #if only 1 record(eg:skill) is present
    if resume_records.count() == 1: 
        #cleaning and converting one skill into dict. first is for selecting the single record
        resume_record = cleaned_data(resume_records.first().__dict__) 
        new_resume_record = {}
        if resume_record:
            for key,value in resume_record.items():
                new_resume_record[key] = str(value)
            final_list.append(new_resume_record)
        return final_list
    # if multiple record (eg:more than one skills) is present
    elif resume_records.count() > 1:
        for record in resume_records.all():
            record = cleaned_data(record.__dict__)
            for key,value in record.items():
                #Converting all values of dictionary "dict" into string.Then passing this dict(here record) into final_list
                record[key] = str(value)
            final_list.append(record)
        return final_list 
    
    
@get("/resumes/")
async def show_all_data() -> json:
    '''API to display all resumes present in database. Getting basic_details only'''
    
    records = session.query(UserInputDetails).all()
    all_records = {}
    for single_user_data in records:
        record_id = single_user_data.id
        dict_record = single_user_data.__dict__
        dict_record.pop("_sa_instance_state", None)
        key = f"record_{record_id}"
        value = dict_record
        all_records[key] = value
        json_data = json.dumps(all_records)
    return json_data

@get("/filter-resumes/{country_value: str}")
async def show_resume_data_by_country(country_value: str) -> json:
    resume_dict = {}
    resume_data = session.query(UserAddressDetails).filter_by(country=country_value).all()
    for entry in resume_data:    
        entry_id = entry.__dict__.get("basic_details_id")
        resume_basic_data = session.query(UserInputDetails).filter_by(id=entry_id).first().__dict__
        resume_basic_data.pop("_sa_instance_state", None)
        resume_dict[entry_id]=resume_basic_data   
    # print(resume_dict) 
    json_data = json.dumps(resume_dict)
    return json_data

@get("/resume/{field_id: int}")
async def show_resume_data_by_id(field_id: int) -> json:
    '''API to display resume details based on id'''
    
    #Creting an empty dictionary
    resume_dict ={}
    
    #Getting the data of a single user based on id
    user_basic_data = session.query(UserInputDetails).filter_by(id = field_id).first().__dict__
    
    #Cleaning the data
    user_basic_data.pop("_sa_instance_state", None)
    
    #Adding the data as a key value pair into dictionary
    resume_dict["basic_details"] = user_basic_data
    
    
    location_details = session.query(UserAddressDetails).filter_by(basic_details_id = field_id).first().__dict__
    resume_dict["location_details"] = cleaned_data(location_details) 
    
    #Fetching all data(including multiple data of a single user) of a single user based on id.first() is not used beacuse more than one data can be occur
    social_media = session.query(UserSocialMediaDetails).filter_by(basic_details_id = field_id)
    #output of final_data function is a list which is adding into dict as a key-value pair
    resume_dict["social_media"] = final_data(social_media)
    
    work = session.query(UserWorkDetails).filter_by(basic_details_id = field_id)
    resume_dict["work"] = final_data(work) 
    
    education = session.query(UserEducationDetails).filter_by(basic_details_id = field_id)
    resume_dict["education"] = final_data(education) 
    
    skills = session.query(UserSkillDetails).filter_by(basic_details_id = field_id)
    resume_dict["skills"] = final_data(skills) 
    
    project_details = session.query(UserProjectDetails).filter_by(basic_details_id = field_id)
    resume_dict["project_details"] = final_data(project_details)    
    
    json_data = json.dumps(resume_dict)
    return json_data

@get("/search-resume/{field_val: str}", name="search_resume_by_field")
async def show_data_by_search_field(field_val: str) -> json:
    '''API for getting single user basic_data , searching based on email '''
    
    resume_data = session.query(UserInputDetails).filter_by(email=field_val).first()
    data = resume_data.__dict__
    data.pop("_sa_instance_state", None)
    json_data = json.dumps(data)
    return json_data

@get("/search-resume-all/{field_val: str}", name="search_all_resume_by_field")
async def show_all_data_by_search_field(field_val: str) -> json:
    resume_dict = {}
    resume_data = session.query(UserInputDetails).filter_by(email=field_val).all()
    for entry in resume_data:
        entry_id = entry.__dict__.get("id")    
        entry.__dict__.pop("_sa_instance_state", None)
        resume_dict[entry_id]=entry.__dict__
    json_data =json.dumps(resume_dict)
    return json_data




@post("/create-new-resume")
async def add_resume(request: Request, data: dict[str, Any]) -> json:
    
    '''API for creating new resume'''
    
    #Getching data from post API request from frontend using keys into a single variable.
    user_input_data = UserInputDetails(    
        name=data["basic_details"].get("name"),
        email=data["basic_details"].get("email"),
        phone=data["basic_details"].get("phone"),
        summary=data["basic_details"].get("summary"),
        image_url=data["basic_details"].get("image_url")
        )
    flag = False
    if user_input_data:
        #Adding data into session
        session.add(user_input_data)
        session.commit()
        flag = True
    # Fetching the last entered basic_details
    if flag:
        all_basic_details = session.query(UserInputDetails).all()
        #creating a list of dictionaries
        records = [record.__dict__ for record in all_basic_details]
        # Fetching last user_record
        *_,user_record = records
        
        
    #Posting address data   
    user_address_data = UserAddressDetails(
        basic_details_id = user_record["id"],
        address = data["location_details"].get("address"),
        street = data["location_details"].get("street"),
        city = data["location_details"].get("city"),
        country = data["location_details"].get("country"),
        pincode = data["location_details"].get("pincode")
        )
    #Storing into session
    if user_address_data:
        session.add(user_address_data)
        
        
    #Posting Skills    
    if data["skills"]:
        set_of_skills = len(data["skills"])
        for entry in range(set_of_skills):
            user_skill_data = UserSkillDetails(
                # basic_details_id=data["basic_details"].get("id"), 
                basic_details_id = user_record["id"],
                skill_name = data["skills"][entry].get("skill_name"),
                level=data["skills"][entry].get("level")
                )
            if user_skill_data:    
                session.add(user_skill_data)   
                
        
    #Posting social_media data    
    if data["social_media"]:
        active_accounts = len(data["social_media"])
        for entry in range(active_accounts):
            social_media = UserSocialMediaDetails(
            # basic_details_id=data["basic_details"].get("id"),
            basic_details_id = user_record["id"],
            network=data["social_media"][entry].get("network"), 
            user_name=data["social_media"][entry].get("user_name"), 
            url=data["social_media"][entry].get("url")
            )
            if social_media:
                session.add(social_media)
                
    
    # Posting work data    
    if data["work"]:
        work_history = len(data["work"])
        for entry in range(work_history):
            if(data["work"][entry].get("start_date") != "" and data["work"][entry].get("end_date") != ""):
                user_work_data = UserWorkDetails(
                    # basic_details_id = data["basic_details"].get("id"),
                    basic_details_id = user_record["id"],
                    organisation = data["work"][entry].get("organisation"),
                    job_role = data["work"][entry].get("job_role"), 
                    job_location =data["work"][entry].get("job_location"),
                    key_roles = data["work"][entry].get("key_roles"),
                    start_date = data["work"][entry].get("start_date"),
                    end_date = data["work"][entry].get("end_date")
                    )
                if user_work_data:
                    session.add(user_work_data)
            else:
                user_work_data = UserWorkDetails(
                    # basic_details_id = data["basic_details"].get("id"),
                    basic_details_id = user_record["id"],
                    organisation = data["work"][entry].get("organisation"),
                    job_role = data["work"][entry].get("job_role"), 
                    job_location =data["work"][entry].get("job_location"),
                    key_roles = data["work"][entry].get("key_roles"),
                    )
                if user_work_data:
                    session.add(user_work_data)
                

    
    #Posting education data
    if data["education"]:
        education_history = len(data["education"])
        for entry in range(education_history):
            user_education_data = UserEducationDetails(
                # basic_details_id = data["basic_details"].get("id"),
                basic_details_id = user_record["id"],
                qualification = data["education"][entry].get("qualification"), 
                course_name = data["education"][entry].get("course_name"),
                institute_name = data["education"][entry].get("institute_name"),
                location=data["education"][entry].get("location"),
                # academic_year_start=data["education"][entry].get("academic_year_start","2000-12-12"),
                # academic_year_end = data["education"][entry].get("academic_year_end","2000-12-12")
                academic_year_start=data["education"][entry].get("academic_year_start"),
                academic_year_end = data["education"][entry].get("academic_year_end")
                )
            if user_education_data:
                session.add(user_education_data)  
                
         
    #Posting project data
    if data["project"]:
        number_of_projects = len(data["project"])
        for entry in range (number_of_projects):
            user_project_data =  UserProjectDetails(
                # basic_details_id = data["basic_details"].get("id"),
                basic_details_id = user_record["id"],
                project_title = data["project"][entry].get("project_title"),
                skills_earned = data["project"][entry].get("skills_earned"),
                description = data["project"][entry].get("description")
                )
            if user_project_data:
                session.add(user_project_data)
                
    #Reflecting changes into database            
    session.commit()
    #calling email function
    session.close()
    send_email(data)
    return data


@delete("/delete-data/{user_id: int}")
async def delete_data(user_id: int) -> None:
    '''API for deleting a particular user data based on id'''
    
    query = session.query(UserInputDetails).filter_by(id=user_id).first()
    if query:
        session.delete(query)
        session.commit()
        session.close()
        return None

@put("/edit-resume/{user_id: int}")
async def edit_data(user_id: int, data: dict[str, Any]) -> json:
    print(data)
    '''API for updating the existing records'''
    user_input_data = session.query(UserInputDetails).filter_by(id=user_id).first()
    if user_input_data:
        record = user_input_data
        user_data = data.get("basic_details") # collecting details using key
        record.name = user_data.get("name")
        record.email = user_data.get("email")
        record.phone = user_data.get("phone")
        record.image_url =user_data.get("image_url")
        record.summary = user_data.get("summary")
        session.add(record)
        
    user_address_data = session.query(UserAddressDetails).filter_by(basic_details_id=user_id).first()
    if user_address_data:
        record = user_address_data
        address_data = data.get("location_details")
        record.address = address_data.get("address")
        record.street = address_data.get("street")
        record.city = address_data.get("city")
        record.country = address_data.get("country")
        record.pincode = address_data.get("pincode")
        session.add(user_address_data)
        
        
    user_education_data = session.query(UserEducationDetails).filter_by(basic_details_id= user_id).all()
    if user_education_data:
        count = 0
        for element in user_education_data:
            education_data = data.get("education")[count]
            element.qualification = education_data.get("qualification")
            element.course_name = education_data.get("course_name")
            element.institute_name = education_data.get("institute_name")
            element.location = education_data.get("location")
            element.academic_year_start = education_data.get("academic_year_start")
            element.academic_year_end = education_data.get("academic_year_end")
            session.add(element)
            count += 1
            
    user_social_media_data = session.query(UserSocialMediaDetails).filter_by(basic_details_id=user_id).all()
    if user_social_media_data:
        count = 0
        for element in user_social_media_data:
            social_media_data = data.get("social_media")[count]
            element.network = social_media_data.get("network")
            element.user_name = social_media_data.get("user_name")
            element.url = social_media_data.get("url")
            session.add(element)
            count += 1
            
    user_work_data = session.query(UserWorkDetails).filter_by(basic_details_id=user_id).all()
    if user_work_data:
        count = 0
        for element in user_work_data:
            work_data = data.get("work")[count]
            if(work_data.get("start_date") == "None" and work_data.get("end_date") == "None"):
                element.organisation = work_data.get("organisation")
                element.job_role = work_data.get("job_role")
                element.job_location = work_data.get("job_location")
                element.key_roles = work_data.get("key_roles")
                session.add(element)
                count += 1
            else:
                element.organisation = work_data.get("organisation")
                element.job_role = work_data.get("job_role")
                element.job_location = work_data.get("job_location")
                element.key_roles = work_data.get("key_roles")
                element.start_date = work_data.get("start_date")
                element.end_date = work_data.get("end_date")
                session.add(element)
                count += 1
    
    user_skill_data = session.query(UserSkillDetails).filter_by(basic_details_id=user_id).all()
    if user_skill_data:
        count = 0
        for element in user_skill_data:
            skill_data = data.get("skills")[count]
            element.skill_name = skill_data.get("skill_name")
            element.level = skill_data.get("level")
            session.add(element)
            count += 1
            
    user_project_data = session.query(UserProjectDetails).filter_by(basic_details_id=user_id).all()
    if user_project_data:
        count = 0
        for element in user_project_data:
            project_data =data.get("project")[count]
            element.project_title = project_data.get("project_title")
            element.skills_earned = project_data.get("skills_earned")
            element.description = project_data.get("description")
            session.add(element)
            count += 1
            
    #Reflecting changes into database
    session.commit()
    session.close()
    return json.dumps("Updated")

'''For API, defining the exact origins from where (frontend ip address) backend can receive data.
cross origin resource sharing'''
cors_config = CORSConfig(
            allow_origins=["*"]
        )

''' Declaring functions in litestar app
 app is an instance of Litestar class 
 we are passing functions as a list and sending it into roothandler as a parameter'''
app = Litestar(
        [
            show_all_data,
            edit_data,
            add_resume,
            delete_data,
            show_resume_data_by_id,
            show_data_by_search_field,
            show_resume_data_by_country,
            show_all_data_by_search_field
        ], 
        cors_config=cors_config,
        debug=True
    )