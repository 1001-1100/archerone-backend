from django.db import models

from django.core.mail import send_mail
from django.core.validators import int_list_validator, RegexValidator
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager

import datetime

class College(models.Model):
    college_code = models.CharField(max_length=12, unique=True)
    section_code = models.CharField(max_length=12, unique=True, null=True, blank=True)
    college_name = models.CharField(max_length=120, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('college')
        verbose_name_plural = _('colleges')

class Degree(models.Model):
    degree_code = models.CharField(max_length=8, unique=True)
    degree_name = models.CharField(max_length=120, unique=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('degree')
        verbose_name_plural = _('degrees')

class Course(models.Model):
    course_code = models.CharField(max_length=8, unique=True)
    course_name = models.CharField(max_length=120, blank=True)
    course_desc = models.TextField(blank=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True)
    units = models.IntegerField(blank=True, null=True, default=3)
    timestamp = models.DateTimeField(auto_now_add=True)
    # flowchart information
    # flowchart_terms = models.ManyToManyField(FlowchartTerm)
    prerequisite_to = models.ManyToManyField('self', related_name='prerequisite', symmetrical=False, blank=True)
    soft_prerequisite_to = models.ManyToManyField('self', related_name='softprereq', symmetrical=False, blank=True)
    co_requisite = models.ManyToManyField('self', related_name='coreq', symmetrical=True, blank=True)

    class Meta:
        verbose_name = _('course')
        verbose_name_plural = _('courses')

class FlowchartTerm(models.Model):
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    batch = models.CharField(max_length=6)
    courses = models.ManyToManyField(Course)
    tracks = models.CharField(validators=[int_list_validator], max_length=100, null=True, blank=True)
    year = models.IntegerField()
    term = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('flowchart term')
        verbose_name_plural = _('flowchart terms')

# class Flowchart(models.Model):
#     degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
#     year = models.CharField(max_length=3)
#     terms = models.ManyToManyField(FlowchartTerm)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = _('flowchart')
#         verbose_name_plural = _('flowcharts')

class Faculty(models.Model):
    full_name = models.CharField(max_length=100, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('faculty member')
        verbose_name_plural = _('faculty members')

class Section(models.Model):
    section_code = models.CharField(max_length=6, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('section')
        verbose_name_plural = _('sections')

class Building(models.Model):
    bldg_code = models.CharField(max_length=50, unique=True)
    bldg_name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('building')
        verbose_name_plural = _('buildings')

class Room(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    room_name = models.CharField(max_length=50, unique=True)
    room_type = models.CharField(max_length=50, blank=True)
    room_capacity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('room')
        verbose_name_plural = _('rooms')

class Day(models.Model):
    day_code = models.CharField(max_length=3, unique=True)
    day_name = models.CharField(max_length=10, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('day')
        verbose_name_plural = _('days')

class Timeslot(models.Model): 
    begin_time = models.TimeField()
    end_time = models.TimeField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('timeslot')
        verbose_name_plural = _('timeslots')

class CourseOffering(models.Model):
    classnumber = models.IntegerField()
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)
    day = models.ForeignKey(Day, on_delete=models.CASCADE, null=True)
    timeslot = models.ForeignKey(Timeslot, on_delete=models.CASCADE, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    # term = models.IntegerField()
    # start_AY = models.IntegerField()
    # end_AY = models.IntegerField()
    current_enrolled = models.IntegerField(blank=True, null=True)
    max_enrolled = models.IntegerField(blank=True, null=True)
    status = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('course offering')
        verbose_name_plural = _('course offerings')

class User(AbstractBaseUser):
    # username = models.CharField(max_length=9) 
    username = None
    email = models.EmailField(_('email address'), unique=True)
    id_num = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    # schedules = models.ManyToManyField(Schedule)
    is_active = models.BooleanField(default=True)
    objects = UserManager()
    friends = models.ManyToManyField('self', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'college', 'degree']

    class Meta:
        # ordering = ['id_num','last_name']
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):              
        return self.email

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    notified = models.BooleanField(default=False)

class Notification(models.Model):
    content = models.CharField(max_length=500)
    category = models.CharField(max_length=100,blank=True,null=True)
    date = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE)

class Schedule(models.Model):
    title = models.CharField(max_length=50)
    courseOfferings = models.ManyToManyField(CourseOffering)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')

class CoursePriority(models.Model):
    courses = models.ForeignKey(Course,on_delete=models.CASCADE)
    priority = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('course priority')
        verbose_name_plural = _('course priorities')

class Preference(models.Model):
    earliest_class_time = models.TimeField(_('earliest class time'), null=True)
    latest_class_time = models.TimeField(_('latest class time'), null=True)
    preferred_days = models.ForeignKey(Day, on_delete=models.CASCADE, null=True)
    break_length = models.IntegerField(_('break length'), null=True)
    min_courses = models.IntegerField(_('min courses per day'), null=True)
    max_courses = models.IntegerField(_('max courses per day'), null=True)
    preferred_faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True) 
    preferred_buildings = models.ForeignKey(Building, on_delete=models.CASCADE, null=True)
    preferred_sections = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)
    # course_priority = models.ForeignKey(CoursePriority, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('preference')
        verbose_name_plural = _('preferences')



