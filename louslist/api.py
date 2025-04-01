import json
from django.http import JsonResponse, HttpRequest
from .models import Course, Schedule, Comment, User
from json import loads
from .manage_schedules import get_schedules
from django.utils import timezone
import traceback

def update_account(request):
    try:
        data = loads(request.body)
        username = data['username'] if 'username' in data else ''
        first_name =data['first_name'] if 'first_name' in data else ''
        last_name = data['last_name'] if 'last_name' in data else ''
        major = data['major'] if 'major' in data else ''
        grad_year = data['grad_year'] if 'grad_year' in data else 0
        profile_pic = data['profile_pic'] if 'profile_pic' in data else ''
        if username and username != request.user.username and len(User.objects.filter(username=username)) > 0:
            return JsonResponse({'result': 'User Already Exists'})
        elif username:
            request.user.username = username
            
        if first_name:
            request.user.first_name = first_name
        if last_name:
            request.user.last_name = last_name
        if major:
            request.user.major = major
        if grad_year and (type(grad_year) == int or grad_year.isnumeric()):
            request.user.grad_year = grad_year
        if profile_pic:
            request.user.profile_pic = profile_pic
        request.user.save()
        return JsonResponse({'result': 'Success'})
    except Exception as e:
        return JsonResponse({'result': 'Failure'})

def add_friend(request):
    try:
        data = loads(request.body)
        user_id = data['user_id'] if 'user_id' in data else 0
        username = data['username'] if 'username' in data else ''
        friend = User.objects.get(pk=user_id) if User.objects.filter(pk=user_id).exists() \
            else User.objects.get(username=username)
        request.user.friends.add(friend)
        friend.friends.add(request.user)
        return JsonResponse({'result': 'Success'})
    except:
        return JsonResponse({'result': 'Failure'})

def remove_friend(request):
    try:
        data = loads(request.body)
        user_id = data['user_id'] if 'user_id' in data else 0
        username = data['username'] if 'username' in data else ''
        friend = User.objects.get(pk=user_id) if User.objects.filter(pk=user_id).exists() \
            else User.objects.get(username=username)
        request.user.friends.remove(friend)
        friend.friends.remove(request.user)
        return JsonResponse({'result': 'Success'})
    except:
        return JsonResponse({'result': 'Failure'})

def post_comment(request):
    try:
        data = loads(request.body)
        schedule_id = data['schedule_id']
        text = data['text']
        schedule = Schedule.objects.get(pk=schedule_id)
        comment = Comment.objects.create(user=request.user, schedule=schedule, text=text)
        return JsonResponse({'result': 'Success', 'id': comment.id})
    except Exception as e:
        print(e)
        return JsonResponse({'result': 'Failure'})

def delete_comment(request):
    try:
        data = loads(request.body)
        comment_id = data['comment_id']
        comment = Comment.objects.get(pk=comment_id)
        if request.user == comment.user:
            comment.delete()
            return JsonResponse({'result': 'Success'})
        return JsonResponse({'result': 'Access denied'})
    except:
        return JsonResponse({'result': 'Failure'})

def add_course_to_cart(request):
    try:
        data = loads(request.body)
        subject = data['subject']
        course_number = data['course_number']
        description = data['description']
        catalog_number = data['catalog_number']
        course_section = data['course_section']
        component = data['component']
        units = data['units']
        #enrollment_total = data['enrollment_total']
        #class_capacity = data['class_capacity']
        enrollment_total = 0
        class_capacity = 0
        instructor = data['instructor']
        topic = data['topic']
        meetings = data['meetings']
        if(not Course.objects.filter(subject=subject, course_number=course_number).exists()):
            course = Course.create_course(subject=subject, catalog_number=catalog_number, description=description, course_number=course_number,
            course_section=course_section, component=component, units=units, enrollment_total=enrollment_total,
            class_capacity=class_capacity, instructor=instructor, topic=topic, meetings=meetings)
        else:
            course = Course.objects.get(subject=subject, course_number=course_number)
        request.user.cart.add(course)
        return JsonResponse({'result': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'result': 'Failure'})

def add_schedule(request):
    data = loads(request.body)
    semester = data["semester"]
    name = data["name"]
    color = data["color"]
    try:
        s = Schedule.objects.create(user=request.user, name=name, semester=semester, color=color)
        return JsonResponse({'result': 'Success', 'schedule_id': s.pk})
    except:
        return JsonResponse({'result': 'Failure'})

def add_course_to_schedule(request):
    try:
        data = loads(request.body)
        course_number = data['course_number']
        schedule_id = data['schedule_id']
        #meetings = data['meetings']
        meetings = Course.objects.get(course_number=course_number).meeting_set.all()

        if course_number and schedule_id:
            #if(not Schedule.objects.filter(pk=schedule_id).exists()):
            #    return JsonResponse({'result': 'Failure'})
            schedule = Schedule.objects.get(pk=schedule_id)
            for meeting in meetings:
                if (meeting.start_time != ":" or meeting.end_time != ":") and meeting.start_time and meeting.end_time:
                    start = int(meeting.start_time[:2] + meeting.start_time[3:5])
                    end = int(meeting.end_time[:2] + meeting.end_time[3:5])
                    for course in schedule.classes.all():
                        for m in course.meeting_set.all():
                            if time_conflict(meeting.days, start, end, m.days, m.start_time, m.end_time):
                                return JsonResponse({'result': 'Time Conflict'})
            schedule.classes.add(Course.objects.get(course_number=course_number))
            return JsonResponse({'result': 'Success'})
        return JsonResponse({'result': 'Failure'})
    except Exception as e:
        print(e)
        traceback.print_exc()
        return JsonResponse({'result': 'Failure'})

def time_conflict(days0, start0, end0, days1, start1, end1):
    if not (start1 and end1):
        return False

    for i in range(0, len(days0), 2):
        if (days0[i:i+2] in days1):

            start1 = int(start1[:2] + start1[3:5])
            end1 = int(end1[:2] + end1[3:5])

            # Assume no time range between two days (e.g. 23:00 - 01:00)
            #return end0 <= start1 or end1 <= start0
            return end0 > start1 and end1 > start0
    return False
    
def remove_course_from_schedule(request):
    try:
        data = loads(request.body)
        course_number = data['course_number']
        schedule_id = data['schedule_id']
        schedule = Schedule.objects.get(pk=schedule_id)
        if schedule.classes.filter(course_number=course_number).exists():
            remove_item = Course.objects.get(course_number=course_number)
            schedule.classes.remove(remove_item)
            return JsonResponse({'result': 'Success'})
        return JsonResponse({'result': 'Failure'})
    except Exception as e:
        print(e)
        return JsonResponse({'result': 'Failure'})

#filter by username when that is added to the User model.
def remove_course_from_cart(request):
    try:
        data = json.loads(request.body)
        prefix = data["prefix"]
        number = data["number"]
        if Course.objects.filter(subject=prefix, course_number=number).exists():
            remove_item = Course.objects.get(subject=prefix, course_number=number)
            request.user.cart.remove(remove_item)
            return JsonResponse({'result': 'Success'})
        return JsonResponse({'result': 'Failure'})
    except:
        return JsonResponse({'result': 'Failure'})

def get_all_schedules(request: HttpRequest) -> JsonResponse:
    schedules = get_schedules(request.user)
    schedule_data = {
        "schedules": schedules
    }
    return JsonResponse(schedule_data)
