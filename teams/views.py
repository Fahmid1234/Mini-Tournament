from django.shortcuts import render, get_object_or_404
from .models import Team, Player

# Create your views here.

def team_list(request):
    teams = Team.objects.all()
    return render(request, 'teams/team_list.html', {'teams': teams})

def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    players = team.players.all()
    return render(request, 'teams/team_detail.html', {'team': team, 'players': players})
