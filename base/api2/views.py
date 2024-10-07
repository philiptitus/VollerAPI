from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from base.utils import *

from base.models import *
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')
class ScrapeInstagramView(APIView):
    def get(self, request):
        scrape_instagram_accounts()
        return Response({"detail": "Scraping complete."}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class CleanInstagramView(APIView):
    def get(self, request):
        process_posts()
        return Response({"detail": "Cleaning complete."}, status=status.HTTP_200_OK)
    

@method_decorator(csrf_exempt, name='dispatch')
class ProcessEmergingIssuesView(APIView):
    def get(self, request):
        # Process the emerging issues using AI
        process_emerging_issues()

        return Response({"detail": "Processing of emerging issues complete."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class ProcessCourse(APIView):
    def get(self, request):
        # Process the emerging issues using AI
        process_course()

        return Response({"detail": "Processing of course complete."}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class ResetFirstAnalysisView(APIView):
    def get(self, request):
        # Reset the first_analysis field to False for all posts
        reset_first_analysis()

        return Response({"detail": "Reset first_analysis to False for all posts."}, status=status.HTTP_200_OK)
    







# # List of fake questions
# FAKE_QUESTIONS = [
#     "Did Kenya ban the use of smartphones in public spaces last year?",
#     "Was the Kenyan government accused of altering COVID-19 statistics to downplay the pandemic?",
#     "Is it true that Kenya stopped using biometric data for national ID registration?",
#     "Did Kenya ban all foreign-owned businesses in Nairobi?",
#     "Was Nairobi declared the most dangerous city in Africa by the UN in 2023?",
#     "Did the Kenyan government recently make cryptocurrency illegal nationwide?",
#     "Is it true that Kenya’s president canceled all international trade agreements?",
#     "Did Kenya introduce a law making social media usage illegal without a license?",
#     "Was Kenya removed from the East African Community over a trade dispute?",
#     "Did the Kenyan government sell the Port of Mombasa to a foreign country last month?",
#     "Is it true that Kenya banned all forms of cash transactions in favor of mobile money?",
#     "Was Kenya accused of manipulating the results of the 2023 national census?",
#     "Did a new law pass in Kenya that fines citizens for watching foreign news channels?",
#     "Did Kenya implement a curfew for all citizens under 30 years old?",
#     "Was a Kenyan government official found guilty of selling national parks to private investors?",
#     "Did Kenya shut down its public transportation system due to rising fuel costs?",
#     "Is it true that all wildlife in Kenya’s national parks was relocated to another country?",
#     "Did Kenya recently withdraw from the African Union?",
#     "Was a mandatory social credit scoring system introduced in Kenya last year?",
#     "Did the Kenyan government impose a tax on internet usage for all citizens?",
# ]

# class GenerateFactCheckData(APIView):
#     def post(self, request):


#         # Create 20 FactCheck objects
#         for question in FAKE_QUESTIONS:
#             FactCheck.objects.create( submitted_data=question)

#         return Response({"detail": "20 FactCheck entries created successfully."}, status=status.HTTP_201_CREATED)



@method_decorator(csrf_exempt, name='dispatch')
class ProcessIssueCountsView(APIView):
    def get(self, request):
        # Process the issue counts using AI
        process_issue_counts()

        return Response({"detail": "Processing of issue counts complete."}, status=status.HTTP_200_OK)
    





@method_decorator(csrf_exempt, name='dispatch')
class ProcessRedundantIssuesView(APIView):
    def get(self, request):
        # Process the redundant trending issues using AI
        process_redundant_issues()

        return Response({"detail": "Processing of redundant trending issues complete."}, status=status.HTTP_200_OK)
    












@method_decorator(csrf_exempt, name='dispatch')
class ProcessTrendingIssuesLimitView(APIView):
    def get(self, request):
        # Process the trending issues to ensure the maximum limit is maintained
        process_trending_issues_limit()

        return Response({"detail": "Processing of trending issues limit complete."}, status=status.HTTP_200_OK)



@method_decorator(csrf_exempt, name='dispatch')
class ProcessPredictionsView(APIView):
    def get(self, request):
        # Process the predictions using AI
        process_predictions()

        return Response({"detail": "Processing of predictions complete."}, status=status.HTTP_200_OK)





@method_decorator(csrf_exempt, name='dispatch')
class ClearConversationView(APIView):
    """View to clear the conversation thread with the AI and start a new blank conversation."""

    def post(self, request, *args, **kwargs):
        try:
            ai_response = clear_conversation_thread()
            return Response({'status': 'success', 'message': ai_response}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)









@method_decorator(csrf_exempt, name='dispatch')
class ProcessPredictionCountsView(APIView):
    def get(self, request):
        # Process the prediction counts using AI
        process_prediction_counts()

        return Response({"detail": "Processing of prediction counts complete."}, status=status.HTTP_200_OK)















@method_decorator(csrf_exempt, name='dispatch')
class ProcessRedundantPredictionsView(APIView):
    def get(self, request):
        # Process the redundant predictions using AI
        process_redundant_predictions()

        return Response({"detail": "Processing of redundant predictions complete."}, status=status.HTTP_200_OK)
    


















@method_decorator(csrf_exempt, name='dispatch')
class ProcessPredictionsLimitView(APIView):
    def get(self, request):
        # Process the predictions to ensure the maximum limit is maintained
        process_predictions_limit()

        return Response({"detail": "Processing of predictions limit complete."}, status=status.HTTP_200_OK)  











@method_decorator(csrf_exempt, name='dispatch')
class ProcessFinancePredictionsView(APIView):
    def get(self, request):
        # Process the finance predictions using AI
        process_finance_predictions()

        return Response({"detail": "Processing of finance predictions complete."}, status=status.HTTP_200_OK)  