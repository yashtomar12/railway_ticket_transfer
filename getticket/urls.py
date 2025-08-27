from django.urls import path
from . import views

app_name = "getticket"

urlpatterns = [
   
    path("home/", views.home, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("chatbot/", views.chatbot_api, name="chatbot_api"),
    # User authentication
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.user_dashboard, name="user_dashboard"),

    # User requests
    path("request_transfer/", views.request_transfer, name="request_transfer"),
    path("my_requests/", views.my_requests, name="my_requests"),

    # Staff authentication & dashboard
    path("staff_login/", views.staff_login, name="staff_login"),
    path("staff_dashboard/", views.staff_dashboard, name="staff_dashboard"),

    # Staff actions
    path("approve/<int:pk>/", views.approve_request, name="approve_request"),
    path("reject/<int:pk>/", views.reject_request, name="reject_request"),
]
