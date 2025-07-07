from django.shortcuts import render
from teams.models import Team
from matches.models import Match, PointsTableEntry

def home(request):
    teams = Team.objects.all()
    upcoming_matches = Match.objects.filter(status='upcoming').order_by('date')[:3]
    recent_matches = Match.objects.filter(status='completed').order_by('-date')[:3]
    points_table = PointsTableEntry.objects.all().order_by('-points')
    
    context = {
        'teams': teams,
        'upcoming_matches': upcoming_matches,
        'recent_matches': recent_matches,
        'points_table': points_table,
    }
    return render(request, 'core/home.html', context)
