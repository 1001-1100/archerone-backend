from django.contrib import admin
from django.urls import path, include                 
from rest_framework import routers                    
from rest_framework_jwt.views import refresh_jwt_token
from api import views                            

router = routers.DefaultRouter()                      
router.register(r'users', views.UserViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'courses', views.CourseViewSet)     
router.register(r'degrees', views.DegreeViewSet)     
router.register(r'faculty', views.FacultyViewSet)     
router.register(r'days', views.DayViewSet)     
router.register(r'buildings', views.BuildingViewSet)     
router.register(r'sections', views.SectionViewSet)     
router.register(r'degrees', views.DegreeViewSet)     
router.register(r'preferences', views.PreferenceViewSet)     
router.register(r'timeslots', views.TimeslotViewSet)     
router.register(r'coursepriority', views.CoursePriorityViewSet)     
router.register(r'courseoffering', views.CourseOfferingViewSet)     
router.register(r'colleges', views.CollegeViewSet)     

urlpatterns = [
    path('api/', include(router.urls)),                
    path('api/generateschedule/', views.SchedulesList.as_view()),
    path('api/preferencelist/<int:pk>/', views.PreferenceList.as_view()),     
    path('api/courseprioritylist/<int:pk>/', views.CoursePriorityList.as_view()),     
    path('api/courseofferingslist/<int:pk>/', views.CourseOfferingsList.as_view()),     
    path('api/auth/', include('rest_auth.urls')),                
    path('api/auth/registration/', include('rest_auth.registration.urls')),                
    path('api/refresh-token/', refresh_jwt_token),
    path('', include('django.contrib.auth.urls')),                
]