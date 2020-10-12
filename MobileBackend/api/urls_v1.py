# -*- coding: utf-8 -*-

from django.urls import path

from .views.account import login, register, validate, forget_password, forget_validate
from .views.friend import friend_router, search_friend, friend_notice, friend_accept
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

    # Friend Service
    path('friend', friend_router),
    path('friend/search', search_friend),
    path('friend/notice', friend_notice),
    path('friend/action', friend_accept),
    # path('friend/remove', remove_friend),

    # Picture Service
    path('picture', file_router),
    path('picture/<str:id>', file_router),
]
