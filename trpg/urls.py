from django.urls import path
from . import views

urlpatterns = [
    path('', views.scenario_list, name='scenario_list'),
    path('start/<int:scenario_id>/', views.start_game, name='start_game'),
    path('game/<int:session_id>/', views.game_session, name='game_session'),
    path('api/send_message/<int:session_id>/', views.send_message, name='send_message'),
    path('game/<int:session_id>/logs/', views.log_view, name='log_view'),
]
