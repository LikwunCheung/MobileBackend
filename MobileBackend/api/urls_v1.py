# -*- coding: utf-8 -*-

from django.urls import path

from .views.account import login, register, validate, forget_password, forget_validate
from .views.profile import profile_router
from .views.file import file_router


urlpatterns = [

    # Account Service
    path('login', login),
    path('register', register),
    path('validate', validate),
    path('forget', forget_password),
    path('forget/validate', forget_validate),
    path('profile', profile_router),

    # Picture Service
    path('picture', file_router),
    path('picture/<str:id>', file_router),
]
