from django.urls import path

from base import views

urlpatterns = [
    path("", views.HelloView.as_view()),
    path("login/", views.LoginView.as_view()),
    path("administrator/user", views.UserListView.as_view()),
    path("administrator/organizations", views.OrganizationsView.as_view()),
    path("administrator/worktime", views.WorktimeListView.as_view()),
    path("organizations/<str:pk>/generateqr", views.GenerateQR.as_view()),
    path("organizations/<str:pk>/checkin", views.CheckinView.as_view()),
    path("organizations/<str:pk>/employees", views.UserListViewOrganization.as_view()),
    path("organizations/<str:pk>/worktime", views.WorktimeListViewOrg.as_view()),
    path("organizations/<str:pk>/monthwork", views.MonthTotalWorkView.as_view()),
]