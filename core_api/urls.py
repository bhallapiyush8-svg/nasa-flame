from django.urls import path
from core_api import views

urlpatterns = [
    path('investigations/', views.InvestigationsListView.as_view(), name='api-investigations'),
    path('investigations/<str:inv_id>/', views.InvestigationDetailView.as_view(), name='api-investigation-detail'),
    path('experiments/', views.ExperimentsListView.as_view(), name='api-experiments'),
    path('predict/', views.PredictCombustionView.as_view(), name='api-predict'),
    path('habitats/', views.HabitatsListView.as_view(), name='api-habitats'),
    path('habitats/ranking/', views.HabitatRankingView.as_view(), name='api-habitat-ranking'),
    path('hardware/cir/', views.HardwareSchematicView.as_view(), name='api-hardware-cir'),
    path('spinoffs/', views.SpinoffsListView.as_view(), name='api-spinoffs'),
    path('dataset/download/', views.DatasetDownloadView.as_view(), name='api-download-dataset'),
    path('copilot/query/', views.CopilotQueryView.as_view(), name='api-copilot-query'),
    path('scenario/simulate/', views.EmergencyScenarioSimulateView.as_view(), name='api-scenario-simulate'),
    path('stats/', views.AnalyticsStatsView.as_view(), name='api-stats'),
    path('extractor/sync/', views.NASAExtractorSyncView.as_view(), name='api-extractor-sync'),
    path('extractor/sources/', views.NASAExtractorSourcesView.as_view(), name='api-extractor-sources'),
    path('extractor/upload/', views.NASAExtractorUploadView.as_view(), name='api-extractor-upload'),
]
