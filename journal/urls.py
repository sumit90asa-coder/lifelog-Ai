from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views
from . import api
from . import auth_api

urlpatterns = [

    # ====================================
    # FRONTEND PAGES
    # ====================================

    path('',           views.login_page,    name='home'),
    path('login/',     views.login_page,    name='login'),
    path('register/',  views.register_page, name='register'),
    path('dashboard/', views.dashboard,     name='dashboard'),
    path('insights/',  views.insights_page, name='insights_page'),
    path('entries/',   views.entries_page,  name='entries_page'),
    path('profile/',   views.profile_page,  name='profile_page'),

    # ====================================
    # JWT AUTH
    # ====================================

    path('api/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),
    path('api/token/verify/',  TokenVerifyView.as_view(),     name='token_verify'),

    # ====================================
    # AUTH API
    # ====================================

    path('api/register/', auth_api.register, name='register_api'),

    # ====================================
    # JOURNAL API
    # ====================================

    path('api/entries/',           api.entries,       name='entries'),
    path('api/entries/<int:pk>/',  api.entry_detail,  name='entry_detail'),
    path('api/entries/preview/',   api.preview_entry, name='preview_entry'),
    path('api/insights/',          api.insights,      name='insights'),
    path('api/streak/',            api.streak_status, name='streak_status'),
    path('api/ai-insights/',       api.ai_insights,   name='ai_insights'),
    path('api/me/',                api.me,            name='me'),

]