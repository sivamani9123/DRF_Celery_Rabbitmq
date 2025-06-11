from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls), //Kind of login page
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), // provide access token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), // To get refresh token 
    path('api/', include('myapp.urls')), 
]
