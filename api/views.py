from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets          
from .serializers import CustomRegisterSerializer, FriendRequestSerializer, NotificationSerializer, ScheduleSerializer, TimeslotSerializer, CourseOfferingSerializer, PreferenceSerializer, UserSerializer, CourseSerializer, DegreeSerializer, CollegeSerializer, CoursePrioritySerializer, DaySerializer, FacultySerializer, BuildingSerializer, SectionSerializer, FlowchartTermSerializer
from .models import User, Schedule, FriendRequest, Notification, Course, Degree, College, CoursePriority, Preference, Day, Faculty, Building, Section, CourseOffering, Timeslot, Room, FlowchartTerm
from .satsolver import solve, solveEdit
from rest_framework.response import Response
from rest_framework.views import APIView
import random
import requests
from bs4 import BeautifulSoup
import _thread

class UserViewSet(viewsets.ModelViewSet):
  serializer_class = UserSerializer
  queryset = User.objects.all()              

class CourseViewSet(viewsets.ModelViewSet):       
  serializer_class = CourseSerializer 
  queryset = Course.objects.all()              

class DegreeViewSet(viewsets.ModelViewSet):       
  serializer_class = DegreeSerializer 
  queryset = Degree.objects.all()              

class FlowchartTermViewSet(viewsets.ModelViewSet):       
  serializer_class = FlowchartTermSerializer 
  queryset = FlowchartTerm.objects.all()              

class CoursePriorityViewSet(viewsets.ModelViewSet):       
  serializer_class = CoursePrioritySerializer 
  queryset = CoursePriority.objects.all()              

class CollegeViewSet(viewsets.ModelViewSet):       
  serializer_class = CollegeSerializer 
  queryset = College.objects.all()              

class FacultyViewSet(viewsets.ModelViewSet):       
  serializer_class = FacultySerializer 
  queryset = Faculty.objects.all()              

class DayViewSet(viewsets.ModelViewSet):       
  serializer_class = DaySerializer
  queryset = Day.objects.all()              

class TimeslotViewSet(viewsets.ModelViewSet):       
  serializer_class = TimeslotSerializer 
  queryset = Timeslot.objects.all()              

class BuildingViewSet(viewsets.ModelViewSet):       
  serializer_class = BuildingSerializer 
  queryset = Building.objects.all()              

class SectionViewSet(viewsets.ModelViewSet):       
  serializer_class = SectionSerializer 
  queryset = Section.objects.all()              

class FriendRequestViewSet(viewsets.ModelViewSet):       
  serializer_class = FriendRequestSerializer 
  queryset = FriendRequest.objects.all()              

class NotificationViewSet(viewsets.ModelViewSet):       
  serializer_class = NotificationSerializer 
  queryset = Notification.objects.all()              

class PreferenceViewSet(viewsets.ModelViewSet):       
  serializer_class = PreferenceSerializer 
  queryset = Preference.objects.all()              

class CourseOfferingViewSet(viewsets.ModelViewSet):       
  serializer_class = CourseOfferingSerializer 
  queryset = CourseOffering.objects.all()              

class ScheduleViewSet(viewsets.ModelViewSet):       
  serializer_class = ScheduleSerializer 
  queryset = Schedule.objects.all()              

class SavedScheduleList(APIView):
    def get(self, request, pk, format=None):
        schedules = Schedule.objects.filter(user=pk).order_by('-timestamp')
        serializer = ScheduleSerializer(schedules, many=True)
        for d in serializer.data:
          courseOfferings = []
          for o in d['courseOfferings']:
            offering = CourseOffering.objects.get(id=o) 
            offeringSerializer = CourseOfferingSerializer(offering)
            d2 = offeringSerializer.data
            print(d2)
            if(d2['faculty'] != None):
              d2['faculty'] = Faculty.objects.get(id=d2['faculty']).full_name
            d2['course_id'] = d2['course']
            d2['course'] = Course.objects.get(id=d2['course']).course_code
            d2['section'] = Section.objects.get(id=d2['section']).section_code  
            d2['day'] = Day.objects.get(id=d2['day']).day_code  
            d2['timeslot_begin'] = Timeslot.objects.get(id=d2['timeslot']).begin_time  
            d2['timeslot_end'] = Timeslot.objects.get(id=d2['timeslot']).end_time
            if(d2['room'] != None):
              d2['room'] = Room.objects.get(id=d2['room']).room_name
            courseOfferings.append(d2)
          d['courseOfferings'] = courseOfferings
        return Response(serializer.data)

class PreferenceList(APIView):
  def get(self, request, pk, format=None):
      preferences = Preference.objects.filter(user=pk)
      serializer = PreferenceSerializer(preferences, many=True)
      for d in serializer.data:
        if(d['preferred_faculty'] != None):
          faculty = Faculty.objects.get(id=d['preferred_faculty'])
          d['preferred_faculty'] = {'id':faculty.id, 'full_name':faculty.full_name}
        if(d['preferred_sections'] != None):
          section = Section.objects.get(id=d['preferred_sections'])
          d['preferred_sections'] = {'id':section.id, 'section_code':section.section_code}
      return Response(serializer.data)

  def delete(self, request, pk, format=None):
      preferences = Preference.objects.filter(user=pk).delete()
      return Response(None)

class CoursePriorityList(APIView):
  def get(self, request, pk, format=None):
      coursePriority = CoursePriority.objects.filter(user=pk)
      serializer = CoursePrioritySerializer(coursePriority, many=True)
      return Response(serializer.data)

  def delete(self, request, pk, format=None):
      coursePriority = CoursePriority.objects.filter(id=pk).delete()
      return Response(None)

class NonFriendList(APIView):
  def get(self, request, pk, format=None):
      user = User.objects.get(id=pk)
      nonFriends = User.objects.all().exclude(id=pk)
      for f in user.friends.all():
        nonFriends = nonFriends.exclude(id=f.id)
      serializer = UserSerializer(nonFriends, many=True)
      return Response(serializer.data)

class FriendRequestList(APIView):
  def get(self, request, pk, format=None):
      friendRequests = FriendRequest.objects.filter(to_user=pk).order_by('-date')
      serializer = FriendRequestSerializer(friendRequests, many=True)
      for d in serializer.data:
        d['from_user_fname'] = User.objects.get(id=d['from_user']).first_name
        d['from_user_lname'] = User.objects.get(id=d['from_user']).last_name
      return Response(serializer.data)

class FriendList(APIView):
  def get(self, request, pk, format=None):
      user = User.objects.get(id=pk)
      friends = User.objects.none()
      for f in user.friends.all():
        friends = friends | User.objects.filter(id=f.id)
      friends = friends.exclude(id=pk).order_by('first_name', 'last_name')
      serializer = UserSerializer(friends, many=True)
      for d in serializer.data:
        d['college'] = College.objects.get(id=d['college']).college_name
        d['degree'] = Degree.objects.get(id=d['degree']).degree_name
      return Response(serializer.data)

class SentRequestList(APIView):
  def get(self, request, pk, format=None):
      friendRequests = FriendRequest.objects.filter(from_user=pk).exclude(accepted=True)
      serializer = FriendRequestSerializer(friendRequests, many=True)
      return Response(serializer.data)

class SearchCourse(APIView):
  def get(self, request, term, format=None):
      courses = Course.objects.filter(course_code__icontains=term).order_by('course_code')
      serializer = CourseSerializer(courses , many=True)
      return Response(serializer.data)

class NotificationList(APIView):
  def get(self, request, pk, format=None):
      notifications = Notification.objects.filter(to_user=pk).order_by('-date')
      serializer = NotificationSerializer(notifications, many=True)
      return Response(serializer.data)

class CourseOfferingsList(APIView):
  def post(self, request, format=None):
      courseData = []
      for c in request.data['courses']:
        offerings = CourseOffering.objects.filter(course=c)
        serializer = CourseOfferingSerializer(offerings, many=True)
        for d in serializer.data:
          if(d['faculty'] != None):
            d['faculty'] = Faculty.objects.get(id=d['faculty']).full_name
          d['classnumber'] = d['classnumber']
          d['course_id'] = d['course']
          d['course'] = Course.objects.get(id=d['course']).course_code
          d['section'] = Section.objects.get(id=d['section']).section_code  
          d['day'] = Day.objects.get(id=d['day']).day_code  
          d['timeslot_begin'] = Timeslot.objects.get(id=d['timeslot']).begin_time  
          d['timeslot_end'] = Timeslot.objects.get(id=d['timeslot']).end_time
          if(d['room'] != None):
            d['room'] = Room.objects.get(id=d['room']).room_name
        courseData.append(serializer.data)
      return Response(courseData)

class EditSchedule(APIView):
  def post(self, request, format=None):
    courses = []
    classnumbers = []
    for c in request.data['courses']:
      courses.append(c)
    for c in request.data['classnumbers']:
      classnumbers.append(c)
    user = request.data['user_id']
    sched_id = request.data['sched_id']

    schedule = solveEdit(courses, classnumbers)

    old_sched = Schedule.objects.get(id=sched_id)
    old_sched.courseOfferings.clear()
    for o in schedule:
      old_sched.courseOfferings.add(o)
    old_sched.save()

    serializer = CourseOfferingSerializer(schedule, many=True)
    for d in serializer.data:
      if(d['faculty'] != None):
        d['faculty'] = Faculty.objects.get(id=d['faculty']).full_name
      d['course_id'] = d['course']
      d['course'] = Course.objects.get(id=d['course']).course_code
      d['section'] = Section.objects.get(id=d['section']).section_code  
      d['day'] = Day.objects.get(id=d['day']).day_code  
      d['timeslot_begin'] = Timeslot.objects.get(id=d['timeslot']).begin_time  
      d['timeslot_end'] = Timeslot.objects.get(id=d['timeslot']).end_time
      if(d['room'] != None):
        d['room'] = Room.objects.get(id=d['room']).room_name
    return Response(serializer.data)

class SchedulesList(APIView):
  def post(self, request, format=None):
    highCourses = []
    lowCourses = []
    for c in request.data['highCourses']:
      highCourses.append(c['course_id'])
    for c in request.data['lowCourses']:
      lowCourses.append(c['course_id'])
    user = request.data['user_id']
    preferences = Preference.objects.filter(user=user)
    filterFull = request.data['filterFull']
    courseOfferings = request.data['courseOfferings']

    serializedSchedules = []
    schedules = solve(highCourses, lowCourses, preferences, filterFull, courseOfferings)
    for s in schedules:
      serializedSchedule = {}
      serializer = CourseOfferingSerializer(s['offerings'], many=True)
      for d in serializer.data:
        if(d['faculty'] != None):
          d['faculty'] = Faculty.objects.get(id=d['faculty']).full_name
        d['course_id'] = d['course']
        d['course'] = Course.objects.get(id=d['course']).course_code
        d['section'] = Section.objects.get(id=d['section']).section_code  
        d['day'] = Day.objects.get(id=d['day']).day_code  
        d['timeslot_begin'] = Timeslot.objects.get(id=d['timeslot']).begin_time  
        d['timeslot_end'] = Timeslot.objects.get(id=d['timeslot']).end_time
        if(d['room'] != None):
          d['room'] = Room.objects.get(id=d['room']).room_name
      serializedSchedule['offerings'] = serializer.data
      serializedSchedule['information'] = s['information']
      serializedSchedule['preferences'] = s['preferences']
      serializedSchedules.append(serializedSchedule)
    return Response(serializedSchedules)

class FlowchartTermsList(APIView):
  def get(self, request, pk, pk2, format=None):
      flowchartTerms = FlowchartTerm.objects.filter(degree=pk, batch=pk2)
      serializer = FlowchartTermSerializer(flowchartTerms, many=True)
      for d in serializer.data:
        courses = []
        for o in d['courses']:
          course = Course.objects.get(id=o)
          courseSerializer = CourseSerializer(course)
          d2 = courseSerializer.data
          print(d2)
          d2['college'] = College.objects.get(id=d2['college']).college_code
          courses.append(d2)
        d['courses'] = courses
      return Response(serializer.data)

class RetrieveCourse(APIView):
  def get(self, request, term, format=None):
      retrieveCourse(term)
      return HttpResponse(term)

def retrieveCourse(c):
  course = Course.objects.filter(course_code=c.strip())
  if(len(course) > 0):
    courses = []
    dataTimes = {}
    dataFaculty = {}
    if(c.strip() != ''):
        URL = "http://enroll.dlsu.edu.ph/dlsu/view_actual_count"
        PARAMS = {'p_course_code':c}
        print("Retrieving data for "+c+"...")
        
        try:
            r = requests.post(url = URL, params = PARAMS)
        except:
            return "Request encountered an error."

        if(r.status_code == 200):
            parsed = BeautifulSoup(r.text, "html5lib").center
            rows = parsed.find_all("tr")
            prevCourse = None
            if(len(rows) > 1):
                for row in rows[1:]:
                    rowData = row.get_text().strip().split("\n")
                    if(len(rowData) == 1):
                        faculty = rowData[0].strip()
                        dataFaculty[prevCourse] = faculty
                    elif(len(rowData) == 2):
                        times = rowData[1].strip().split(' ')
                        begintime = times[0][0:2] + ':' + times[0][2:4]
                        endtime = times[2][0:2] + ':' + times[2][2:4]
                        for day in rowData[0].strip():
                            if prevCourse not in dataTimes:
                                dataTimes[prevCourse] = []
                            time = {
                                'day':day,
                                'begintime':begintime,
                                'endtime':endtime,
                                'room':''
                            }
                            dataTimes[prevCourse].append(time)
                    elif(len(rowData) == 3):
                        times = rowData[1].strip().split(' ')
                        begintime = times[0][0:2] + ':' + times[0][2:4]
                        endtime = times[2][0:2] + ':' + times[2][2:4]
                        for day in rowData[0].strip():
                            if prevCourse not in dataTimes:
                                dataTimes[prevCourse] = []
                            time = {
                                'day':day,
                                'begintime':begintime,
                                'endtime':endtime,
                                'room':rowData[2].strip()
                            }
                            dataTimes[prevCourse].append(time)
                    elif(len(rowData) >= 8):
                        coursenumber = int(rowData[0].strip())
                        times = rowData[4].strip().split(' ')
                        begintime = times[0][0:2] + ':' + times[0][2:4]
                        endtime = times[2][0:2] + ':' + times[2][2:4]
                        course = { 
                            'coursenumber':coursenumber,
                            'coursecode':rowData[1].strip(),
                            'section':rowData[2].strip(),
                            'enrollcap':rowData[6].strip(),
                            'enrolled':rowData[7].strip(),
                        }
                        prevCourse = coursenumber
                        courses.append(course)
                        for day in rowData[3].strip():
                            if coursenumber not in dataTimes:
                                dataTimes[coursenumber] = []
                            time = {
                                'day':day,
                                'begintime':begintime,
                                'endtime':endtime,
                                'room':rowData[5].strip()
                            }
                            dataTimes[coursenumber].append(time)
            else:
                print("No course offering.")
        else:
            print("Server unavailable.")

    goks = Building.objects.get_or_create(bldg_code='GK',bldg_name='Gokongwei Hall')
    for c in courses:
        classnumber = c['coursenumber']
        course_code = c['coursecode']
        section_code = c['section']
        current_enrolled = int(c['enrolled'])
        max_enrolled = int(c['enrollcap'])
        faculty_name = '' 
        if(classnumber in dataFaculty):
            faculty_name = dataFaculty[classnumber]
        for d in dataTimes[classnumber]:
            time_begin = d['begintime'] 
            time_end= d['endtime']
            room_name = d['room'].strip()
            faculty = None
            if(faculty_name != ''):
                faculty = Faculty.objects.get_or_create(full_name=faculty_name)[0]
            course = Course.objects.get_or_create(course_code=course_code)[0]
            section = Section.objects.get_or_create(section_code=section_code)[0]
            day = Day.objects.get(day_code=d['day'])
            timeslot = Timeslot.objects.get_or_create(begin_time=time_begin, end_time=time_end)[0]
            room = Room.objects.get_or_create(building=goks[0], room_name=room_name, room_type='', room_capacity=40)[0]
            status = True
            CourseOffering.objects.get_or_create(classnumber=classnumber, faculty=faculty, course=course, section=section, day=day, timeslot=timeslot,room=room, status=status)
            offerings = CourseOffering.objects.filter(classnumber=classnumber, faculty=faculty, course=course, section=section, day=day, timeslot=timeslot,room=room, status=status)
            for o in offerings:
                o.current_enrolled = current_enrolled
                o.max_enrolled = max_enrolled
                o.save()
            print(course_code, section_code, faculty_name, d['day'], d['begintime'], d['endtime'], room_name, classnumber)

def init(request):
    def start_init():
        try:
            # Colleges
            ccs = College.objects.get_or_create(college_code='CCS', college_name='College of Computer Studies')
            # cla = College.objects.get_or_create(college_code='CLA', college_name='College of Liberal Arts')
            # cos = College.objects.get_or_create(college_code='COS', college_name='College of Science')
            # gcoe = College.objects.get_or_create(college_code='GCOE', college_name='Gokongwei College of Engineering')
            # soe = College.objects.get_or_create(college_code='SOE', college_name='School of Economics')
            # bagced = College.objects.get_or_create(college_code='BAGCED', college_name='Br. Andrew Gonzalez College of Education')
            # rvrcob = College.objects.get_or_create(college_code='RVRCOB', college_name='Ramon V. Del Rosario College of Business')
            # Degrees
            Degree.objects.get_or_create(degree_code='BS CS', degree_name='Bachelor of Science in Computer Science', college=ccs[0])
            # Degree.objects.get_or_create(degree_code='BS IT', degree_name='Bachelor of Science in Information Technology', college=ccs[0])
            # Degree.objects.get_or_create(degree_code='BS-PSY', degree_name='Bachelor of Science in Psychology', college=cla[0])
            # Degree.objects.get_or_create(degree_code='AB-SOC', degree_name='Bachelor of Arts in Sociology', college=cla[0])
            # Degree.objects.get_or_create(degree_code='AEI-BSA', degree_name='Bachelor of Science in Applied Economics, Major in Industrial Economics and Bachelor of Science in Accountancy', college=soe[0])
            # Degree.objects.get_or_create(degree_code='AEI-ADV', degree_name='Bachelor of Science in Applied Economics, Major in Industrial Economics and Bachelor of Science in Advertising Management', college=soe[0])
            # Buildings
            goks = Building.objects.get_or_create(bldg_code='GK',bldg_name='Gokongwei Hall')
            lasalle = Building.objects.get_or_create(bldg_code='LS',bldg_name='St. La Salle Hall')
            yuch = Building.objects.get_or_create(bldg_code='Y',bldg_name='Enrique Yuchengco Hall')
            joseph = Building.objects.get_or_create(bldg_code='J',bldg_name='St. Joseph Hall')
            velasco = Building.objects.get_or_create(bldg_code='V',bldg_name='Velasco Hall')
            miguel = Building.objects.get_or_create(bldg_code='M',bldg_name='St. Miguel Hall')
            mutien = Building.objects.get_or_create(bldg_code='MU',bldg_name='St. Mutien Marie Hall')
            andrew = Building.objects.get_or_create(bldg_code='A',bldg_name='Br. Andrew Gonzales Hall')
            # Days
            monday = Day.objects.get_or_create(day_code='M', day_name='Monday')
            tuesday = Day.objects.get_or_create(day_code='T', day_name='Tuesday')
            wednesday = Day.objects.get_or_create(day_code='W', day_name='Wednesday')
            thursday = Day.objects.get_or_create(day_code='H', day_name='Thursday')
            friday = Day.objects.get_or_create(day_code='F', day_name='Friday')
            saturday = Day.objects.get_or_create(day_code='S', day_name='Saturday')
        except Exception as e:
            return HttpResponse(e)

        try:
            def retrieveCourse(c):
                courses = []
                dataTimes = {}
                dataFaculty = {}
                if(c.strip() != ''):
                    URL = "http://enroll.dlsu.edu.ph/dlsu/view_actual_count"
                    PARAMS = {'p_course_code':c}
                    print("Retrieving data for "+c+"...")
                    
                    try:
                        r = requests.post(url = URL, params = PARAMS)
                    except:
                        return "Request encountered an error."

                    if(r.status_code == 200):
                        parsed = BeautifulSoup(r.text, "html5lib").center
                        rows = parsed.find_all("tr")
                        prevCourse = None
                        if(len(rows) > 1):
                            for row in rows[1:]:
                                rowData = row.get_text().strip().split("\n")
                                if(len(rowData) == 1):
                                    faculty = rowData[0].strip()
                                    dataFaculty[prevCourse] = faculty
                                elif(len(rowData) == 2):
                                    times = rowData[1].strip().split(' ')
                                    begintime = times[0][0:2] + ':' + times[0][2:4]
                                    endtime = times[2][0:2] + ':' + times[2][2:4]
                                    for day in rowData[0].strip():
                                        if prevCourse not in dataTimes:
                                            dataTimes[prevCourse] = []
                                        time = {
                                            'day':day,
                                            'begintime':begintime,
                                            'endtime':endtime,
                                            'room':''
                                        }
                                        dataTimes[prevCourse].append(time)
                                elif(len(rowData) == 3):
                                    times = rowData[1].strip().split(' ')
                                    begintime = times[0][0:2] + ':' + times[0][2:4]
                                    endtime = times[2][0:2] + ':' + times[2][2:4]
                                    for day in rowData[0].strip():
                                        if prevCourse not in dataTimes:
                                            dataTimes[prevCourse] = []
                                        time = {
                                            'day':day,
                                            'begintime':begintime,
                                            'endtime':endtime,
                                            'room':rowData[2].strip()
                                        }
                                        dataTimes[prevCourse].append(time)
                                elif(len(rowData) >= 8):
                                    coursenumber = int(rowData[0].strip())
                                    times = rowData[4].strip().split(' ')
                                    begintime = times[0][0:2] + ':' + times[0][2:4]
                                    endtime = times[2][0:2] + ':' + times[2][2:4]
                                    course = { 
                                        'coursenumber':coursenumber,
                                        'coursecode':rowData[1].strip(),
                                        'section':rowData[2].strip(),
                                        'enrollcap':rowData[6].strip(),
                                        'enrolled':rowData[7].strip(),
                                    }
                                    prevCourse = coursenumber
                                    courses.append(course)
                                    for day in rowData[3].strip():
                                        if coursenumber not in dataTimes:
                                            dataTimes[coursenumber] = []
                                        time = {
                                            'day':day,
                                            'begintime':begintime,
                                            'endtime':endtime,
                                            'room':rowData[5].strip()
                                        }
                                        dataTimes[coursenumber].append(time)
                        else:
                            print("No course offering.")
                    else:
                        print("Server unavailable.")
                for c in courses:
                    classnumber = c['coursenumber']
                    course_code = c['coursecode']
                    section_code = c['section']
                    current_enrolled = int(c['enrolled'])
                    max_enrolled = int(c['enrollcap'])
                    faculty_name = '' 
                    if(classnumber in dataFaculty):
                        faculty_name = dataFaculty[classnumber]
                    if(classnumber in dataTimes):
                        for d in dataTimes[classnumber]:
                            time_begin = d['begintime'] 
                            time_end= d['endtime']
                            room_name = d['room'].strip()
                            faculty = None
                            if(faculty_name != ''):
                                faculty = Faculty.objects.get_or_create(full_name=faculty_name)[0]
                            course = Course.objects.get_or_create(course_code=course_code)[0]
                            section = Section.objects.get_or_create(section_code=section_code)[0]
                            day = Day.objects.get(day_code=d['day'])
                            timeslot = Timeslot.objects.get_or_create(begin_time=time_begin, end_time=time_end)[0]
                            room = Room.objects.get_or_create(building=goks[0], room_name=room_name, room_type='', room_capacity=40)[0]
                            status = True
                            CourseOffering.objects.get_or_create(classnumber=classnumber, faculty=faculty, course=course, section=section, day=day, timeslot=timeslot,room=room, status=status)
                            offerings = CourseOffering.objects.filter(classnumber=classnumber, faculty=faculty, course=course, section=section, day=day, timeslot=timeslot,room=room, status=status)
                            for o in offerings:
                                o.current_enrolled = current_enrolled
                                o.max_enrolled = max_enrolled
                                o.save()
                            print(course_code, section_code, faculty_name, d['day'], d['begintime'], d['endtime'], room_name, classnumber)
                    else:
                        time_begin = '00:00'
                        time_end = '00:00'
                        room_name = ''
                        faculty = None
                        if(faculty_name != ''):
                            faculty = Faculty.objects.get_or_create(full_name=faculty_name)[0]
                        course = Course.objects.get_or_create(course_code=course_code)[0]
                        section = Section.objects.get_or_create(section_code=section_code)[0]
                        timeslot = Timeslot.objects.get_or_create(begin_time=time_begin, end_time=time_end)[0]
                        room = Room.objects.get_or_create(building=goks[0], room_name=room_name, room_type='', room_capacity=40)[0]
                        status = True
                        CourseOffering.objects.get_or_create(classnumber=classnumber, faculty=faculty, course=course, section=section, timeslot=timeslot,room=room, status=status)
                        offerings = CourseOffering.objects.filter(classnumber=classnumber, faculty=faculty, course=course, section=section, timeslot=timeslot,room=room, status=status)
                        for o in offerings:
                            o.current_enrolled = current_enrolled
                            o.max_enrolled = max_enrolled
                            o.save()
                        print(course_code, section_code, faculty_name, room_name, classnumber)

        except Exception as e:
            print(e)
        with open('courselist.txt','r') as course_list:
            for c in course_list:
                try:
                    retrieveCourse(c.rstrip())
                except Exception as e:
                  print(e)
    _thread.start_new_thread(start_init,())
    return HttpResponse('Adrienne Soliven is cute <3')