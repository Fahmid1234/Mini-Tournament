from django.db import models
from teams.models import Team, Player

# Create your models here.

class Match(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('completed', 'Completed'),
    ]
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team1_matches')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team2_matches')
    date = models.DateField()
    result = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    team1_score = models.PositiveIntegerField(null=True, blank=True)
    team2_score = models.PositiveIntegerField(null=True, blank=True)
    # New fields for 5-over format
    overs_per_innings = models.PositiveIntegerField(default=5)
    player_of_match = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='pom_matches')

    def __str__(self):
        return f"{self.team1} vs {self.team2} on {self.date}"

class PlayerMatchPerformance(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='player_performances')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='match_performances')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='player_match_performances')
    
    # Batting stats
    runs_scored = models.PositiveIntegerField(default=0)
    balls_faced = models.PositiveIntegerField(default=0)
    fours = models.PositiveIntegerField(default=0)
    sixes = models.PositiveIntegerField(default=0)
    strike_rate = models.FloatField(default=0.0)
    
    # Bowling stats
    overs_bowled = models.FloatField(default=0.0)
    wickets_taken = models.PositiveIntegerField(default=0)
    runs_conceded = models.PositiveIntegerField(default=0)
    economy_rate = models.FloatField(default=0.0)
    
    # Fielding stats
    catches_taken = models.PositiveIntegerField(default=0)
    stumpings = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['match', 'player']
        verbose_name = "Player Match Performance"
        verbose_name_plural = "Player Match Performances"

    def __str__(self):
        return f"{self.player.name} - {self.runs_scored}({self.balls_faced}) & {self.wickets_taken}/{self.runs_conceded}"

    def save(self, *args, **kwargs):
        # Calculate strike rate
        if self.balls_faced > 0:
            self.strike_rate = (self.runs_scored / self.balls_faced) * 100
        
        # Calculate economy rate
        if self.overs_bowled > 0:
            self.economy_rate = self.runs_conceded / self.overs_bowled
        
        super().save(*args, **kwargs)

class TournamentAwards(models.Model):
    AWARD_TYPES = [
        ('player_of_tournament', 'Player of the Tournament'),
        ('highest_run_scorer', 'Highest Run Scorer'),
        ('highest_wicket_taker', 'Highest Wicket Taker'),
        ('best_batsman', 'Best Batsman'),
        ('best_bowler', 'Best Bowler'),
        ('best_all_rounder', 'Best All-Rounder'),
    ]
    
    award_type = models.CharField(max_length=30, choices=AWARD_TYPES)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='tournament_awards')
    value = models.PositiveIntegerField(default=0)  # runs, wickets, etc.
    description = models.CharField(max_length=200, blank=True)
    
    class Meta:
        unique_together = ['award_type']
        verbose_name = "Tournament Award"
        verbose_name_plural = "Tournament Awards"

    def __str__(self):
        return f"{self.get_award_type_display()}: {self.player.name} ({self.value})"

class PointsTableEntry(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    matches_played = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)
    runs_for = models.PositiveIntegerField(default=0)
    runs_against = models.PositiveIntegerField(default=0)
    overs_for = models.FloatField(default=0.0)
    overs_against = models.FloatField(default=0.0)
    nrr = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.team.name} - {self.points} pts (NRR: {self.nrr:.3f})"

    def calculate_nrr(self):
        """Calculate Net Run Rate"""
        if self.overs_for > 0 and self.overs_against > 0:
            run_rate_for = self.runs_for / self.overs_for
            run_rate_against = self.runs_against / self.overs_against
            self.nrr = run_rate_for - run_rate_against
        else:
            self.nrr = 0.0
        self.save()
