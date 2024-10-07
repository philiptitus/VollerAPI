from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from base.models import *
from base.serializers import *

from rest_framework.pagination import PageNumberPagination


class EnrollCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = kwargs.get('course_id')
        new_course = get_object_or_404(Course, id=course_id)
        
        # Check if the new course is ready for enrollment
        if not new_course.ready:
            return Response({"detail": "Course is not ready for enrollment."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the requesting user
        user = request.user
        current_course = user.course  # The user's currently enrolled course

        # Check if the user is already enrolled in the requested course
        if current_course == new_course:
            return Response({"detail": "You are already enrolled in this course."}, status=status.HTTP_400_BAD_REQUEST)

        # If the user is enrolled in another course, decrease its capacity
        if current_course:
            current_course.capacity = max(0, current_course.capacity - 1)  # Ensure capacity doesn't go below 0
            current_course.save()

        # Enroll the user in the new course
        user.course = new_course
        user.save()

        # Increase the new course capacity by 1
        new_course.capacity += 1
        new_course.save()

        # Create a notification for the user
        notification_message = f"You have successfully enrolled in the course '{new_course.title}'."
        Notification.objects.create(user=user, message=notification_message)

        return Response({"detail": "Successfully enrolled in the course."}, status=status.HTTP_200_OK)
    







class EnrollBasedOnTrendingIssueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        trending_issue_id = kwargs.get('trending_issue_id')
        
        # Fetch the trending issue
        trending_issue = get_object_or_404(TrendingIssue, id=trending_issue_id)
        
        # Check if there is an associated course with the trending issue
        try:
            course = Course.objects.get(issue=trending_issue)
        except Course.DoesNotExist:
            return Response({"detail": "No course found for the given trending issue."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the course is ready for enrollment
        if not course.ready:
            return Response({"detail": "Course is not ready for enrollment."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the requesting user
        user = request.user
        current_course = user.course  # The user's currently enrolled course

        # Check if the user is already enrolled in the course
        if current_course == course:
            return Response({"detail": "You are already enrolled in this course."}, status=status.HTTP_400_BAD_REQUEST)

        # If the user is enrolled in another course, decrease the capacity of the current course
        if current_course:
            current_course.capacity = max(0, current_course.capacity - 1)
            current_course.save()

        # Enroll the user in the new course
        user.course = course
        user.save()

        # Increase the course capacity by 1
        course.capacity += 1
        course.save()

        # Create a notification for the user
        notification_message = f"You have successfully enrolled in the course '{course.title}' for the trending issue '{trending_issue.issue}'."
        Notification.objects.create(user=user, message=notification_message)

        return Response({"detail": "Successfully enrolled in the course based on trending issue."}, status=status.HTTP_200_OK)













class UnenrollCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get the requesting user
        user = request.user
        current_course = user.course  # The user's currently enrolled course

        # Check if the user is enrolled in any course
        if not current_course:
            return Response({"detail": "You are not enrolled in any course."}, status=status.HTTP_400_BAD_REQUEST)

        # Decrease the course capacity by 1, ensuring it doesn't go below 0
        current_course.capacity = max(0, current_course.capacity - 1)
        current_course.save()

        # Set the user's course field to None (unenroll the user)
        user.course = None
        user.save()

        # Create a notification for the user
        notification_message = f"You have successfully unenrolled from the course '{current_course.title}'."
        Notification.objects.create(user=user, message=notification_message)

        return Response({"detail": "Successfully unenrolled from the course."}, status=status.HTTP_200_OK)









class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        course = get_object_or_404(Course, id=id)

        if course.ready == False:
            return Response({'detail': 'Your Course Is Not Ready Yet. Please come back later.'}, status=status.HTTP_409_CONFLICT)

        # Ensure the requesting user is attached to the course
        if course != request.user.course:
            return Response({'detail': 'Not authorized to view this course.'}, status=status.HTTP_403_FORBIDDEN)

        # Serialize the course
        serializer = CourseSerializer(course)
        response_data = serializer.data

        # Fetch and serialize associated objects
        response_data['blocks'] = CourseBlockSerializer(course.blocks.all(), many=True).data
        response_data['google_search_results'] = GoogleSearchResultSerializer(course.searches.all(), many=True).data
        response_data['youtube_links'] = YouTubeLinkSerializer(course.youtube.all(), many=True).data

        # Print the response data to the console
        print(response_data)

        return Response(response_data)









class CourseListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Retrieve all available courses and sort by capacity in descending order
        courses = Course.objects.all().order_by('-capacity')

        # Filter by name if provided in query parameters
        name = request.query_params.get('name')
        if name is not None:
            courses = courses.filter(title__icontains=name)

        # Pagination setup
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of courses per page
        result_page = paginator.paginate_queryset(courses, request)

        # Serialize the paginated courses
        serializer = CourseSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)











class CommentOnFinanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, finance_id, *args, **kwargs):
        # Get the finance object
        finance = get_object_or_404(Finance, id=finance_id)

        # Serialize the comment data
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            # Save the comment with the finance and user fields
            serializer.save(finance=finance, user=request.user)

            # Update the comment count for the finance object
            finance.comment_count = Comment.objects.filter(finance=finance).count()
            finance.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class ReplyToCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, *args, **kwargs):
        # Get the parent comment object
        parent_comment = get_object_or_404(Comment, id=comment_id)

        # Serialize the reply data
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            # Save the reply with the finance, user, and parent fields
            serializer.save(finance=parent_comment.finance, user=request.user, parent=parent_comment)

            # Update the comment count for the finance object
            finance = parent_comment.finance
            finance.comment_count = Comment.objects.filter(finance=finance).count()
            finance.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class DeleteCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id, *args, **kwargs):
        # Get the comment object
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)

        # Ensure the comment belongs to the requesting user
        if comment.user != request.user:
            return Response({"detail": "You do not have permission to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

        # Get the finance object before deleting the comment
        finance = comment.finance

        # Delete the comment
        comment.delete()

        # Update the comment count for the finance object
        finance.comment_count = Comment.objects.filter(finance=finance).count()
        finance.save()

        return Response({"detail": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)








class UpdateCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, comment_id, *args, **kwargs):
        # Get the comment object
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)

        # Ensure the comment belongs to the requesting user
        if comment.user != request.user:
            return Response({"detail": "You do not have permission to update this comment."}, status=status.HTTP_403_FORBIDDEN)

        # Serialize the updated data, ensuring only the content is updated
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            # Save the updated comment
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)










class FinanceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, finance_id, *args, **kwargs):
        # Get the finance object
        finance = get_object_or_404(Finance, id=finance_id)

        # Serialize the finance object
        finance_serializer = FinanceSerializer(finance)

        # Get the associated comments
        comments = Comment.objects.filter(finance=finance, parent=None)  # Get only root-level comments
        comment_serializer = CommentSerializer(comments, many=True)

        # Combine finance data and comments data into a response
        return Response({
            "finance": finance_serializer.data,
            "comments": comment_serializer.data
        }, status=status.HTTP_200_OK)
    













class FinanceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Retrieve all available finance records and sort by comment count in descending order
        finances = Finance.objects.all().order_by('-comment_count')

        # Filter by title if provided in query parameters
        title = request.query_params.get('title')
        if title is not None:
            finances = finances.filter(title__icontains=title)

        # Pagination setup
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of finance records per page
        result_page = paginator.paginate_queryset(finances, request)

        # Serialize the paginated finance records
        serializer = FinanceSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)










class TrendingIssueListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Retrieve all available trending issues and sort by count in descending order
        trending_issues = TrendingIssue.objects.all().order_by('-count')

        # Filter by issue if provided in query parameters
        issue = request.query_params.get('issue')
        if issue is not None:
            trending_issues = trending_issues.filter(issue__icontains=issue)

        # Pagination setup
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of trending issues per page
        result_page = paginator.paginate_queryset(trending_issues, request)

        # Serialize the paginated trending issues
        serializer = TrendingIssueSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)













class TrendingIssueDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, issue_id, *args, **kwargs):
        # Get the trending issue object
        trending_issue = get_object_or_404(TrendingIssue, id=issue_id)

        # Serialize the trending issue object
        serializer = TrendingIssueSerializer(trending_issue)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)













class PredictionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Retrieve all available predictions and sort by count in descending order
        predictions = Prediction.objects.all().order_by('-count')

        # Filter by type if provided in query parameters
        prediction_type = request.query_params.get('type')
        if prediction_type is not None:
            predictions = predictions.filter(type=prediction_type)

        # Pagination setup
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of predictions per page
        result_page = paginator.paginate_queryset(predictions, request)

        # Serialize the paginated predictions
        serializer = PredictionSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)












class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get all unread notifications ordered by timestamp
        notifications = Notification.objects.filter(user=request.user, read=False).order_by('-timestamp')

        # Take the latest 3 unread notifications
        latest_notifications = notifications[:3]

        # If there are exactly 3 notifications, mark them as read (but use the full queryset)
        if len(latest_notifications) == 3:
            notifications.update(read=True)

        # Serialize the notifications
        serializer = NotificationSerializer(latest_notifications, many=True)

        # Paginate the results
        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(latest_notifications, request)

        return paginator.get_paginated_response(serializer.data)







