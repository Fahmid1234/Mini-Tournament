from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone

class GaliPremierLeagueAdminSite(AdminSite):
    site_header = "🏏 Gali Premier League Mini Tournament Administration"
    site_title = "Gali Premier League Admin Portal"
    index_title = "Welcome to Gali Premier League Mini Tournament Management"
    
    def index(self, request, extra_context=None):
        """
        Custom admin index page with tournament statistics
        """
        from teams.models import Team, Player
        from matches.models import Match, PointsTableEntry
        
        # Get statistics
        total_teams = Team.objects.count()
        total_players = Player.objects.count()
        total_matches = Match.objects.count()
        completed_matches = Match.objects.filter(status='completed').count()
        upcoming_matches = Match.objects.filter(status='scheduled').count()
        
        # Get top teams
        top_teams = PointsTableEntry.objects.all().order_by('-points', '-nrr')[:3]
        
        # Get recent matches
        recent_matches = Match.objects.all().order_by('-date')[:5]
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_teams': total_teams,
            'total_players': total_players,
            'total_matches': total_matches,
            'completed_matches': completed_matches,
            'upcoming_matches': upcoming_matches,
            'top_teams': top_teams,
            'recent_matches': recent_matches,
        })
        
        return super().index(request, extra_context)

# Create custom admin site instance
gali_premier_league_admin_site = GaliPremierLeagueAdminSite(name='gali_premier_league_admin')

# Register models with custom admin site
from teams.models import Team, Player
from matches.models import Match, PointsTableEntry
from teams.admin import TeamAdmin, PlayerAdmin
from matches.admin import MatchAdmin, PointsTableEntryAdmin

gali_premier_league_admin_site.register(Team, TeamAdmin)
gali_premier_league_admin_site.register(Player, PlayerAdmin)
gali_premier_league_admin_site.register(Match, MatchAdmin)
gali_premier_league_admin_site.register(PointsTableEntry, PointsTableEntryAdmin)

# Custom admin actions and utilities
class AdminUtilities:
    """
    Utility functions for admin operations
    """
    
    @staticmethod
    def get_tournament_summary():
        """Get tournament summary statistics"""
        from teams.models import Team, Player
        from matches.models import Match, PointsTableEntry
        
        stats = {
            'teams': Team.objects.count(),
            'players': Player.objects.count(),
            'matches': Match.objects.count(),
            'completed': Match.objects.filter(status='completed').count(),
            'upcoming': Match.objects.filter(status='scheduled').count(),
        }
        
        return stats
    
    @staticmethod
    def get_team_performance():
        """Get team performance summary"""
        from matches.models import PointsTableEntry
        
        return PointsTableEntry.objects.all().order_by('-points', '-nrr')
    
    @staticmethod
    def get_recent_activity():
        """Get recent admin activity"""
        from matches.models import Match
        
        return Match.objects.all().order_by('-date')[:10]

# Custom admin templates and styling
class AdminCustomization:
    """
    Admin interface customization
    """
    
    @staticmethod
    def get_admin_css():
        """Custom CSS for admin interface"""
        return """
        <style>
        .gali-premier-league-admin-header {
            background: linear-gradient(135deg, #1e1b4b 0%, #3730a3 100%);
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .gali-premier-league-stats-card {
            background: white;
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        
        .gali-premier-league-gradient {
            background: linear-gradient(135deg, #1e1b4b 0%, #3730a3 100%);
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #1e1b4b;
        }
        
        .stat-label {
            color: #6b7280;
            font-size: 0.875rem;
        }
        
        .team-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
            color: white;
        }
        
        .match-status {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
        }
        
        .status-completed { background-color: #10b981; color: white; }
        .status-upcoming { background-color: #3b82f6; color: white; }
        </style>
        """
    
    @staticmethod
    def get_admin_js():
        """Custom JavaScript for admin interface"""
        return """
        <script>
        // Auto-refresh tournament statistics
        function refreshStats() {
            // Add auto-refresh functionality here
            console.log('Refreshing tournament statistics...');
        }
        
        // Initialize admin interface
        document.addEventListener('DOMContentLoaded', function() {
            // Add any admin interface enhancements here
            console.log('Gali Premier League Admin interface loaded');
        });
        </script>
        """

# Export the custom admin site
__all__ = ['gali_premier_league_admin_site', 'AdminUtilities', 'AdminCustomization']
