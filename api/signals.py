from .models import User, Schedule, FriendRequest, Notification, Course, Degree, College, CoursePriority, Preference, Day, Faculty, Building, Section, CourseOffering, Timeslot, Room, FlowchartTerm

def save_friend_request(sender, instance, **kwargs):
    if(instance.accepted and not(instance.notified)):
        Notification(category='Friend', content=instance.to_user.first_name+' accepted your friend request!', seen=False, to_user=instance.from_user).save()
        instance.notified = True
        instance.save()


def save_schedule(sender, instance, created, **kwargs):
    if(created):
        for u in instance.user.friends.all().exclude(id=instance.user.id):
            Notification(category='Schedule', content=instance.user.first_name+' saved a new schedule named \''+instance.title+'\'!', seen=False, to_user=u).save()
    else:
        for u in instance.user.friends.all().exclude(id=instance.user.id):
            Notification(category='Schedule', content=instance.user.first_name+' modified the schedule named \''+instance.title+'\'!', seen=False, to_user=u).save()

def save_user(sender, instance, created, **kwargs):
    if(created):
        Preference(user=instance, earliest_class_time='07:30:00', latest_class_time='21:00:00', break_length=15, min_courses=0, max_courses=10).save()

def save_preference(sender, instance, **kwargs):
    if(instance.earliest_class_time != None):
        for u in instance.user.friends.all().exclude(id=instance.user.id):
            Notification(category='Friend', content=instance.user.first_name+' modified their preferences!', seen=False, to_user=u).save()

def save_courseoffering(sender, instance, **kwargs):
    def checkCourseExists(schedule, offering):
        for s in schedule:
            if(s == offering):
                return True
        return False
    if(instance.max_enrolled == instance.current_enrolled):
        for s in Schedule.objects.all():
            if(checkCourseExists(s.courseOfferings.all(), instance)):
                Notification(category='Schedule', content=instance.course.course_code+' in schedule \''+s.title+'\' is now full!', seen=False, to_user=s.user).save()