from django.urls import path
from . import views

urlpatterns = [
    path('known/', views.known_faces_list, name='known_faces_list'),
    path('enroll/', views.enroll_face_view, name='enroll_face'),
    path('delete/<int:fid>/', views.delete_known_face, name='delete_known_face'),
    path('recognize/', views.recognize_view, name='recognize_view'),
    path('recognize/api/', views.recognize_api, name='recognize_api'),
    path('logs/', views.recognition_logs_view, name='recognition_logs'),
]
