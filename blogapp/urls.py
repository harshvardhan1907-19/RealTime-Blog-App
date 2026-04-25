from django import views
from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .forms import Loginform
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r"posts", PostViewSet)

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name="post_delete"),
    path('post/<int:pk>/like/', like_post, name='post_like'),
    path('profile/', profile_view, name='profile'),
    path('api/posts/', api_post_list, name="api_post_list"),
    path('api/postget/<int:pk>', api_post_detail, name="api_post_detail"),
    path('api/postupdate/<int:pk>', api_post_update, name="api_post_update"),
    path('api/postdelete/<int:pk>', api_post_delete, name="api_post_delete"),
    path('api/postform', api_post_form, name="api_post_form"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('notifications/', notification_view, name='notifications'),
    path('notification/data/', get_notifications, name='get_notifications'),
    path('notification/count/', notification_count_api, name='notification_count'),
    path('notification/markread/<int:pk>/', mark_notification_read, name="notification_read"),

    path('filter-posts/', filter_posts, name='filter_posts'),

    path('api/loginuser', auth_views.LoginView.as_view(template_name='login.html', authentication_form=Loginform), name="login"),
    path('register/', register, name='register'),
]

urlpatterns += router.urls # This line actually activates those routes

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)