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

# def save_preference(sender, instance, **kwargs):
#     if(instance.accepted):
#         Notification(content=instance.to_user.first_name+' accepted your friend request!', seen=False, to_user=instance.from_user).save()