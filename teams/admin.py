from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Team, Player

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_theme', 'player_count', 'logo_display', 'team_actions')
    list_filter = ('color_theme',)
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 20
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'color_theme', 'logo'),
            'classes': ('wide',)
        }),
    )
    
    def player_count(self, obj):
        count = obj.players.count()
        if count == 0:
            return format_html('<span style="color: #ef4444; font-weight: bold;">{}</span>', count)
        elif count < 3:
            return format_html('<span style="color: #f59e0b; font-weight: bold;">{}</span>', count)
        else:
            return format_html('<span style="color: #10b981; font-weight: bold;">{}</span>', count)
    player_count.short_description = 'Players'
    player_count.admin_order_field = 'players__count'
    
    def logo_display(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover; border: 2px solid #e5e7eb;" />', 
                obj.logo.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 18px;">{}</div>', 
            obj.name[:2].upper()
        )
    logo_display.short_description = 'Logo'
    
    def team_actions(self, obj):
        players_url = reverse('admin:teams_player_changelist') + f'?team__id__exact={obj.id}'
        return format_html(
            '<a href="{}" class="btn btn-sm btn-info">View Players</a>',
            players_url
        )
    team_actions.short_description = 'Actions'
    
    # Custom admin actions
    actions = ['duplicate_teams', 'reset_team_colors']
    
    def duplicate_teams(self, request, queryset):
        for team in queryset:
            new_team = Team.objects.create(
                name=f"{team.name} (Copy)",
                color_theme=team.color_theme,
                logo=team.logo
            )
        self.message_user(request, f'{queryset.count()} teams duplicated successfully.')
    duplicate_teams.short_description = "Duplicate selected teams"
    
    def reset_team_colors(self, request, queryset):
        colors = ['blue', 'yellow', 'red', 'purple', 'green', 'orange']
        for i, team in enumerate(queryset):
            team.color_theme = colors[i % len(colors)]
            team.save()
        self.message_user(request, f'Colors reset for {queryset.count()} teams.')
    reset_team_colors.short_description = "Reset team colors"

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'role', 'team_color', 'player_actions')
    list_filter = ('role', 'team', 'team__color_theme')
    search_fields = ('name', 'team__name')
    ordering = ('team__name', 'name')
    list_per_page = 25
    autocomplete_fields = ['team']
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    fieldsets = (
        ('Player Information', {
            'fields': ('name', 'role', 'team'),
            'classes': ('wide',)
        }),
        ('Statistics', {
            'fields': (),
            'classes': ('collapse',),
            'description': 'Player statistics will be displayed here when matches are played.'
        }),
    )
    
    def team_color(self, obj):
        colors = {
            'blue': '#3b82f6',
            'yellow': '#eab308',
            'red': '#ef4444',
            'purple': '#8b5cf6',
            'green': '#10b981',
            'orange': '#f97316',
        }
        color = colors.get(obj.team.color_theme, '#6b7280')
        return format_html(
            '<span style="background: linear-gradient(135deg, {} 0%, {} 100%); color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">{}</span>',
            color, color, obj.team.color_theme.title()
        )
    team_color.short_description = 'Team Theme'
    
    def player_actions(self, obj):
        team_url = reverse('admin:teams_team_change', args=[obj.team.id])
        return format_html(
            '<a href="{}" class="btn btn-sm btn-primary">View Team</a>',
            team_url
        )
    player_actions.short_description = 'Actions'
    
    # Custom admin actions
    actions = ['assign_batsman_role', 'assign_bowler_role', 'assign_all_rounder_role', 'assign_wicketkeeper_role', 'move_players']
    
    def assign_batsman_role(self, request, queryset):
        updated = queryset.update(role='Batsman')
        self.message_user(request, f'{updated} players assigned as Batsman.')
    assign_batsman_role.short_description = "Assign selected players as Batsman"
    
    def assign_bowler_role(self, request, queryset):
        updated = queryset.update(role='Bowler')
        self.message_user(request, f'{updated} players assigned as Bowler.')
    assign_bowler_role.short_description = "Assign selected players as Bowler"
    
    def assign_all_rounder_role(self, request, queryset):
        updated = queryset.update(role='All-rounder')
        self.message_user(request, f'{updated} players assigned as All-rounder.')
    assign_all_rounder_role.short_description = "Assign selected players as All-rounder"
    
    def assign_wicketkeeper_role(self, request, queryset):
        updated = queryset.update(role='Wicketkeeper')
        self.message_user(request, f'{updated} players assigned as Wicketkeeper.')
    assign_wicketkeeper_role.short_description = "Assign selected players as Wicketkeeper"
    
    def move_players(self, request, queryset):
        # This would need a custom form to select target team
        self.message_user(request, 'Player move functionality would be implemented with a custom form.')
    move_players.short_description = "Move players to different team"

# Customize admin site
admin.site.site_header = "🏏 Gali Premier League Mini Tournament Administration"
admin.site.site_title = "Gali Premier League Admin Portal"
admin.site.index_title = "Welcome to Gali Premier League Mini Tournament Admin"
