from django.urls import path
from .views import *


urlpatterns = [





    path('scrape/', ScrapeInstagramView.as_view(), name='scrape_instagram'),
    path('clean/', CleanInstagramView.as_view(), name='clean_instagram'),
    path('issues/', ProcessEmergingIssuesView.as_view(), name='check_issues'),
    path('reset/', ResetFirstAnalysisView.as_view(), name='check_issues'),
    path('course/', ProcessCourse.as_view(), name='processCourse'),
    # path('generate/', GenerateFactCheckData.as_view(), name='generate_factcheck_data'),
    path('issue-count/', ProcessIssueCountsView.as_view(), name='process_issue_count'),
    path('issue-redundant/', ProcessRedundantIssuesView.as_view(), name='process_issue_count'),
    path('issue-limit/', ProcessTrendingIssuesLimitView.as_view(), name='process_issue_count'),
    path('predictions/', ProcessPredictionsView.as_view(), name='process_predictions'),
    path('clear/', ClearConversationView.as_view(), name='clear_conversation'),
    path('predictions-count/', ProcessPredictionCountsView.as_view(), name='process_predictions_count'),
    path('predictions-redundant/', ProcessRedundantPredictionsView.as_view(), name='process_redundant_predictions'),
    path('predictions-limit/', ProcessPredictionsLimitView.as_view(), name='process_prediction_limit'),
    path('finance/', ProcessFinancePredictionsView.as_view(), name='process_finance'),








]
