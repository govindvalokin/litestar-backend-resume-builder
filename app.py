from litestar import Litestar, get, post, Request, delete, put
from database import session
from models import UserInputDetails, UserSkillDetails, UserSocialMediaDetails, UserWorkDetails, UserEducationDetails, UserProjectDetails, UserAddressDetails
from typing import Any


# @get("/resumedata")
# async def getdata(request: Request) -> str:
#     data = UserInputDetails

@post("/add-input")
async def add_input(request: Request, data: dict[str, Any]) -> str:
    print({"data":data})
    user_input_data = UserInputDetails(id=data["id"], name=data["name"], email=data["email"],phone=data["phone"],summary=data["summary"], image_url=data["image_url"])
    if user_input_data:
        session.add(user_input_data)
    user_skill_data = UserSkillDetails(basic_details_id=data["id"], skill_name = data["skill_name"], level=data["level"])
    if user_skill_data:
        session.add(user_skill_data)
    user_address_data = UserAddressDetails(basic_details_id = data["id"], address = data["address"], street = data["street"], city = data["city"], country = data["country"], pincode = data["pincode"])
    if user_address_data:
        session.add(user_address_data)
    social_media = UserSocialMediaDetails(basic_details_id=data["id"], network=data["network"], user_name=data["user_name"], url=data["url"])
    if social_media:
        session.add(social_media)
    user_work_data = UserWorkDetails(basic_details_id = data["id"], organisation = data["organisation"], job_role = data["job_role"], job_location =data["job_location"], key_roles = data["key_roles"], start_date = data["start_date"], end_date = data["end_date"])
    if user_work_data:
        session.add(user_work_data)
    education = UserEducationDetails(basic_details_id = data["id"], qualification = data["qualification"], course_name = data["course_name"], institute_name = data["institute_name"], location=data["location"], academic_year_start=data["academic_year_start"], accademic_year_end = data["accademic_year_end"])
    if education:
        session.add(education)
    user_project_data =  UserProjectDetails(basic_details_id = data["id"], project_title = data["project_title"], skills_earned = data["skills_earned"], description = data["description"])
    if user_project_data:
        session.add(user_project_data)
    
    session.commit()
   
    return "Data added"

@delete("/delete-data/{user_id: int}")
async def delete_data(user_id: int) -> None:
    query = session.query(UserInputDetails).filter_by(id=user_id).first()
    if query:
        session.delete(query)
        session.commit()
        session.close()
        return None

@put("/edit-data/{user_id: int}")
async def edit_data(user_id: int, data: dict[str, Any]) -> str:
    user_input_data = session.query(UserInputDetails).filter_by(id=user_id).first()
    user_address_data = session.query(UserAddressDetails).filter_by(basic_details_id=user_id).first()
    user_social_media_data = session.query(UserSocialMediaDetails).filter_by(basic_details_id=user_id).first()
    user_work_data = session.query(UserWorkDetails).filter_by(basic_details_id=user_id).first()
    user_education_data = session.query(UserEducationDetails).filter_by(basic_details_id= user_id).first()
    user_skill_data = session.query(UserSkillDetails).filter_by(basic_details_id=user_id).first()
    user_project_data = session.query(UserProjectDetails).filter_by(basic_details_id=user_id).first()
    if user_input_data:
        user_input_data.email = data["email"]
        user_input_data.phone = data["phone"]
        user_input_data.image_url = data["image_url"]
        user_input_data.summary = data["summary"]
    if user_address_data:
        user_address_data.address = data["address"]
        user_address_data.street = data["street"]
        user_address_data.city = data["city"]
        user_address_data.country = data["country"]
        user_address_data.pincode = data["pincode"]
    if user_social_media_data:
        user_social_media_data.network = data["network"]
        user_social_media_data.user_name = data["user_name"]
        user_social_media_data.url = data["url"]
    if user_work_data:
        user_work_data.organisation = data["organisation"]
        user_work_data.job_role = data["job_role"]
        user_work_data.job_location = data["job_location"]
        user_work_data.key_roles = data["key_roles"]
        user_work_data.start_date = data["start_date"]
        user_work_data.end_date = data["end_date"]
    if user_education_data:
        user_education_data.qualification = data["qualification"]
        user_education_data.course_name = data["course_name"]
        user_education_data.institute_name = data["institute_name"]
        user_education_data.location = data["location"]
        user_education_data.academic_year_start = data["academic_year_start"]
        user_education_data.accademic_year_end = data["accademic_year_end"]
    if user_skill_data:
        user_skill_data.skill_name = data["skill_name"]
        user_skill_data.level = data["level"]
    if user_project_data:
        user_project_data.project_title = data["project_title"]
        user_project_data.skills_earned = data["skills_earned"]
        user_project_data.description = data["description"]
    session.add(user_input_data)
    session.add(user_address_data)
    session.add(user_social_media_data)
    session.add(user_work_data)
    session.add(user_education_data)
    session.add(user_skill_data)
    session.add(user_project_data)
    session.commit()
    session.close()
    return "Updated"

app = Litestar([add_input, delete_data, edit_data])