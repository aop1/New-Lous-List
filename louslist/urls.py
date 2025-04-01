from django.urls import path, include

from . import views
from . import api
from django.conf.urls import handler404

urlpatterns = [
    path('', views.home, name='home'),
    path('notLogged', views.not_logged, name='notLogged'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('search/', views.quick_search, name='quick-search'),
    path('departments/', views.majorPage, name='majorpage'),
    path('departments/<str:dept>/', views.department, name='department'),
    path('results/', views.results, name='results'),
    path('class-search/', views.advS, name='advS'),
    path("schedule-builder/<int:schedule_id>/", views.schedule_viewer, name="schedule-viewer"),
    path('schedule-builder/', views.schedule_builder, name="schedule-builder"),
    path('create-schedule/', views.create_schedule, name="create-schedule"),
    path('edit-schedule/', views.edit_schedule, name="edit-schedule"),
    path("delete-schedule/", views.delete_schedule, name="delete-schedule"),
    path("view-schedule/<int:schedule_id>", views.view_schedule_post, name="view-schedule"),
    path('social/',views.socialpage,name ="socialpage"),
    path('social/user/<str:friendnames>/',views.friendspage,name ="friendpage"),
    path('api/update-account/', api.update_account, name='update-account'),
    path("account-settings/", views.account_settings, name="account-settings"),
    path('api/add-course-to-cart/', api.add_course_to_cart, name='add-to-cart'),
    path('api/add-course-to-schedule/', api.add_course_to_schedule, name='add-to-schedule'),
    path('api/add-schedule/', api.add_schedule, name='add-schedule'),
    path('api/remove-course-from-cart/', api.remove_course_from_cart, name='remove-course'),
    path('api/remove-course-from-schedule/', api.remove_course_from_schedule, name='remove-from-schedule'),
    path('api/get-all-schedules/', api.get_all_schedules, name='get-all-schedules'),
    path('api/post-comment/', api.post_comment, name='post-comment'),
    path('api/delete-comment/', api.delete_comment, name='post-comment'),
    path('api/add-friend/', api.add_friend, name='add-friend'),
    path('api/remove-friend/', api.remove_friend, name='remove-friend'),
    path('account-settings/', views.account_settings, name='account-settings')
]
