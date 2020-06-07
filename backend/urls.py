from django.contrib import admin
from django.urls import path, include                 
from rest_framework import routers                    
from rest_framework_jwt.views import refresh_jwt_token
from api import views                            
from django.conf import settings
from django.conf.urls.static import static
from rest_auth.registration.views import VerifyEmailView, RegisterView

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
router.register(r'friendrequests', views.FriendRequestViewSet)     
router.register(r'notifications', views.NotificationViewSet)     
router.register(r'colleges', views.CollegeViewSet)    
router.register(r'flowchartterms', views.FlowchartTermViewSet)

urlpatterns = [
    path('api/', include(router.urls)),                
    path('api/init/', views.init),   
    path('api/addcourse/<slug:term>/', views.RetrieveCourse.as_view()),   
    path('api/generateschedule/', views.SchedulesList.as_view()),
    path('api/editschedule/', views.EditSchedule.as_view()),
    path('api/preferencelist/<int:pk>/', views.PreferenceList.as_view()),     
    path('api/friendlist/<int:pk>/', views.FriendList.as_view()),     
    path('api/searchcourse/<slug:term>/', views.SearchCourse.as_view()),     
    path('api/friendrequestlist/<int:pk>/', views.FriendRequestList.as_view()),     
    path('api/sentrequestlist/<int:pk>/', views.SentRequestList.as_view()),     
    path('api/nonfriendlist/<int:pk>/', views.NonFriendList.as_view()),     
    path('api/notificationlist/<int:pk>/', views.NotificationList.as_view()),     
    path('api/schedulelist/<int:pk>/', views.SavedScheduleList.as_view()),     
    path('api/courseprioritylist/<int:pk>/', views.CoursePriorityList.as_view()),     
    path('api/courseofferingslist/', views.CourseOfferingsList.as_view()),     
    path('api/flowcharttermslist/<int:pk>/<int:pk2>/', views.FlowchartTermsList.as_view()),    
    path('api/auth/', include('rest_auth.urls')),                
    path('api/auth/registration/', include('rest_auth.registration.urls')),                
    path('api/auth/registration/', include('allauth.urls')),                
    # path('api/auth/registration/account-confirm-email/', VerifyEmailView.as_view(),
    # name='account_email_verification_sent'),
    # path('api/auth/registration/account-confirm-email/(?P<key>\w+)/$', VerifyEmailView.as_view(),
    # name='account_confirm_email'),
    path('api/refresh-token/', refresh_jwt_token),
    # path('', include('django.contrib.auth.urls')),                
    path('accounts/', include('allauth.urls')),                
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)