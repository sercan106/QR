# accaunt/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),

    # 👇 Bu satır şablondaki {% url 'user_register' %} için gerekli!
    path('register/', views.step_1_check_tag, name='user_register'),

    path('register/step-1/', views.step_1_check_tag, name='step_1_check_tag'),
    path('register/step-2/', views.step_2_pet_info, name='step_2_pet_info'),
    path('register/step-3/', views.step_3_owner_info, name='step_3_owner_info'),
    path('register/step-4/', views.step_4_complete, name='step_4_complete'),
]
