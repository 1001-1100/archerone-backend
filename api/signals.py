from .models import User, Schedule, FriendRequest, Notification, Course, Degree, College, CoursePriority, Preference, Day, Faculty, Building, Section, CourseOffering, Timeslot, Room, FlowchartTerm

def save_friend_request(sender, instance, **kwargs):
    if(instance.accepted):
        Notification(content=instance.from_user.first_name+' accepted your friend request!', seen=False, to_user=instance.to_user).save()

def save_schedule(sender, instance, **kwargs):
    for u in instance.user.friends.all():
        Notification(content=instance.user.first_name+' saved a new schedule named \''+instance.title+'\'!', seen=False, to_user=u).save()