from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignUpView, LogInView, PasswordResetView, PasswordResetSuccessView

app_name = 'registration'
urlpatterns = [
    path('login/', LogInView, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('signup/', SignUpView, name='signup'),
    path('password_reset/', PasswordResetView, name='password_reset'),
    path('password_reset_success/', PasswordResetSuccessView, name='password_reset_success'),
]
