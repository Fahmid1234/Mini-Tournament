from django.core.management.base import BaseCommand
from django.utils import timezone
from teams.models import Team, Player
from matches.models import Match, PlayerMatchPerformance, PointsTableEntry
import random

class Command(BaseCommand):
    help = 'Create sample data for the tournament'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create teams if they don't exist
        teams_data = [
            {'name': 'Team A', 'color_theme': 'blue'},
            {'name': 'Team B', 'color_theme': 'red'},
            {'name': 'Team C', 'color_theme': 'green'},
            {'name': 'Team D', 'color_theme': 'purple'},
        ]

        teams = []
        for team_data in teams_data:
            team, created = Team.objects.get_or_create(
                name=team_data['name'],
                defaults={'color_theme': team_data['color_theme']}
            )
            teams.append(team)
            if created:
                self.stdout.write(f'Created team: {team.name}')

        # Create players for each team
        players_per_team = 8
        player_names = [
            'Virat Kohli', 'Rohit Sharma', 'KL Rahul', 'Shikhar Dhawan',
            'Jasprit Bumrah', 'Mohammed Shami', 'Ravindra Jadeja', 'Hardik Pandya',
            'MS Dhoni', 'Rishabh Pant', 'Yuzvendra Chahal', 'Kuldeep Yadav',
            'Bhuvneshwar Kumar', 'Ishant Sharma', 'Ajinkya Rahane', 'Cheteshwar Pujara',
            'Ravichandran Ashwin', 'Washington Sundar', 'Shardul Thakur', 'Axar Patel',
            'Suryakumar Yadav', 'Ishan Kishan', 'Venkatesh Iyer', 'Harshal Patel',
            'Avesh Khan', 'Mohammed Siraj', 'Shreyas Iyer', 'Ruturaj Gaikwad',
            'Devdutt Padikkal', 'Prithvi Shaw', 'Mayank Agarwal', 'Hanuma Vihari'
        ]

        all_players = []
        for team in teams:
            for i in range(players_per_team):
                player_name = f"{player_names.pop(0)} ({team.name})"
                role = random.choice(['Batsman', 'Bowler', 'All-rounder', 'Wicketkeeper'])
                player, created = Player.objects.get_or_create(
                    name=player_name,
                    defaults={'team': team, 'role': role}
                )
                all_players.append(player)
                if created:
                    self.stdout.write(f'Created player: {player.name} ({role})')

        # Create matches
        matches = []
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                match_date = timezone.now() + timezone.timedelta(days=len(matches) * 2)
                match = Match.objects.create(
                    team1=teams[i],
                    team2=teams[j],
                    date=match_date,
                    status='upcoming',
                    overs_per_innings=5
                )
                matches.append(match)

        # Complete some matches with results
        completed_matches = matches[:4]  # Complete first 4 matches
        for match in completed_matches:
            match.status = 'completed'
            match.team1_score = random.randint(40, 80)
            match.team2_score = random.randint(40, 80)
            
            if match.team1_score > match.team2_score:
                match.result = f"{match.team1.name} won by {match.team1_score - match.team2_score} runs"
                player_of_match = random.choice([p for p in all_players if p.team == match.team1])
            else:
                match.result = f"{match.team2.name} won by {match.team2_score - match.team1_score} runs"
                player_of_match = random.choice([p for p in all_players if p.team == match.team2])
            
            match.player_of_match = player_of_match
            match.save()

            # Create player performances for this match
            team1_players = [p for p in all_players if p.team == match.team1]
            team2_players = [p for p in all_players if p.team == match.team2]

            # Team 1 batting performances
            for player in random.sample(team1_players, 6):  # 6 players bat
                runs = random.randint(0, 25)
                balls = random.randint(0, 15) if runs > 0 else 0
                fours = random.randint(0, 3) if runs > 0 else 0
                sixes = random.randint(0, 2) if runs > 0 else 0
                
                PlayerMatchPerformance.objects.create(
                    match=match,
                    player=player,
                    team=match.team1,
                    runs_scored=runs,
                    balls_faced=balls,
                    fours=fours,
                    sixes=sixes
                )

            # Team 2 batting performances
            for player in random.sample(team2_players, 6):  # 6 players bat
                runs = random.randint(0, 25)
                balls = random.randint(0, 15) if runs > 0 else 0
                fours = random.randint(0, 3) if runs > 0 else 0
                sixes = random.randint(0, 2) if runs > 0 else 0
                
                PlayerMatchPerformance.objects.create(
                    match=match,
                    player=player,
                    team=match.team2,
                    runs_scored=runs,
                    balls_faced=balls,
                    fours=fours,
                    sixes=sixes
                )

            # Bowling performances (some players bowl)
            for player in random.sample(team1_players, 4):  # 4 players bowl
                overs = random.uniform(1.0, 5.0)
                wickets = random.randint(0, 3)
                runs_conceded = random.randint(5, 25)
                
                performance, created = PlayerMatchPerformance.objects.get_or_create(
                    match=match,
                    player=player,
                    team=match.team1
                )
                performance.overs_bowled = overs
                performance.wickets_taken = wickets
                performance.runs_conceded = runs_conceded
                performance.save()

            for player in random.sample(team2_players, 4):  # 4 players bowl
                overs = random.uniform(1.0, 5.0)
                wickets = random.randint(0, 3)
                runs_conceded = random.randint(5, 25)
                
                performance, created = PlayerMatchPerformance.objects.get_or_create(
                    match=match,
                    player=player,
                    team=match.team2
                )
                performance.overs_bowled = overs
                performance.wickets_taken = wickets
                performance.runs_conceded = runs_conceded
                performance.save()

        # Update points table
        for match in completed_matches:
            from matches.views import update_points_table
            update_points_table(match)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {len(teams)} teams\n'
                f'- {len(all_players)} players\n'
                f'- {len(matches)} matches (total)\n'
                f'- {len(completed_matches)} completed matches\n'
                f'- Player performances for completed matches'
            )
        ) 