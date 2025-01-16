from django.db import models
from Account.models import CustomUser


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100)
    logo = models.FileField(upload_to='logos/')
    icon = models.FileField(upload_to='logos/')
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    city = models.CharField(max_length=100)

    class Meta:
        db_table = 'Team'
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self):
        return self.name


class Match(models.Model):
    team1 = models.ForeignKey(Team, related_name='team1_matches', on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='team2_matches', on_delete=models.CASCADE)
    date = models.CharField(max_length=50)
    score_team1 = models.PositiveSmallIntegerField(null=True, blank=True)
    score_team2 = models.PositiveSmallIntegerField(null=True, blank=True)
    round = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Match'
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name} on {self.date}"


class Prediction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, related_name='predictions', on_delete=models.CASCADE)
    predicted_score_team1 = models.PositiveSmallIntegerField()
    predicted_score_team2 = models.PositiveSmallIntegerField()
    score = models.PositiveSmallIntegerField(default=2)

    class Meta:
        db_table = 'Prediction'
        verbose_name = "Prediction"
        verbose_name_plural = "Predictions"

    def __str__(self):
        return f"{self.user.username}'s prediction for {self.match} scored {self.score}"


class Table(models.Model):
    rank = models.PositiveSmallIntegerField()
    team = models.CharField(max_length=40)
    points = models.PositiveSmallIntegerField()
    games = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'Table'
        verbose_name_plural = "Table"
        verbose_name = "Table"
