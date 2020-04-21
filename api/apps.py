from django.apps import AppConfig

class ApiConfig(AppConfig):
    name = 'api'
    verbose_name = 'api'
    def ready(self):
        from django.db.models.signals import post_save
        from django.utils.translation import ugettext_lazy as _
        from .models import User, Schedule, FriendRequest, Notification, Course, Degree, College, CoursePriority, Preference, Day, Faculty, Building, Section, CourseOffering, Timeslot, Room, FlowchartTerm
        from .signals import save_friend_request, save_schedule, save_user, save_preference, save_courseoffering
        post_save.connect(save_friend_request,sender=FriendRequest)
        post_save.connect(save_schedule,sender=Schedule)
        post_save.connect(save_user,sender=User)
        post_save.connect(save_preference,sender=Preference)
        post_save.connect(save_courseoffering,sender=CourseOffering)
