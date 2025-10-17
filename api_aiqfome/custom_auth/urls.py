from django.urls import path

from .views import (
    DecoratedTokenObtainPairView, 
    DecoratedTokenRefreshView, 
    DecoratedTokenBlacklistView
)

urlpatterns = [
    path('login', DecoratedTokenObtainPairView.as_view()),
    path('refresh', DecoratedTokenRefreshView.as_view()),
    path('logout', DecoratedTokenBlacklistView.as_view()),
]
