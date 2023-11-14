from litestar import Litestar, get, post, Request, delete, put
from database import session
from models import UserInputDetails, UserSkillDetails, UserSocialMediaDetails, UserWorkDetails, UserEducationDetails, UserProjectDetails, UserAddressDetails
from typing import Any
import json



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

@post("/create-new-resume")
async def add_resume(request: Request, data: dict[str, Any]) -> str:
    '''API for creating new resume'''
    
    #Getching data from post API request from frontend using keys into a single variable.
    user_input_data = UserInputDetails(
        id=data["basic_details"].get("id"),
        name=data["basic_details"].get("name"),
        email=data["basic_details"].get("email"),
        phone=data["basic_details"].get("phone"),
        summary=data["basic_details"].get("summary"),
        image_url=data["basic_details"].get("image_url")
        )
    if user_input_data:
        #Adding data into session
        session.add(user_input_data)
       
    user_address_data = UserAddressDetails(
        basic_details_id = data["basic_details"].get("id"),
        address = data["location_details"].get("address"),
        street = data["location_details"].get("street"),
        city = data["location_details"].get("city"),
        country = data["location_details"].get("country"),
        pincode = data["location_details"].get("pincode")
        )
    
    if user_address_data:
        session.add(user_address_data)
        
        
        
    if data["skills"]:
        set_of_skills = len(data["skills"])
        for entry in range(set_of_skills):
            user_skill_data = UserSkillDetails(
                basic_details_id=data["basic_details"].get("id"), 
                skill_name = data["skills"][entry].get("skill_name"),
                level=data["skills"][entry].get("level")
                )
            if user_skill_data:    
                session.add(user_skill_data)   
                
        
        
    if data["social_media"]:
        active_accounts = len(data["social_media"])
        for entry in range(active_accounts):
            social_media = UserSocialMediaDetails(
            basic_details_id=data["basic_details"].get("id"),
            network=data["social_media"][entry].get("network"), 
            user_name=data["social_media"][entry].get("user_name"), 
            url=data["social_media"][entry].get("url")
            )
            if social_media:
                session.add(social_media)
                
    
        
    if data["work"]:
        work_history = len(data["work"])
        for entry in range(work_history):
            user_work_data = UserWorkDetails(
                basic_details_id = data["basic_details"].get("id"),
                organisation = data["work"][entry].get("organisation"),
                job_role = data["work"][entry].get("job_role"), 
                job_location =data["work"][entry].get("job_location"),
                key_roles = data["work"][entry].get("key_roles"),
                start_date = data["work"][entry].get("start_date"),
                end_date = data["work"][entry].get("end_date")
                )
            if user_work_data:
                session.add(user_work_data)
                

    
    
    if data["education"]:
        education_history = len(data["education"])
        for entry in range(education_history):
            user_education_data = UserEducationDetails(
                basic_details_id = data["basic_details"].get("id"),
                qualification = data["education"][entry].get("qualification"), 
                course_name = data["education"][entry].get("course_name"),
                institute_name = data["education"][entry].get("institute_name"),
                location=data["education"][entry].get("location"),
                academic_year_start=data["education"][entry].get("academic_year_start"),
                academic_year_end = data["education"][entry].get("academic_year_end")
                )
            if user_education_data:
                session.add(user_education_data)  
                
         
    
    if data["project_details"]:
        number_of_projects = len(data["project_details"])
        for entry in range (number_of_projects):
            user_project_data =  UserProjectDetails(
                basic_details_id = data["basic_details"].get("id"),
                project_title = data["project_details"][entry].get("project_title"),
                skills_earned = data["project_details"][entry].get("skills_earned"),
                description = data["project_details"][entry].get("description")
                )
            if user_project_data:
                session.add(user_project_data)
                
    session.commit()   
    session.close()
    return "Data added"


@delete("/delete-data/{user_id: int}")
async def delete_data(user_id: int) -> None:
    '''API for deleting a particular user data based on id'''
    
    query = session.query(UserInputDetails).filter_by(id=user_id).first()
    if query:
        session.delete(query)
        session.commit()
        session.close()
        return None

# @put("/edit-data/{user_id: int}")
# async def edit_data(user_id: int, data: dict[str, Any]) -> str:
#     user_input_data = session.query(UserInputDetails).filter_by(id=user_id).first()
#     user_address_data = session.query(UserAddressDetails).filter_by(basic_details_id=user_id).first()
#     user_social_media_data = session.query(UserSocialMediaDetails).filter_by(basic_details_id=user_id).first()
#     user_work_data = session.query(UserWorkDetails).filter_by(basic_details_id=user_id).first()
#     user_education_data = session.query(UserEducationDetails).filter_by(basic_details_id= user_id).first()
#     user_skill_data = session.query(UserSkillDetails).filter_by(basic_details_id=user_id).first()
#     user_project_data = session.query(UserProjectDetails).filter_by(basic_details_id=user_id).first()
#     if user_input_data:
#         user_input_data.email = data["email"]
#         user_input_data.phone = data["phone"]
#         user_input_data.image_url = data["image_url"]
#         user_input_data.summary = data["summary"]
#     if user_address_data:
#         user_address_data.address = data["address"]
#         user_address_data.street = data["street"]
#         user_address_data.city = data["city"]
#         user_address_data.country = data["country"]
#         user_address_data.pincode = data["pincode"]
#     if user_social_media_data:
#         user_social_media_data.network = data["network"]
#         user_social_media_data.user_name = data["user_name"]
#         user_social_media_data.url = data["url"]
#     if user_work_data:
#         user_work_data.organisation = data["organisation"]
#         user_work_data.job_role = data["job_role"]
#         user_work_data.job_location = data["job_location"]
#         user_work_data.key_roles = data["key_roles"]
#         user_work_data.start_date = data["start_date"]
#         user_work_data.end_date = data["end_date"]
#     if user_education_data:
#         user_education_data.qualification = data["qualification"]
#         user_education_data.course_name = data["course_name"]
#         user_education_data.institute_name = data["institute_name"]
#         user_education_data.location = data["location"]
#         user_education_data.academic_year_start = data["academic_year_start"]
#         user_education_data.accademic_year_end = data["accademic_year_end"]
#     if user_skill_data:
#         user_skill_data.skill_name = data["skill_name"]
#         user_skill_data.level = data["level"]
#     if user_project_data:
#         user_project_data.project_title = data["project_title"]
#         user_project_data.skills_earned = data["skills_earned"]
#         user_project_data.description = data["description"]
#     session.add(user_input_data)
#     session.add(user_address_data)
#     session.add(user_social_media_data)
#     session.add(user_work_data)
#     session.add(user_education_data)
#     session.add(user_skill_data)
#     session.add(user_project_data)
#     session.commit()
#     session.close()
#     return "Updated"

app = Litestar([show_all_data, add_resume, delete_data, show_resume_data_by_id, show_data_by_search_field])