from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    friends = models.ManyToManyField("User", blank=True)
    cart = models.ManyToManyField("Course", blank=True)
    profile_pic = models.CharField(max_length=255, default="yhRgWb.md.png")
    major = models.CharField(max_length=100)
    grad_year = models.IntegerField(default=2023)

class SearchTerm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    term = models.CharField(max_length=200)
    date_created = models.DateTimeField('date created', default=timezone.now)

    def save(self, *args, **kwargs):
        # Checks if object has already been created
        if not self.pk:
            self.date_created = timezone.now()
        super(SearchTerm, self).save(*args, **kwargs)

#Note each department is represented by a code

class Prefix(models.Model):
    prefix = models.CharField(max_length=20)
    dep_name = models.CharField(max_length=200)
    school = models.CharField(max_length=200)

    @classmethod
    def create_prefix(cls, prefix: str, dep_name: str, school: str):
        dep = cls(prefix=prefix, dep_name=dep_name, school=school)
        return dep

class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    semester = models.IntegerField()
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=8, default="#000000")
    classes = models.ManyToManyField("Course", blank=True)
    date_created = models.DateTimeField('date created', default=timezone.now)
    is_private = models.IntegerField(default=3)

    def save(self, *args, **kwargs):
        # Checks if object has already been created
        if not self.pk:
            self.date_created = timezone.now()
        super(Schedule, self).save(*args, **kwargs)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    text = models.TextField()
    date_created = models.DateTimeField('date created', default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.date_created = timezone.now()
        super(Comment, self).save(*args, **kwargs)

class Course(models.Model):
    #prefix = models.CharField(max_length=20)
    # Section number
    #number = models.IntegerField()
    subject = models.CharField(max_length=10)
    catalog_number = models.CharField(max_length=5)
    description = models.CharField(max_length=200)
    course_number = models.IntegerField()
    course_section = models.CharField(max_length=10)
    component = models.CharField(max_length=10)
    units = models.CharField(max_length=10)
    enrollment_total = models.IntegerField()
    class_capacity = models.IntegerField()
    instructor = models.CharField(max_length=30)
    topic = models.CharField(max_length=50)

    @classmethod
    def create_course(cls, subject: str, catalog_number: str, description: str, course_number: int, course_section: str,
    component: str, units: str, enrollment_total: int, class_capacity: int,  instructor: str, topic: str, meetings: list):
        course = cls(subject=subject, catalog_number=catalog_number, description=description, course_number=course_number,
        course_section=course_section, component=component, units=units, enrollment_total=enrollment_total,
        class_capacity=class_capacity, instructor=instructor, topic=topic)
        course.save()
        for meeting in meetings:
            Meeting.objects.create(course=course, days=meeting['days'], start_time=meeting['start_time'],
            end_time=meeting['end_time'], facility_description=meeting['facility_description'])
        return course

class Meeting(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    days = models.CharField(max_length=14)
    start_time = models.CharField(max_length=5)
    end_time = models.CharField(max_length=5)
    facility_description = models.CharField(max_length=50)

    @classmethod
    def create_meeting(cls, course: Course, days: str, start_time: str, end_time: str, facility_description: str):
        return cls(course=course, days=days, start_time=start_time, end_time=end_time, facility_description=facility_description)
