from rest_framework import serializers
from .models import Team, Match, Prediction, Table


class TeamSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None

    def get_icon(self, obj):
        return obj.icon.url if obj.icon else None

    class Meta:
        model = Team
        fields = ['id', 'name', 'name_en', 'logo', 'icon',]


class MatchSerializer(serializers.ModelSerializer):
    team1 = TeamSerializer()
    team2 = TeamSerializer()

    class Meta:
        model = Match
        fields = ['id', 'team1', 'team2', 'date', 'score_team1', 'score_team2', 'round',]


class PredictionSerializer(serializers.ModelSerializer):
    match_id = serializers.PrimaryKeyRelatedField(
        source='match',
        queryset=Match.objects.all(),
        write_only=True
    )
    match = MatchSerializer(read_only=True)

    class Meta:
        model = Prediction
        fields = ['id', 'match_id', 'match', 'predicted_score_team1', 'predicted_score_team2', 'score']

    def create(self, validated_data):
        user = self.context['request'].user
        match = validated_data['match']

        prediction, created = Prediction.objects.update_or_create(
            user=user,
            match=match,
            defaults={
                'predicted_score_team1': validated_data['predicted_score_team1'],
                'predicted_score_team2': validated_data['predicted_score_team2'],
                'score': validated_data.get('score', 2),
            }
        )
        return prediction


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['rank', 'team', 'points', 'games']

