from django.core.management.base import BaseCommand
from django.db.models import Sum
from matches.models import PlayerMatchPerformance, TournamentAwards
from teams.models import Player

class Command(BaseCommand):
    help = 'Calculate and update tournament awards based on player performances'

    def handle(self, *args, **options):
        self.stdout.write('Calculating tournament awards...')

        # Calculate highest run scorer
        top_batsman = PlayerMatchPerformance.objects.values(
            'player__name', 'player__team__name'
        ).annotate(
            total_runs=Sum('runs_scored')
        ).filter(total_runs__gt=0).order_by('-total_runs').first()

        if top_batsman:
            player = Player.objects.get(name=top_batsman['player__name'])
            award, created = TournamentAwards.objects.get_or_create(
                award_type='highest_run_scorer',
                defaults={
                    'player': player,
                    'value': top_batsman['total_runs'],
                    'description': f"Highest run scorer with {top_batsman['total_runs']} runs"
                }
            )
            if not created:
                award.player = player
                award.value = top_batsman['total_runs']
                award.description = f"Highest run scorer with {top_batsman['total_runs']} runs"
                award.save()
            
            self.stdout.write(f'Highest Run Scorer: {player.name} ({top_batsman["total_runs"]} runs)')

        # Calculate highest wicket taker
        top_bowler = PlayerMatchPerformance.objects.values(
            'player__name', 'player__team__name'
        ).annotate(
            total_wickets=Sum('wickets_taken')
        ).filter(total_wickets__gt=0).order_by('-total_wickets').first()

        if top_bowler:
            player = Player.objects.get(name=top_bowler['player__name'])
            award, created = TournamentAwards.objects.get_or_create(
                award_type='highest_wicket_taker',
                defaults={
                    'player': player,
                    'value': top_bowler['total_wickets'],
                    'description': f"Highest wicket taker with {top_bowler['total_wickets']} wickets"
                }
            )
            if not created:
                award.player = player
                award.value = top_bowler['total_wickets']
                award.description = f"Highest wicket taker with {top_bowler['total_wickets']} wickets"
                award.save()
            
            self.stdout.write(f'Highest Wicket Taker: {player.name} ({top_bowler["total_wickets"]} wickets)')

        # Calculate Player of the Tournament
        if top_batsman and top_bowler:
            batsman_score = top_batsman['total_runs']
            bowler_score = top_bowler['total_wickets'] * 25  # Simple scoring system
            
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
            
            self.stdout.write(f'Player of the Tournament: {player_of_tournament.name} (Score: {score})')

        self.stdout.write(
            self.style.SUCCESS('Tournament awards calculated successfully!')
        ) 