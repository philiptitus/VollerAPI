from django.urls import path
from .views import *

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('predictions/', PredictionListView.as_view(), name='issue-list'),#CHECK
    path('issues/', TrendingIssueListView.as_view(), name='issue-list'),#CHECK
    path('finances/', FinanceListView.as_view(), name='finance-list'),#CHECK
    path('courses/', CourseListView.as_view(), name='course-list'),#CHECK
    path('courses/unenroll/', UnenrollCourseView.as_view(), name='unenroll-course'),
    path('courses/<int:course_id>/enroll/', EnrollCourseView.as_view(), name='enroll-course'),
    path('courses/trending_issue/<int:trending_issue_id>/', EnrollBasedOnTrendingIssueView.as_view(), name='enroll_trending_issue'),

    path('courses/<int:id>/', CourseDetailView.as_view(), name='preparation-material-detail'),#CHECK
    path('finance/<int:finance_id>/comment/', CommentOnFinanceView.as_view(), name='comment-on-finance'),
    path('comment/<int:comment_id>/reply/', ReplyToCommentView.as_view(), name='reply-to-comment'),
    path('comment/<int:comment_id>/delete/', DeleteCommentView.as_view(), name='delete-comment'),
    path('comment/<int:comment_id>/update/', UpdateCommentView.as_view(), name='update-comment'),
    path('finances/<int:finance_id>/', FinanceDetailView.as_view(), name='finance-detail'),
    path('trending-issue/<int:issue_id>/', TrendingIssueDetailView.as_view(), name='trending-issue-detail'),


]
