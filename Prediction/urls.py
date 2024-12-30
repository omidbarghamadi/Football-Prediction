from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamListView, MatchListView, PredictionViewSet, TableView, UpdateView

router = DefaultRouter()
router.register(r'predictions', PredictionViewSet)

urlpatterns = [
    path('teams/', TeamListView.as_view(), name='team-list'),
    path('matches/', MatchListView.as_view(), name='match-list'),
    path('table/', TableView.as_view(), name='table'),

    path('update/', UpdateView.as_view(), name='table'),
    path('', include(router.urls)),
]
