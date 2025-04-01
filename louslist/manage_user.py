from datetime import datetime
from .models import User, SearchTerm, Course
from typing import Dict, List
from django.forms.models import model_to_dict
from django.conf import settings
import os
from django.db.models.query import QuerySet
from asgiref.sync import sync_to_async

def get_profile_img(user_id: int) -> Dict:
    user = User.objects.get(pk=user_id)
    # Retrieve the last element - os.path.splitext will break it into the file name and extension
    file_ext = os.path.splitext(user.profile_pic)[-1]
    if file_ext != ".png" and file_ext != ".jpg":
        return "yhRgWb.md.png"
    return user.profile_pic


def get_profile_imgs():
    img_file_path = os.path.join(
        settings.BASE_DIR, "louslist/static/louslist/image_urls.txt")
    image_data_file = open(img_file_path, "r")
    image_paths = image_data_file.read().splitlines()
    image_data_file.close()
    return image_paths


def get_graduation_years():
    date = datetime.now()
    if date.month >= 6:
        return list(range(date.year + 1, date.year + 5))
    return list(range(date.year, date.year + 4))


def delete_keys(dict: Dict, *keys: List[str]):
    for key in keys:
        dict.pop(key)


def get_user_dict(user: User):
    user_dict = model_to_dict(user)
    cart_courses = []
    for course in user.cart.all():
        cart_courses.append(model_to_dict(course))
    user_dict["cart"] = cart_courses
    user_dict["friends"] = []
    for friend in user.friends.all():
        user_dict["friends"].append(friend.pk)
    delete_keys(user_dict, "is_superuser", "is_staff", "password",
                "is_active", "last_login", "date_joined")
    return user_dict

def are_friends(user1: User, user2: User):
    user1_friends = user1.friends.all()
    user2_friends = user2.friends.all()
    return (user1 in user2_friends) or (user2 in user1_friends)


def get_recent_searches(user: User) -> QuerySet:
    terms = SearchTerm.objects.filter(user=user)
    terms = terms.order_by("-date_created")
    return terms

@sync_to_async
def update_recent_searches(user: User, search_term: str):
    term = SearchTerm.objects.create(user=user, term=search_term)
    recent_searches = get_recent_searches(user)
    if len(recent_searches) > 5:
        for search_term in reversed(recent_searches[5:]):
            search_term.delete()
    term.save()
        


def is_course_in_cart(user: User, course: Dict) -> bool:
    user_cart = user.cart.all()
    db_courses = user_cart.filter(subject=course["subject"], catalog_number=course["catalog_number"])
    if len(db_courses) > 0:
        return True
    return False

@sync_to_async
def get_courses_in_cart(user: User):
    user_cart = user.cart.all()
    course_nums = []
    for course in user_cart:
        course_nums.append(course.course_number)
    return course_nums
        
    

def get_recent_searches_list(user: User) -> List[str]:
    terms = get_recent_searches(user)
    terms_list = []
    for term in terms:
        terms_list.append(term.term)
    return terms_list

