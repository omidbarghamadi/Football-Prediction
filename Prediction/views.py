from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Team, Match, Prediction, Table
from .serializers import TeamSerializer, MatchSerializer, PredictionSerializer, TableSerializer
from .middleware import update_user_scores, update_predictions, update_matches, get_matches, update_table


class TeamListView(APIView):
    permission_classes = []

    def get(self, request):
        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)


class MatchListView(APIView):
    permission_classes = []

    def get(self, request):
        matches = Match.objects.filter(is_active=True)
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)


class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        is_active = self.request.query_params.get('is_active')

        if is_active:
            return Prediction.objects.filter(user=self.request.user, match__is_active=is_active)

        return Prediction.objects.filter(user=self.request.user)


class TableView(APIView):
    permission_classes = []

    def get(self, request):
        table = Table.objects.all()
        serializer = TableSerializer(table, many=True)
        return Response(serializer.data)


class UpdateView(APIView):
    permission_classes = []

    def get(self, request):
        # get_matches()
        # update_matches()
        update_predictions()
        update_user_scores()
        # update_table()
        return Response("ok")
