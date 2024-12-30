from django.contrib import admin
from .models import Team, Match, Prediction


class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'name_en', 'city', 'founded_year']
    search_fields = ['name', 'name_en']
    list_filter = ['city']


class MatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'team1', 'team2', 'date', 'round', 'score_team1', 'score_team2', 'created_at']
    search_fields = ['team1__name', 'team2__name']
    list_filter = ['round']


class PredictionAdmin(admin.ModelAdmin):
    list_display = ['user', 'match', 'predicted_score_team1', 'predicted_score_team2', 'score']
    search_fields = ['user__username', 'match__team1__name', 'match__team2__name']
    list_filter = ['score']


admin.site.register(Team, TeamAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Prediction, PredictionAdmin)