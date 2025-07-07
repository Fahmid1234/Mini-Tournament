from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.db.models import Count, Sum, Avg
from django.utils.html import format_html
from teams.models import Team, Player
from matches.models import Match, PlayerMatchPerformance, TournamentAwards, PointsTableEntry

class GPLAdminSite(AdminSite):
    site_header = "🏏 Gali Premier League Mini Tournament"
    site_title = "🏏 GPL Tournament Admin"
    index_title = "🏏 Tournament Dashboard"
    
    def index(self, request, extra_context=None):
        """
        Display the main admin index page with statistics.
        """
        # Get statistics
        teams_count = Team.objects.count()
        players_count = Player.objects.count()
        matches_count = Match.objects.count()
        performances_count = PlayerMatchPerformance.objects.count()
        awards_count = TournamentAwards.objects.count()
        
        # Get recent matches
        recent_matches = Match.objects.select_related('team1', 'team2').order_by('-date')[:5]
        
        # Get top performers
        top_batsmen = PlayerMatchPerformance.objects.select_related('player', 'team').order_by('-runs_scored')[:5]
        top_bowlers = PlayerMatchPerformance.objects.select_related('player', 'team').order_by('-wickets_taken')[:5]
        
        # Get points table
        points_table = PointsTableEntry.objects.select_related('team').order_by('-points', '-nrr')[:5]
        
        extra_context = extra_context or {}
        extra_context.update({
            'teams_count': teams_count,
            'players_count': players_count,
            'matches_count': matches_count,
            'performances_count': performances_count,
            'awards_count': awards_count,
            'recent_matches': recent_matches,
            'top_batsmen': top_batsmen,
            'top_bowlers': top_bowlers,
            'points_table': points_table,
        })
        
        return super().index(request, extra_context)

# Create custom admin site instance
admin_site = GPLAdminSite(name='gpl_admin')

# Admin classes
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_theme', 'player_count', 'logo_preview']
    list_filter = ['color_theme']
    search_fields = ['name']
    readonly_fields = ['logo_preview']
    
    def player_count(self, obj):
        return obj.players.count()
    player_count.short_description = 'Players'
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px;" />', obj.logo.url)
        return "No Logo"
    logo_preview.short_description = 'Logo'

class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'team', 'total_runs', 'total_wickets']
    list_filter = ['role', 'team']
    search_fields = ['name', 'team__name']
    
    def total_runs(self, obj):
        total = obj.match_performances.aggregate(total=Sum('runs_scored'))['total'] or 0
        return total
    total_runs.short_description = 'Total Runs'
    
    def total_wickets(self, obj):
        total = obj.match_performances.aggregate(total=Sum('wickets_taken'))['total'] or 0
        return total
    total_wickets.short_description = 'Total Wickets'

class MatchAdmin(admin.ModelAdmin):
    list_display = ['team1', 'team2', 'date', 'status', 'result_display', 'player_of_match']
    list_filter = ['status', 'date']
    search_fields = ['team1__name', 'team2__name']
    date_hierarchy = 'date'
    
    def result_display(self, obj):
        if obj.status == 'completed':
            return f"{obj.team1_score} - {obj.team2_score}"
        return "TBD"
    result_display.short_description = 'Result'

class PlayerMatchPerformanceAdmin(admin.ModelAdmin):
    list_display = ['player', 'match', 'team', 'runs_scored', 'wickets_taken', 'strike_rate', 'economy_rate']
    list_filter = ['team', 'match__date']
    search_fields = ['player__name', 'team__name']
    readonly_fields = ['strike_rate', 'economy_rate']
    
    def strike_rate(self, obj):
        return f"{obj.strike_rate:.2f}"
    strike_rate.short_description = 'Strike Rate'
    
    def economy_rate(self, obj):
        return f"{obj.economy_rate:.2f}"
    economy_rate.short_description = 'Economy Rate'

class TournamentAwardsAdmin(admin.ModelAdmin):
    list_display = ['award_type', 'player', 'value', 'description']
    list_filter = ['award_type']
    search_fields = ['player__name', 'award_type']

class PointsTableEntryAdmin(admin.ModelAdmin):
    list_display = ['team', 'matches_played', 'wins', 'losses', 'points', 'nrr']
    list_filter = ['matches_played']
    search_fields = ['team__name']
    readonly_fields = ['nrr']
    
    def nrr(self, obj):
        return f"{obj.nrr:.3f}"
    nrr.short_description = 'Net Run Rate'

# Register models with custom admin site
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(Team, TeamAdmin)
admin_site.register(Player, PlayerAdmin)
admin_site.register(Match, MatchAdmin)
admin_site.register(PlayerMatchPerformance, PlayerMatchPerformanceAdmin)
admin_site.register(TournamentAwards, TournamentAwardsAdmin)
admin_site.register(PointsTableEntry, PointsTableEntryAdmin) 