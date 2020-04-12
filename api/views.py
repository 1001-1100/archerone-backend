from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets          
from .serializers import CustomRegisterSerializer, ScheduleSerializer, TimeslotSerializer, CourseOfferingSerializer, PreferenceSerializer, UserSerializer, CourseSerializer, DegreeSerializer, CollegeSerializer, CoursePrioritySerializer, DaySerializer, FacultySerializer, BuildingSerializer, SectionSerializer, FlowchartTermSerializer
from .models import User, Schedule, Course, Degree, College, CoursePriority, Preference, Day, Faculty, Building, Section, CourseOffering, Timeslot, Room, FlowchartTerm
from .satsolver import solve
from rest_framework.response import Response
from rest_framework.views import APIView

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
        schedules = Schedule.objects.filter(user=pk)
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

class CourseOfferingsList(APIView):
  def post(self, request, format=None):
      courseData = []
      for c in request.data['courses']:
        offerings = CourseOffering.objects.filter(course=c)
        serializer = CourseOfferingSerializer(offerings, many=True)
        for d in serializer.data:
          if(d['faculty'] != None):
            d['faculty'] = Faculty.objects.get(id=d['faculty']).full_name
          d['course'] = Course.objects.get(id=d['course']).course_code
          d['section'] = Section.objects.get(id=d['section']).section_code  
          d['day'] = Day.objects.get(id=d['day']).day_code  
          d['timeslot_begin'] = Timeslot.objects.get(id=d['timeslot']).begin_time  
          d['timeslot_end'] = Timeslot.objects.get(id=d['timeslot']).end_time
          if(d['room'] != None):
            d['room'] = Room.objects.get(id=d['room']).room_name
        courseData.append(serializer.data)
      return Response(courseData)

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

    serializedSchedules = []
    schedules = solve(highCourses, lowCourses, preferences)
    for s in schedules:
      serializedSchedule = {}
      serializer = CourseOfferingSerializer(s['offerings'], many=True)
      for d in serializer.data:
        if(d['faculty'] != None):
          d['faculty'] = Faculty.objects.get(id=d['faculty']).full_name
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