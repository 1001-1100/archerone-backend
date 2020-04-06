from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

from .models import College, Degree, Course, Faculty, Section, Building, Room, Day, Timeslot, CourseOffering, CoursePriority, Schedule, User, Preference

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm

class CollegeSerializer(serializers.ModelSerializer):
  class Meta:
    model = College 
    fields = ('id', 'college_code', 'college_name')

class DegreeSerializer(serializers.ModelSerializer):
  class Meta:
    model = Degree 
    fields = ('id', 'degree_code', 'degree_name', 'college')

class CourseSerializer(serializers.ModelSerializer):
  class Meta:
    model = Course 
    fields = ('id', 'course_code', 'course_name', 'course_desc', 'college', 'units')

class FacultySerializer(serializers.ModelSerializer):
  class Meta:
    model = Faculty 
    fields = ('id', 'full_name')

class SectionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Section 
    fields = ('id', 'section_code')

class BuildingSerializer(serializers.ModelSerializer):
  class Meta:
    model = Building 
    fields = ('id', 'bldg_code', 'bldg_name')

class RoomSerializer(serializers.ModelSerializer):
  class Meta:
    model = Room 
    fields = ('id', 'building', 'room_type', 'room_capacity')

class DaySerializer(serializers.ModelSerializer):
  class Meta:
    model = Day 
    fields = ('id','day_code', 'day_name')

class TimeslotSerializer(serializers.ModelSerializer):
  class Meta:
    model = Timeslot 
    fields = ('id', 'begin_time', 'end_time')

class CourseOfferingSerializer(serializers.ModelSerializer):
  class Meta:
    model = CourseOffering 
    fields = ('id', 'classnumber', 'faculty', 'course', 'section', 'day', 'timeslot', 'room', 'current_enrolled', 'max_enrolled', 'status')

class CoursePrioritySerializer(serializers.ModelSerializer):
  class Meta:
    model = CoursePriority 
    fields = ('id', 'courses', 'priority', 'user')

class ScheduleSerializer(serializers.ModelSerializer):
  class Meta:
    model = Schedule 
    fields = ('id', 'title', 'courseOfferings', 'user')

class PreferenceSerializer(serializers.ModelSerializer):
  class Meta:
    model = Preference
    fields = ('id', 'earliest_class_time', 'latest_class_time', 'preferred_days', 'break_length', 'min_courses', 'max_courses', 'preferred_faculty', 'preferred_buildings', 'preferred_sections', 'user')

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'email', 'first_name', 'last_name', 'college', 'degree', 'friends', 'is_active')

class CustomRegisterSerializer(RegisterSerializer):
    # username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    # college = CollegeSerializer()
    college = serializers.PrimaryKeyRelatedField(queryset=College.objects.all(), required=True)
    degree = serializers.PrimaryKeyRelatedField(queryset=Degree.objects.all(),required=True)
    
    def validate_email(self, value):
        if "@dlsu.edu.ph" not in value:
            raise serializers.ValidationError("Please enter a valid DLSU email address.")
        return value

    def get_cleaned_data(self):
        super(CustomRegisterSerializer, self).get_cleaned_data()

        return {
            # 'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1',''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'college': self.validated_data.get('college',''),
            'degree': self.validated_data.get('degree','') 
        }
    def save(self, request):
      adapter = get_adapter()
      user = adapter.new_user(request)
      self.cleaned_data = self.get_cleaned_data()
      user.college = self.get_cleaned_data().get('college')
      user.degree = self.get_cleaned_data().get('degree')
      adapter.save_user(request, user, self)
      self.custom_signup(request, user)
      setup_user_email(request, user, [])
      return user

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password_reset_form_class = PasswordResetForm

    def validate_email(self, value):
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(_('Error'))

        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('Invalid e-mail address'))

        return value

    def save(self):
        request = self.context.get('request')
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'html_email_template_name': 'password_reset_email.html',
            'request': request,
        }
        self.reset_form.save(**opts)
