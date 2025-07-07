from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from .models import Match, PointsTableEntry, PlayerMatchPerformance, TournamentAwards
from teams.models import Team, Player

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_display', 'date', 'status_badge', 'result_display', 'score_display', 'match_actions')
    list_filter = ('status', 'date', 'team1', 'team2')
    search_fields = ('team1__name', 'team2__name', 'result')
    ordering = ('-date',)
    readonly_fields = ('result',)
    date_hierarchy = 'date'
    list_per_page = 20
    autocomplete_fields = ['team1', 'team2']
    
    fieldsets = (
        ('Match Information', {
            'fields': ('team1', 'team2', 'date', 'status', 'overs_per_innings'),
            'classes': ('wide',)
        }),
        ('Match Results', {
            'fields': ('team1_score', 'team2_score', 'result', 'player_of_match'),
            'classes': ('collapse',),
            'description': 'Enter the final scores to determine the match result.'
        }),
    )
    
    def match_display(self, obj):
        team1_color = self.get_team_color(obj.team1.color_theme)
        team2_color = self.get_team_color(obj.team2.color_theme)
        
        return format_html(
            '<div style="display: flex; align-items: center; gap: 12px; font-weight: bold;">'
            '<div style="background: linear-gradient(135deg, {} 0%, {} 100%); color: white; padding: 6px 12px; border-radius: 8px; min-width: 80px; text-align: center;">{}</div>'
            '<span style="color: #6b7280; font-size: 14px;">VS</span>'
            '<div style="background: linear-gradient(135deg, {} 0%, {} 100%); color: white; padding: 6px 12px; border-radius: 8px; min-width: 80px; text-align: center;">{}</div>'
            '</div>',
            team1_color, team1_color, obj.team1.name, team2_color, team2_color, obj.team2.name
        )
    match_display.short_description = 'Match'
    
    def status_badge(self, obj):
        if obj.status == 'completed':
            color = '#10b981'
            icon = '✅'
            bg_color = 'rgba(16, 185, 129, 0.1)'
        else:
            color = '#3b82f6'
            icon = '⏳'
            bg_color = 'rgba(59, 130, 246, 0.1)'
        
        return format_html(
            '<span style="background: {}; color: {}; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; border: 1px solid {};">{} {}</span>',
            bg_color, color, color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def result_display(self, obj):
        if obj.result:
            return format_html('<span style="color: #059669; font-weight: bold; font-size: 14px;">{}</span>', obj.result)
        return format_html('<span style="color: #6b7280; font-style: italic;">Pending</span>')
    result_display.short_description = 'Result'
    
    def score_display(self, obj):
        if obj.team1_score is not None and obj.team2_score is not None:
            winner = obj.team1 if obj.team1_score > obj.team2_score else obj.team2
            winner_color = self.get_team_color(winner.color_theme)
            return format_html(
                '<div style="text-align: center;">'
                '<div style="font-weight: bold; color: #1f2937; font-size: 16px;">{} - {}</div>'
                '<div style="font-size: 11px; color: #6b7280; margin-top: 2px;">Winner: <span style="color: {}; font-weight: bold;">{}</span></div>'
                '</div>',
                obj.team1_score, obj.team2_score, winner_color, winner.name
            )
        return format_html('<span style="color: #6b7280; font-style: italic;">TBD</span>')
    score_display.short_description = 'Score'
    
    def match_actions(self, obj):
        team1_url = reverse('admin:teams_team_change', args=[obj.team1.id])
        team2_url = reverse('admin:teams_team_change', args=[obj.team2.id])
        return format_html(
            '<div style="display: flex; gap: 4px;">'
            '<a href="{}" class="btn btn-sm btn-outline-primary">Team 1</a>'
            '<a href="{}" class="btn btn-sm btn-outline-primary">Team 2</a>'
            '</div>',
            team1_url, team2_url
        )
    match_actions.short_description = 'Actions'
    
    def get_team_color(self, color_theme):
        colors = {
            'blue': '#3b82f6',
            'yellow': '#eab308',
            'red': '#ef4444',
            'purple': '#8b5cf6',
            'green': '#10b981',
            'orange': '#f97316',
        }
        return colors.get(color_theme, '#6b7280')
    
    # Custom admin actions
    actions = ['mark_as_completed', 'mark_as_upcoming', 'update_points_table', 'generate_fixtures']
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} matches marked as completed.')
    mark_as_completed.short_description = "Mark selected matches as completed"
    
    def mark_as_upcoming(self, request, queryset):
        updated = queryset.update(status='upcoming')
        self.message_user(request, f'{updated} matches marked as upcoming.')
    mark_as_upcoming.short_description = "Mark selected matches as upcoming"
    
    def update_points_table(self, request, queryset):
        from .views import update_points_table
        count = 0
        for match in queryset.filter(status='completed'):
            if match.team1_score is not None and match.team2_score is not None:
                update_points_table(match)
                count += 1
        self.message_user(request, f'Points table updated for {count} completed matches.')
    update_points_table.short_description = "Update points table for selected matches"
    
    def generate_fixtures(self, request, queryset):
        # Generate round-robin fixtures for all teams
        teams = list(Team.objects.all())
        if len(teams) < 2:
            self.message_user(request, 'Need at least 2 teams to generate fixtures.')
            return
        
        # Clear existing upcoming matches
        Match.objects.filter(status='upcoming').delete()
        
        # Generate round-robin fixtures
        fixtures_created = 0
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                match_date = timezone.now() + timezone.timedelta(days=fixtures_created * 2)
                Match.objects.create(
                    team1=teams[i],
                    team2=teams[j],
                    date=match_date,
                    status='upcoming'
                )
                fixtures_created += 1
        
        self.message_user(request, f'{fixtures_created} fixtures generated successfully.')
    generate_fixtures.short_description = "Generate round-robin fixtures"

@admin.register(PointsTableEntry)
class PointsTableEntryAdmin(admin.ModelAdmin):
    list_display = ('position', 'team_display', 'matches_played', 'wins', 'losses', 'points', 'nrr_display', 'performance_indicator', 'table_actions')
    list_filter = ('matches_played', 'wins', 'losses')
    search_fields = ('team__name',)
    ordering = ('-points', '-nrr')
    readonly_fields = ('matches_played', 'wins', 'losses', 'points', 'runs_for', 'runs_against', 'overs_for', 'overs_against', 'nrr')
    list_per_page = 20
    
    fieldsets = (
        ('Team Information', {
            'fields': ('team',),
            'classes': ('wide',)
        }),
        ('Match Statistics', {
            'fields': ('matches_played', 'wins', 'losses', 'points'),
            'classes': ('wide',)
        }),
        ('Run Rate Details', {
            'fields': ('runs_for', 'runs_against', 'overs_for', 'overs_against', 'nrr'),
            'classes': ('collapse',),
            'description': 'Net Run Rate calculation details.'
        }),
    )
    
    def position(self, obj):
        # Calculate position based on points and NRR
        all_entries = PointsTableEntry.objects.all().order_by('-points', '-nrr')
        position = list(all_entries).index(obj) + 1
        
        if position == 1:
            return format_html('<span style="color: #f59e0b; font-weight: bold; font-size: 16px;">🥇 {}</span>', position)
        elif position == 2:
            return format_html('<span style="color: #6b7280; font-weight: bold; font-size: 16px;">🥈 {}</span>', position)
        elif position == 3:
            return format_html('<span style="color: #f97316; font-weight: bold; font-size: 16px;">🥉 {}</span>', position)
        else:
            return format_html('<span style="color: #6b7280; font-weight: bold;">{}</span>', position)
    position.short_description = 'Pos'
    
    def team_display(self, obj):
        color = self.get_team_color(obj.team.color_theme)
        return format_html(
            '<div style="display: flex; align-items: center; gap: 10px;">'
            '<div style="width: 35px; height: 35px; background: linear-gradient(135deg, {} 0%, {} 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">{}</div>'
            '<span style="font-weight: bold; font-size: 14px;">{}</span>'
            '</div>',
            color, color, obj.team.name[:2].upper(), obj.team.name
        )
    team_display.short_description = 'Team'
    
    def nrr_display(self, obj):
        if obj.nrr > 0:
            color = '#10b981'
            prefix = '+'
            bg_color = 'rgba(16, 185, 129, 0.1)'
        elif obj.nrr < 0:
            color = '#ef4444'
            prefix = ''
            bg_color = 'rgba(239, 68, 68, 0.1)'
        else:
            color = '#6b7280'
            prefix = ''
            bg_color = 'rgba(107, 114, 128, 0.1)'
        
        # Format NRR as string to avoid SafeString issues
        nrr_formatted = f"{obj.nrr:.3f}"
        
        return format_html(
            '<span style="background: {}; color: {}; padding: 4px 8px; border-radius: 12px; font-weight: bold; font-size: 12px; border: 1px solid {};">{}{}</span>',
            bg_color, color, color, prefix, nrr_formatted
        )
    nrr_display.short_description = 'NRR'
    
    def performance_indicator(self, obj):
        if obj.matches_played == 0:
            return format_html('<span style="color: #6b7280; font-style: italic;">No matches</span>')
        
        win_rate = (obj.wins / obj.matches_played) * 100
        
        if win_rate >= 75:
            color = '#10b981'
            icon = '🔥'
            bg_color = 'rgba(16, 185, 129, 0.1)'
        elif win_rate >= 50:
            color = '#f59e0b'
            icon = '⚡'
            bg_color = 'rgba(245, 158, 11, 0.1)'
        elif win_rate >= 25:
            color = '#f97316'
            icon = '📈'
            bg_color = 'rgba(249, 115, 22, 0.1)'
        else:
            color = '#ef4444'
            icon = '📉'
            bg_color = 'rgba(239, 68, 68, 0.1)'
        
        # Format win rate as string to avoid SafeString issues
        win_rate_formatted = f"{win_rate:.1f}"
        
        return format_html(
            '<span style="background: {}; color: {}; padding: 4px 8px; border-radius: 12px; font-weight: bold; font-size: 12px; border: 1px solid {};">{} {}%</span>',
            bg_color, color, color, icon, win_rate_formatted
        )
    performance_indicator.short_description = 'Win Rate'
    
    def table_actions(self, obj):
        team_url = reverse('admin:teams_team_change', args=[obj.team.id])
        matches_url = reverse('admin:matches_match_changelist') + f'?team1__id__exact={obj.team.id}&team2__id__exact={obj.team.id}'
        return format_html(
            '<div style="display: flex; gap: 4px;">'
            '<a href="{}" class="btn btn-sm btn-outline-primary">Team</a>'
            '<a href="{}" class="btn btn-sm btn-outline-info">Matches</a>'
            '</div>',
            team_url, matches_url
        )
    table_actions.short_description = 'Actions'
    
    def get_team_color(self, color_theme):
        colors = {
            'blue': '#3b82f6',
            'yellow': '#eab308',
            'red': '#ef4444',
            'purple': '#8b5cf6',
            'green': '#10b981',
            'orange': '#f97316',
        }
        return colors.get(color_theme, '#6b7280')
    
    # Custom admin actions
    actions = ['recalculate_nrr', 'reset_statistics', 'export_standings']
    
    def recalculate_nrr(self, request, queryset):
        for entry in queryset:
            entry.calculate_nrr()
        self.message_user(request, f'NRR recalculated for {queryset.count()} teams.')
    recalculate_nrr.short_description = "Recalculate NRR for selected teams"
    
    def reset_statistics(self, request, queryset):
        updated = queryset.update(
            matches_played=0, wins=0, losses=0, points=0,
            runs_for=0, runs_against=0, overs_for=0.0, overs_against=0.0, nrr=0.0
        )
        self.message_user(request, f'Statistics reset for {updated} teams.')
    reset_statistics.short_description = "Reset statistics for selected teams"
    
    def export_standings(self, request, queryset):
        # This would implement CSV export functionality
        self.message_user(request, f'Standings export functionality would be implemented for {queryset.count()} teams.')
    export_standings.short_description = "Export standings to CSV"

@admin.register(PlayerMatchPerformance)
class PlayerMatchPerformanceAdmin(admin.ModelAdmin):
    list_display = ('player', 'match', 'team', 'batting_display', 'bowling_display', 'fielding_display')
    list_filter = ('team', 'player__role', 'match__status')
    search_fields = ('player__name', 'team__name', 'match__team1__name', 'match__team2__name')
    ordering = ('-match__date', 'player__name')
    readonly_fields = ('strike_rate', 'economy_rate')
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    fieldsets = (
        ('Match Information', {
            'fields': ('match', 'player', 'team'),
            'classes': ('wide',)
        }),
        ('Batting Performance', {
            'fields': ('runs_scored', 'balls_faced', 'fours', 'sixes', 'strike_rate'),
            'classes': ('wide',)
        }),
        ('Bowling Performance', {
            'fields': ('overs_bowled', 'wickets_taken', 'runs_conceded', 'economy_rate'),
            'classes': ('wide',)
        }),
        ('Fielding Performance', {
            'fields': ('catches_taken', 'stumpings'),
            'classes': ('wide',)
        }),
    )
    
    def batting_display(self, obj):
        if obj.runs_scored > 0:
            return format_html(
                '<span style="color: #059669; font-weight: bold;">{}({})</span>',
                obj.runs_scored, obj.balls_faced
            )
        return format_html('<span style="color: #6b7280;">DNB</span>')
    batting_display.short_description = 'Batting'
    
    def bowling_display(self, obj):
        if obj.overs_bowled > 0:
            return format_html(
                '<span style="color: #dc2626; font-weight: bold;">{}/{} ({})</span>',
                obj.wickets_taken, obj.runs_conceded, obj.overs_bowled
            )
        return format_html('<span style="color: #6b7280;">DNB</span>')
    bowling_display.short_description = 'Bowling'
    
    def fielding_display(self, obj):
        if obj.catches_taken > 0 or obj.stumpings > 0:
            return format_html(
                '<span style="color: #7c3aed; font-weight: bold;">C:{} S:{}</span>',
                obj.catches_taken, obj.stumpings
            )
        return format_html('<span style="color: #6b7280;">-</span>')
    fielding_display.short_description = 'Fielding'

@admin.register(TournamentAwards)
class TournamentAwardsAdmin(admin.ModelAdmin):
    list_display = ('award_type', 'player', 'team', 'value', 'description')
    list_filter = ('award_type', 'player__team')
    search_fields = ('player__name', 'player__team__name')
    ordering = ('award_type', '-value')
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    fieldsets = (
        ('Award Information', {
            'fields': ('award_type', 'player', 'value', 'description'),
            'classes': ('wide',)
        }),
    )
    
    def team(self, obj):
        return obj.player.team.name
    team.short_description = 'Team'

# Customize admin site
admin.site.site_header = "🏏 Gali Premier League Mini Tournament Administration"
admin.site.site_title = "Gali Premier League Admin Portal"
admin.site.index_title = "Welcome to Gali Premier League Mini Tournament Admin"

# Add custom CSS to all admin pages
class CustomAdminSite(admin.AdminSite):
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

# Override the default admin site
admin.site.__class__ = CustomAdminSite
