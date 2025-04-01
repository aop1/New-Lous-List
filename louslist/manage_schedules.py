from datetime import datetime
from typing import Dict, List

from louslist.manage_user import get_user_dict
from .models import Schedule, User, Meeting, Comment
from django.forms.models import model_to_dict
from django.utils.timezone import localtime
    

def get_cart(username: str):
    user = User.objects.get(username=username)
    courses = []
    for course in user.cart.all():
        course_dict = model_to_dict(course)
        meetings = []
        db_meetings = Meeting.objects.filter(course=course)
        for meeting in db_meetings:
            meetings.append(model_to_dict(meeting))
        course_dict["meetings"] = meetings
        courses.append(course_dict)
    return courses

def get_schedules(username: str):
    user = User.objects.get(username=username)
    schedules = Schedule.objects.filter(user=user)
    schedules_list = []
    for schedule in schedules:
        schedules_list.append(get_schedule_dict(schedule))
    return schedules_list

#Key - course number (CS 4993) Value - Course Section Dictionary
def course_num_to_sections(course_dicts: List[Dict]) -> Dict[str, Dict]:
    course_sections = {}
    for course_dict in course_dicts:
        course_num = "{subject} {catalog_number}".format_map(course_dict)
        if course_num not in course_sections:
            course_sections[course_num] = [course_dict]
        else:
            course_sections[course_num].append(course_dict)
    return course_sections
    

def time_to_str(date: datetime) -> Dict:
    return {
        "date": localtime(date).strftime("%m/%d/%y"),
        "time": localtime(date).strftime("%I:%M:%S %p")
    }

def can_view(schedule: Schedule, viewer: User, allow_self_view: bool = True) -> bool:
    if schedule.user == viewer and allow_self_view:
        return True
    elif schedule.is_private == 3:
        return True
    elif schedule.is_private == 1:
        return False
    
    owner = User.objects.get(pk=schedule.user.id)
    owner_friends = owner.friends.all()
    if viewer in owner_friends or (viewer == owner and allow_self_view == False):
        return True
    return False

def get_schedule_dict(schedule: Schedule) -> Dict:
    user_schedule = model_to_dict(schedule)
    courses = []
    for course in user_schedule["classes"]:
        course_dict = model_to_dict(course)
        meetings = []
        db_meetings = Meeting.objects.filter(course=course)
        for meeting in db_meetings:
            meetings.append(model_to_dict(meeting))
        course_dict["meetings"] = meetings
        courses.append(course_dict)
    user_schedule["classes"] = courses
    time_dict = time_to_str(schedule.date_created)
    del user_schedule["date_created"]
    user_schedule["date_str"] = time_dict["date"]
    user_schedule["year_str"] = time_dict["time"]
    return user_schedule

def get_schedule_comments(schedule_id: int):
    comments = Comment.objects.filter(schedule=schedule_id)
    comment_dicts = []
    for comment in comments:
        comment_dicts.append(get_comment_dict(comment))
    comment_dicts.reverse()
    return comment_dicts

def get_comment_dict(comment: Comment):
    comment_dict = model_to_dict(comment)
    comment_dict["user"] = get_user_dict(comment.user)
    time_str_dict = time_to_str(comment.date_created)
    comment_dict["date_created"] = time_str_dict["date"]
    comment_dict["time_created"] = time_str_dict["time"]
    return comment_dict


    


