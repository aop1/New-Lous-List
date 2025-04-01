import asyncio
import json
import aiohttp
from asgiref.sync import sync_to_async
from django.forms import model_to_dict
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.forms.models import model_to_dict
from django.db.models import Q
from requests import get
from .manage_schedules import (can_view, course_num_to_sections, get_cart, get_schedule_comments,
                               get_schedule_dict, get_schedules)
from .manage_user import (get_courses_in_cart, get_graduation_years, get_profile_imgs,
                          get_profile_img, get_recent_searches_list, get_user_dict, are_friends, is_course_in_cart, update_recent_searches, get_recent_searches)
from .templatetags.meeting_display import am_pm
from .models import Course, Prefix, Schedule, User,Comment

import datetime


def not_logged(request):
    return render(request,'louslist/not_login.html')

def home(request):
    return render(request, 'louslist/home.html')

@login_required
#friend's user page
def friendspage(request, friendnames):
    if not User.objects.filter(username=friendnames).exists():
        return HttpResponseRedirect(reverse('socialpage') + f'?q={friendnames}')
    creator = User.objects.get(username = friendnames)
    allschedule = []
    for schedule in (Schedule.objects.filter(user=creator)):
        if can_view(schedule, request.user, allow_self_view=False):
            allschedule.append(schedule)
    schedule_post_context = {}
    schedule_post_context["creator"] = model_to_dict(creator)
    schedule_post_context["creator_img"] = get_profile_img(creator.id)
    schedule_post_context["user_dict"] = get_user_dict(request.user)
    schedule_post_context["are_friends"] = are_friends(creator, request.user)
    schedule_post_context["all_user"] = request.user.friends.all()
    schedule_post_context["classes"] = allschedule
    
    return render(request,'louslist/friends-dashboard.html',schedule_post_context)

@login_required
def socialpage(request):
    allschedule = []
    alluser = request.user.friends.all()
    comments = Comment.objects.all()
    created_time = datetime.datetime.now() - datetime.timedelta(minutes=1440*7)
    unique_cart_titles = []
    unique_cart = []
    for course in request.user.cart.all():
        new_course = course.subject + " " + course.catalog_number + ": " + course.description
        if new_course not in unique_cart_titles:
            unique_cart_titles.append(new_course)
            unique_cart.append(course)
    for item in request.user.friends.all():
        for schedules in (Schedule.objects.filter(user=item,date_created__gte=created_time)):
            allschedule.append(schedules)

    search = request.GET.get('q')
    if search:
        users = []
        #results = User.objects.filter(Q(username__icontains=search) | Q(first_name__icontains=search) \
        #    | Q(last_name__icontains=search))
        results = User.objects.filter(~Q(pk=request.user.pk), Q(username__icontains=search) | \
            Q(first_name__icontains=search) | Q(last_name__icontains=search))
        for user in results:
            user_dict = model_to_dict(user)
            user_dict["are_friends"] = are_friends(request.user, user)
            user_dict.pop('password')
            user_dict.pop('user_permissions')
            user_dict.pop('groups')
            user_dict.pop('friends')
            user_dict.pop('cart')
            user_dict['last_login'] = user_dict['last_login'].strftime("%m/%d/%Y, %H:%M:%S") \
                if user_dict['last_login'] != None else "00/00/0000, 00:00:00"
            user_dict['date_joined'] = user_dict['date_joined'].strftime("%m/%d/%Y, %H:%M:%S")
            users.append(user_dict)
        if len(users):
            return render(request, 'louslist/user-results.html', {'users': users, "all_user": alluser})
        return render(request, 'louslist/user-results.html',
            {'error_message': f"No user matched '{search}'.", "all_user": alluser})

    return render(request,'louslist/social-home.html',{"all_user":alluser,"all_schedule":allschedule,"all_comments":comments})

def majorPage(request):
    depts = Prefix.objects.values_list('dep_name', flat=True).distinct()
    all_dept = [Prefix.objects.filter(dep_name=x).first() for x in depts]
    all_dept.append(Prefix(dep_name='Computer Science', school='Engineering & Applied Sciences Departments'))
    all_dept.append(Prefix(dep_name='Interdisciplinary Studies', school='Other Schools at the University of Virginia'))
    all_dept.append(Prefix(dep_name='University Seminars', school='Other Schools at the University of Virginia'))
    all_dept.append(Prefix(dep_name='Cross Disciplinary (For All Schools)', school='Other Programs, Seminars, and Institutes'))
    all_dept.append(Prefix(dep_name='University Studies', school='Other Programs, Seminars, and Institutes'))
    return render(request, 'louslist/department-page.html',{"all_dept": all_dept})

def advS(request):
    return render(request, 'louslist/adv-search.html')

@login_required
def dashboard(request: HttpRequest):
    if request.user.is_authenticated:
        recent_searches = get_recent_searches_list(request.user)
        unique_cart_titles = []
        unique_cart = []
        for course in request.user.cart.all():
            new_course = course.subject + " " + course.catalog_number + ": " + course.description
            if new_course not in unique_cart_titles:
                unique_cart_titles.append(new_course)
                unique_cart.append(course)
        schedules = get_schedules(request.user)
        dashboard_context = {
            "cart": get_cart(request.user),
            "schedules": schedules,
            "unique_cart": unique_cart,
            "recent_searches": recent_searches,
        }
        return render(request, 'louslist/dashboard.html', dashboard_context)

@login_required
def account_settings(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        settings_context = {
            "profile_img": get_profile_img(request.user.id),
            "profile_imgs": get_profile_imgs(),
            "grad_years": get_graduation_years(),
            "user_dict": get_user_dict(request.user)
        }
        return render(request, 'louslist/account-settings.html', settings_context)



async def quick_search(request):
    search = request.GET.get('q')
    if search:
        numbers = []
        courses = []
        courses_by_number = {}
        subject_list = get('http://luthers-list.herokuapp.com/api/deptlist/?format=json').json()
        urls = [f"http://luthers-list.herokuapp.com/api/dept/{x['subject']}/?format=json" for x in subject_list if search.upper() == x['subject']]
        async for prefix in Prefix.objects.filter(dep_name__iexact=search).values('prefix').distinct():
            urls.append(f"http://luthers-list.herokuapp.com/api/dept/{prefix['prefix']}/?format=json")
            
        if len(urls) == 0:
            resp = get(f'https://thecourseforum.com/search/?q={search}')
            indexes = [i for i in findall('/course/', resp.text)]
            for i in indexes:
                start = i + 8
                i = resp.text[start:start+20].find('/')
                mnemonic = resp.text[start:start+i]
                urls.append(f"http://luthers-list.herokuapp.com/api/dept/{mnemonic}/?format=json")
                start += i + 1
                i = resp.text[start:start+20].find('/')
                number = resp.text[start:start+i]
                numbers.append(number)
            responses = await get_responses(urls)

            for i in range(len(responses)):
                for course in responses[i]:
                    if numbers[i] == course['catalog_number']:
                        courses.append(course)
        else:
            responses = await get_responses(urls)
            for resp in responses:
                for course in resp:
                    courses.append(course)
        add_courses_to_context(courses, courses_by_number)
        is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
        context = {'courses_by_number' : courses_by_number, 'title': 'Search',
        "is_authenticated": is_authenticated}
        if is_authenticated:
            await update_recent_searches(user=request.user, search_term=search)
            context["courses_in_cart"] = await get_courses_in_cart(request.user)
        if len(courses_by_number) == 0:
            context['error_message'] = f"No courses matched '{search}'."
        return render(request, 'louslist/search-results.html', context)

    return render(request, 'louslist/home.html')

async def results(request):
    courses_by_number = {}
    is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
    context = {'courses_by_number' : courses_by_number, 'title': 'Results',
    "is_authenticated": is_authenticated}
    if is_authenticated:
        context["courses_in_cart"] = await get_courses_in_cart(request.user)
    if request.method != 'POST':
        return render(request, 'louslist/search-results.html', context)
    
    mnemonic = request.POST.get('mnemonic', '').upper()
    mo = request.POST.get('mo', '')
    tu = request.POST.get('tu', '')
    we = request.POST.get('we', '')
    th = request.POST.get('th', '')
    fr = request.POST.get('fr', '')
    sa = request.POST.get('sa', '')
    su = request.POST.get('su', '')
    days = f'{mo}{tu}{we}{th}{fr}{sa}{su}'
    start = request.POST.get('start_time', '')
    end = request.POST.get('end_time', '')
    name = request.POST.get('name', '').lower()
    number = request.POST.get('number', '')
    instructor = request.POST.get('instructor', '').lower()
    min = request.POST.get('min', '')
    dept = request.POST.get('dept', '')

    urls = []
    if dept and not mnemonic:
        async for prefix in Prefix.objects.filter(dep_name__icontains=dept).values('prefix').distinct():
            urls.append(f"http://luthers-list.herokuapp.com/api/dept/{prefix['prefix']}/?format=json")
    else:
        subject_list = get('http://luthers-list.herokuapp.com/api/deptlist/?format=json').json()
        urls = [f"http://luthers-list.herokuapp.com/api/dept/{x['subject']}/?format=json" for x in subject_list if mnemonic in x['subject']]
        if dept:
            urls = [f"http://luthers-list.herokuapp.com/api/dept/{x['prefix']}/?format=json" async for x in Prefix.objects.filter(dep_name__icontains=dept).values('prefix').distinct() if mnemonic in x['prefix']]
    responses = await get_responses(urls)

    courses = []
    for resp in responses:
        for course in resp:
            courses.append(course)
    if name:
        courses = [x for x in courses if name in x['description'].lower()]
    if number:
        courses = [x for x in courses if number in x['catalog_number']]
    if instructor:
        courses = [x for x in courses if instructor in x['instructor']['name'].lower()]
    if min:
        min = int(min)
        courses = [x for x in courses if min <= x['enrollment_available']]
    if days:
        courses = [x for x in courses if len(x['meetings']) > 0 and days in x['meetings'][0]['days']]
    if start and end:
        start_int = int(start[:2] + start[3:5])
        end_int = int(end[:2] + end[3:5])
        courses = [x for x in courses if len(x['meetings']) > 0 and time_in_range(start_int, end_int, x['meetings'][0]['start_time'], x['meetings'][0]['end_time'])]

    add_courses_to_context(courses, courses_by_number)
    if len(courses_by_number) == 0:
        filters_values = [name, mnemonic, number, dept, instructor, days, am_pm(start), am_pm(end), min]
        filters_names = ['Class Title', 'Class Mnemonic', 'Class Number', 'Department', \
            'Instructor', 'Meeting Days', 'Start Time', 'End Time', 'Minimum Seats Available']
        filters = []
        for i in range(len(filters_values)):
            if filters_values[i]:
                filters.append(f"{filters_names[i]}: {filters_values[i]}")
        context['error_message'] = f"No courses matched the following filters:"
        context['filters'] = filters
    return render(request, 'louslist/search-results.html', context)

async def department(request, dept):
    urls = [f"http://luthers-list.herokuapp.com/api/dept/{x['prefix']}/?format=json" async for x in Prefix.objects.filter(dep_name=dept).values('prefix').distinct()]
    responses = await get_responses(urls)
    courses = []
    for resp in responses:
        for course in resp:
            courses.append(course)
    courses_by_number = {}
    is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
    add_courses_to_context(courses, courses_by_number)
    context = {'courses_by_number' : courses_by_number, 'title': dept,
    "is_authenticated": is_authenticated}
    if is_authenticated:
        context["courses_in_cart"] = await get_courses_in_cart(request.user)
    if len(courses_by_number) == 0:
            context['error_message'] = f"No courses matched '{dept}'."
    return render(request, 'louslist/search-results.html', context)

def add_courses_to_context(courses, courses_by_number):
    for course in courses:
        if not f"{course['subject']} {course['catalog_number']}" in courses_by_number:
            courses_by_number[f"{course['subject']} {course['catalog_number']}"] = []
        if len(course['meetings']) > 0:
            course['start_time'] = course['meetings'][0]['start_time'][:2] + ':' + course['meetings'][0]['start_time'][3:5]
            course['end_time'] = course['meetings'][0]['end_time'][:2] + ':' + course['meetings'][0]['end_time'][3:5]
            course['days'] = course['meetings'][0]['days']
            course['facility_description'] = course['meetings'][0]['facility_description']
            del(course['meetings'][0])
        for i in range(len(course['meetings'])):
            course['meetings'][i]['start_time'] = course['meetings'][i]['start_time'][:2] + ':' + course['meetings'][i]['start_time'][3:5]
            course['meetings'][i]['end_time'] = course['meetings'][i]['end_time'][:2] + ':' + course['meetings'][i]['end_time'][3:5]
        course['color'] =  color(course['enrollment_total'], course['class_capacity'])
        courses_by_number[f"{course['subject']} {course['catalog_number']}"].append(course)

async def get_subject(session, url):
    async with session.get(url) as resp:
        return await resp.json()

async def get_responses(urls):
    tasks = []
    async with aiohttp.ClientSession(trust_env=True) as sess:
        for u in urls:
            task = asyncio.ensure_future(get_subject(sess, u))
            tasks.append(task)
        return await asyncio.gather(*tasks)

def time_in_range(start, end, class_start, class_end):
    if not (class_start and class_end):
        return False

    class_start = int(class_start[:2] + class_start[3:5])
    class_end = int(class_end[:2] + class_end[3:5])

    if start <= end:
        return start <= class_start and class_end <= end
    else:
        return (start <= class_start or class_start <= end) and (start <= class_end or class_end <= end)
    
BLUE = 20
def color(x, y):
    try:
        factor = x/y
        if (x-y >= 0):
            return '%02x%02x%02x' % (255, 0, BLUE)
        elif (factor > 0.5):
            return '%02x%02x%02x' % (255, 255-int((factor-0.5)*2*100), BLUE)
        else:
            return '%02x%02x%02x' % (int(factor*2*255), 255, BLUE)
    except ZeroDivisionError:
        return '%02x%02x%02x' % (255, 0, BLUE)

def findall(p, s):
    '''Yields all the positions of
    the pattern p in the string s.'''
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)

@login_required
def schedule_builder(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        cart_dict = get_cart(request.user)
        sections = course_num_to_sections(cart_dict)
        schedule_dict = get_schedules(request.user)
        schedule_builder_context = {
            "cart": cart_dict,
            "schedules": schedule_dict,
            "sections": sections,
            "cart_json": json.dumps(cart_dict),
            "schedules_json": json.dumps(schedule_dict)
        }
        return render(request, "louslist/schedule-builder.html", context=schedule_builder_context)
    
@login_required
def schedule_viewer(request: HttpRequest, schedule_id: int):
    if request.user.is_authenticated:
        cart = get_cart(request.user)
        schedules = get_schedules(request.user)
        for i, schedule in enumerate(schedules):
            if schedule["id"] == schedule_id:
                schedule = schedules.pop(i)
                schedules.insert(0, schedule)
                break
        schedule_builder_context = {
            "cart": cart,
            "schedules": schedules,
            "cart_json": json.dumps(cart),
            "schedules_json": json.dumps(schedules)
        }
    return render(request, "louslist/schedule-builder.html", context=schedule_builder_context)
    
def create_schedule(request: HttpRequest) -> HttpResponseRedirect:
    if request.method == "POST":
        schedule_name = request.POST.get("schedule_name")
        semester = int(request.POST.get("semester"))
        visiblity = int(request.POST.get("visibility"))
        color = request.POST.get("color")
        schedule = Schedule(user=request.user, name=schedule_name, semester=semester, is_private=visiblity, color=color)
        schedule.save()
        return HttpResponseRedirect(reverse("schedule-builder"))

def edit_schedule(request: HttpRequest) -> HttpResponseRedirect:
    if request.method == "POST":
        schedule_id = int(request.POST.get("schedule_id"))
        schedule_name = request.POST.get("schedule_name")
        visibility = int(request.POST.get("visibility"))
        color = request.POST.get("color")

        schedule = Schedule.objects.get(pk=schedule_id)
        try:
            schedule.name = schedule_name
            schedule.is_private = visibility
            schedule.color = color
            schedule.save()
        except Exception as e:
            print(e)
            return HttpResponseRedirect(reverse("schedule-builder"))

        return HttpResponseRedirect(reverse("schedule-builder") + str(schedule_id))

def delete_schedule(request: HttpRequest) -> HttpResponseRedirect:
    if request.method == "POST":
        schedule_id = request.POST.get("schedule_id")
        schedule = Schedule.objects.filter(id=schedule_id)
        schedule.delete()
        return HttpResponseRedirect(reverse("schedule-builder"))

@login_required
def view_schedule_post(request: HttpRequest, schedule_id: int) -> HttpResponseRedirect:
    schedule = Schedule.objects.get(pk=schedule_id)
    creator = User.objects.get(pk=schedule.user.id)
    schedule_post_context = {"user": request.user}
    alluser = request.user.friends.all()
    search = request.GET.get('q')
    if search:
        users = []
        #results = User.objects.filter(Q(username__icontains=search) | Q(first_name__icontains=search) \
        #    | Q(last_name__icontains=search))
        results = User.objects.filter(~Q(pk=request.user.pk), Q(username__icontains=search) | \
            Q(first_name__icontains=search) | Q(last_name__icontains=search))
        for user in results:
            user_dict = model_to_dict(user)
            user_dict.pop('password')
            user_dict.pop('user_permissions')
            user_dict.pop('groups')
            user_dict.pop('friends')
            user_dict.pop('cart')
            user_dict['last_login'] = user_dict['last_login'].strftime("%m/%d/%Y, %H:%M:%S") \
                if user_dict['last_login'] != None else "00/00/0000, 00:00:00"
            user_dict['date_joined'] = user_dict['date_joined'].strftime("%m/%d/%Y, %H:%M:%S")
            users.append(user_dict)
        if len(users):
            return render(request, 'louslist/user-results.html', {'users': users})
        return render(request, 'louslist/user-results.html',
            {'error_message': f"No user matched '{search}'."})

    if can_view(schedule, request.user):
        schedule_post_context["schedule"] = get_schedule_dict(schedule)
        schedule_post_context["comments"] = get_schedule_comments(schedule_id)
        schedule_post_context["creator"] = model_to_dict(creator)
        schedule_post_context["creator_img"] = get_profile_img(creator.id)
        schedule_post_context["user_dict"] = get_user_dict(request.user)
        schedule_post_context["are_friends"] = are_friends(creator, request.user)
        schedule_post_context["all_user"] = request.user.friends.all()
        return render(request, "louslist/calendar-post.html", schedule_post_context)
    
    if schedule.is_private == 2:
        return render(request, "louslist/calendar-post-non-friends.html")


    return render(request, "louslist/calendar-post-private.html",{"all_user":alluser})