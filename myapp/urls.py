from django.urls import path
from .views import PingView, ConnectView, FetchDataView, LoginView, SignupView

urlpatterns = [
    path('ping/', PingView.as_view(), name='ping'),
    path('connect/', ConnectView.as_view(), name='connect'),
    path('fetch_data/', FetchDataView.as_view(), name='fetch_data'),
    path('login/', LoginView.as_view(), name='login'),  # Login API
    path('signup/', SignupView.as_view(), name='signup'),
]
