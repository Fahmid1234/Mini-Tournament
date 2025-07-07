from django.db import models

# Create your models here.

class Team(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='team_logos/')
    color_theme = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Player(models.Model):
    ROLE_CHOICES = [
        ('Batsman', 'Batsman'),
        ('Bowler', 'Bowler'),
        ('All-rounder', 'All-rounder'),
        ('Wicketkeeper', 'Wicketkeeper'),
    ]
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    # Optional: stats = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name
