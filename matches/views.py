from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum, Avg, Count, Q
from .models import Match, PointsTableEntry, PlayerMatchPerformance, TournamentAwards
from teams.models import Team, Player
from django.utils import timezone

def schedule(request):
    matches = Match.objects.all().order_by('date')
    return render(request, 'matches/schedule.html', {'matches': matches})

def results(request):
    from teams.models import Team
    teams = Team.objects.all()
    matches = Match.objects.all().order_by('-date')

    # Filters
    team_id = request.GET.get('team')
    date = request.GET.get('date')
    status = request.GET.get('status')

    if team_id and team_id.isdigit():
        matches = matches.filter(Q(team1_id=team_id) | Q(team2_id=team_id))
    if date:
        matches = matches.filter(date=date)
    if status and status in dict(Match.STATUS_CHOICES):
        matches = matches.filter(status=status)

    context = {
        'matches': matches,
        'teams': teams,
        'selected_team': int(team_id) if team_id and team_id.isdigit() else None,
        'selected_date': date,
        'selected_status': status,
    }
    return render(request, 'matches/results.html', context)

def points_table(request):
    points_table = PointsTableEntry.objects.all().order_by('-points', '-nrr')
    return render(request, 'matches/points_table.html', {'points_table': points_table})

def recalculate_points_table():
    """Recalculate the points table for all teams from all completed matches."""
    # Reset all points table entries
    for entry in PointsTableEntry.objects.all():
        entry.matches_played = 0
        entry.wins = 0
        entry.losses = 0
        entry.points = 0
        entry.runs_for = 0
        entry.runs_against = 0
        entry.overs_for = 0.0
        entry.overs_against = 0.0
        entry.nrr = 0.0
        entry.save()

    # Recalculate from all completed matches
    completed_matches = Match.objects.filter(status='completed', team1_score__isnull=False, team2_score__isnull=False)
    for match in completed_matches:
        team1_entry, _ = PointsTableEntry.objects.get_or_create(team=match.team1)
        team2_entry, _ = PointsTableEntry.objects.get_or_create(team=match.team2)
        T20_OVERS = 20.0
        team1_entry.matches_played += 1
        team2_entry.matches_played += 1
        team1_entry.runs_for += match.team1_score
        team1_entry.runs_against += match.team2_score
        team1_entry.overs_for += T20_OVERS
        team1_entry.overs_against += T20_OVERS
        team2_entry.runs_for += match.team2_score
        team2_entry.runs_against += match.team1_score
        team2_entry.overs_for += T20_OVERS
        team2_entry.overs_against += T20_OVERS
        if match.team1_score > match.team2_score:
            team1_entry.wins += 1
            team1_entry.points += 2
            team2_entry.losses += 1
        else:
            team2_entry.wins += 1
            team2_entry.points += 2
            team1_entry.losses += 1
        team1_entry.save()
        team2_entry.save()
    # Calculate NRR for all teams
    for entry in PointsTableEntry.objects.all():
        entry.calculate_nrr()

def update_points_table(match):
    recalculate_points_table()

def player_statistics(request):
    """Display player statistics and rankings"""
    
    # Batting statistics
    batting_stats = PlayerMatchPerformance.objects.values(
        'player__name', 'player__team__name', 'player__role'
    ).annotate(
        total_runs=Sum('runs_scored'),
        total_balls=Sum('balls_faced'),
        total_fours=Sum('fours'),
        total_sixes=Sum('sixes'),
        matches_played=Count('match', distinct=True),
        average=Avg('runs_scored'),
        strike_rate=Avg('strike_rate')
    ).filter(total_runs__gt=0).order_by('-total_runs')
    
    # Bowling statistics
    bowling_stats = PlayerMatchPerformance.objects.values(
        'player__name', 'player__team__name', 'player__role'
    ).annotate(
        total_wickets=Sum('wickets_taken'),
        total_runs_conceded=Sum('runs_conceded'),
        total_overs=Sum('overs_bowled'),
        matches_played=Count('match', distinct=True),
        average=Avg('runs_conceded'),
        economy_rate=Avg('economy_rate')
    ).filter(total_wickets__gt=0).order_by('-total_wickets')
    
    # All-rounder statistics (players with both batting and bowling)
    all_rounder_stats = []
    for player in Player.objects.all():
        batting = batting_stats.filter(player__name=player.name).first()
        bowling = bowling_stats.filter(player__name=player.name).first()
        
        if batting and bowling:
            all_rounder_stats.append({
                'player': player,
                'batting_runs': batting['total_runs'],
                'bowling_wickets': bowling['total_wickets'],
                'all_rounder_score': batting['total_runs'] + (bowling['total_wickets'] * 25)  # Simple scoring
            })
    
    all_rounder_stats.sort(key=lambda x: x['all_rounder_score'], reverse=True)
    
    context = {
        'batting_stats': batting_stats,
        'bowling_stats': bowling_stats,
        'all_rounder_stats': all_rounder_stats,
    }
    return render(request, 'matches/player_statistics.html', context)

def tournament_awards(request):
    """Display tournament awards and achievements"""
    
    # Get or create awards
    awards = {}
    
    # Highest run scorer
    top_batsman = PlayerMatchPerformance.objects.values(
        'player__name', 'player__team__name'
    ).annotate(
        total_runs=Sum('runs_scored')
    ).filter(total_runs__gt=0).order_by('-total_runs').first()
    
    if top_batsman:
        award, created = TournamentAwards.objects.get_or_create(
            award_type='highest_run_scorer',
            defaults={
                'player': Player.objects.get(name=top_batsman['player__name']),
                'value': top_batsman['total_runs'],
                'description': f"Highest run scorer with {top_batsman['total_runs']} runs"
            }
        )
        if not created:
            award.player = Player.objects.get(name=top_batsman['player__name'])
            award.value = top_batsman['total_runs']
            award.description = f"Highest run scorer with {top_batsman['total_runs']} runs"
            award.save()
        awards['highest_run_scorer'] = award
    
    # Highest wicket taker
    top_bowler = PlayerMatchPerformance.objects.values(
        'player__name', 'player__team__name'
    ).annotate(
        total_wickets=Sum('wickets_taken')
    ).filter(total_wickets__gt=0).order_by('-total_wickets').first()
    
    if top_bowler:
        award, created = TournamentAwards.objects.get_or_create(
            award_type='highest_wicket_taker',
            defaults={
                'player': Player.objects.get(name=top_bowler['player__name']),
                'value': top_bowler['total_wickets'],
                'description': f"Highest wicket taker with {top_bowler['total_wickets']} wickets"
            }
        )
        if not created:
            award.player = Player.objects.get(name=top_bowler['player__name'])
            award.value = top_bowler['total_wickets']
            award.description = f"Highest wicket taker with {top_bowler['total_wickets']} wickets"
            award.save()
        awards['highest_wicket_taker'] = award
    
    # Player of the Tournament (based on overall performance)
    player_of_tournament = None
    if top_batsman and top_bowler:
        # Simple scoring: runs + (wickets * 25)
        batsman_score = top_batsman['total_runs']
        bowler_score = top_bowler['total_wickets'] * 25
        
        if batsman_score >= bowler_score:
            player_of_tournament = Player.objects.get(name=top_batsman['player__name'])
            score = batsman_score
        else:
            player_of_tournament = Player.objects.get(name=top_bowler['player__name'])
            score = bowler_score
        
        award, created = TournamentAwards.objects.get_or_create(
            award_type='player_of_tournament',
            defaults={
                'player': player_of_tournament,
                'value': score,
                'description': f"Player of the Tournament with score {score}"
            }
        )
        if not created:
            award.player = player_of_tournament
            award.value = score
            award.description = f"Player of the Tournament with score {score}"
            award.save()
        awards['player_of_tournament'] = award
    
    # Get all awards
    all_awards = TournamentAwards.objects.all()
    
    context = {
        'awards': awards,
        'all_awards': all_awards,
    }
    return render(request, 'matches/tournament_awards.html', context)
