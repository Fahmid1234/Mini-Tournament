from django.urls import path
from . import views

urlpatterns = [
    path('schedule/', views.schedule, name='schedule'),
    path('results/', views.results, name='results'),
    path('points-table/', views.points_table, name='points_table'),
    path('player-statistics/', views.player_statistics, name='player_statistics'),
    path('tournament-awards/', views.tournament_awards, name='tournament_awards'),
] 