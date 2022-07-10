from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FollowListAPIView, UserFollowApiView

app_name = 'users'

router_v1 = DefaultRouter()

urlpatterns = [
    path('users/<int:id>/subscribe/', UserFollowApiView.as_view(),
         name='subscribe'),
    path('users/subscriptions/', FollowListAPIView.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]
