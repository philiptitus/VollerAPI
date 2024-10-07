
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.utils.html import strip_tags
from django.conf import settings
# utils.py
import httpx
from urllib.parse import quote
import jmespath
from typing import Dict
import json
import time
from django.db import IntegrityError
from .models import InstagramData





from googleapiclient.discovery import build
from django.conf import settings








def get_youtube_links(search_query, max_results=3):
    api_key = settings.YOUTUBE_API_KEY  # Replace with your YouTube Data API key
    youtube = build("youtube", "v3", developerKey=api_key)

    # Search for videos matching the query
    search_response = youtube.search().list(
        q=search_query,
        part="id,snippet",
        maxResults=max_results,
        type="video"
    ).execute()

    video_links = []
    for item in search_response.get("items", []):
        video_id = item["id"]["videoId"]
        video_title = item["snippet"]["title"]
        video_url = f"https://www.youtube.com/embed/{video_id}"
        video_links.append((video_title, video_url))

    return video_links








from googleapiclient.discovery import build
from django.conf import settings













def search_google(query):
    # Configure the API key and the Custom Search Engine ID
    api_key = settings.GOOGLE_SEARCH_API_KEY
    cse_id = settings.GOOGLE_CUSTOM_SEARCH_ENGINE_ID

    # Build the service
    service = build("customsearch", "v1", developerKey=api_key)

    # Perform the search
    res = service.cse().list(q=query, cx=cse_id).execute()

    # Extract the search results
    search_items = res.get("items", [])

    # Format the search results
    results = []
    for item in search_items:
        result = {
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "link": item.get("link")
        }
        results.append(result)

    return results




















def send_normal_email(data):
    # Load and render the template with context
    template = Template(data['email_body'])
    context = Context(data.get('context', {}))
    html_content = template.render(context)
    text_content = strip_tags(html_content)  # Fallback text content

    # Create email message
    email = EmailMultiAlternatives(
        subject=data['email_subject'],
        body=html_content,  # Plain text content for email clients that don't support HTML
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']],
    )
    email.attach_alternative(html_content, "text/html")  # Attach the HTML version

    # Send email
    email.send()


















import time
import json
from typing import Dict, List
import httpx
import jmespath
from urllib.parse import quote
from django.db import IntegrityError
from django.utils import timezone
from .models import InstagramData  # Assuming InstagramData is your Django model

def parse_post(data: Dict) -> Dict:
    print(f"parsing post data {data['shortcode']}")
    result = jmespath.search("""{
        id: id,
        captions: edge_media_to_caption.edges[].node.text
    }""", data)
    return result

def scrape_user_posts(user_id: str, session: httpx.Client, max_posts: int = 300, max_pages: int = 30):
    base_url = "https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables="
    variables = {
        "id": user_id,
        "first": 12,  # Increase the page size to reduce the number of requests
        "after": None,
    }
    _page_number = 1
    _post_count = 0

    while True:
        resp = session.get(base_url + quote(json.dumps(variables)))
        data = resp.json()
        if 'data' not in data:
            print(f"Error: No data found for user_id {user_id}")
            break
        posts = data["data"]["user"]["edge_owner_to_timeline_media"]
        for post in posts["edges"]:
            yield parse_post(post["node"])
            _post_count += 1
            if _post_count >= max_posts:
                print(f"Scraped {max_posts} posts, stopping.")
                return
        page_info = posts["page_info"]
        if _page_number == 1:
            print(f"scraping total {posts['count']} posts of {user_id}")
        else:
            print(f"scraping page {_page_number}")
        if not page_info["has_next_page"]:
            break
        if variables["after"] == page_info["end_cursor"]:
            break
        variables["after"] = page_info["end_cursor"]
        _page_number += 1
        if _page_number > max_pages:
            print(f"Scraped {max_pages} pages, stopping.")
            break

def scrape_user(username: str):
    """Scrape Instagram user's data"""
    client = httpx.Client(
        headers={
            "x-ig-app-id": "936619743392459",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
        }
    )
    result = client.get(
        f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
    )
    data = json.loads(result.content)
    return data["data"]["user"]

def scrape_instagram_accounts():
    accounts = [
        ("tuko.co.ke", "00:00"),
        ("nairobi_gossip_club", "01:30"),
        ("citizentvkenya", "03:00"),
        ("ntvkenya", "04:30"),
        ("k24tv", "06:00"),
        ("standardkenya", "07:30"),
        ("ntvkenya", "09:00"),
        ("ktnnews", "10:30"),
        ("thestarkenya", "12:00"),
        ("mpashogram", "13:30"),
        ("larrymadowo", "15:00"),
        ("nation", "16:30"),
        ("thekenyatimes", "18:00"),
        ("thenairobireport", "19:30"),
        ("kenya.gossip.club", "21:00"),
        ("nairobi.leo", "22:30")
    ]

    current_time = timezone.now().time()
    closest_account = min(accounts, key=lambda x: abs((timezone.datetime.combine(timezone.now(), timezone.datetime.strptime(x[1], "%H:%M").time()) - timezone.datetime.combine(timezone.now(), current_time)).total_seconds()))

    account, scheduled_time = closest_account
    print(f"Scraping account: {account} at scheduled time: {scheduled_time}")

    with httpx.Client(timeout=httpx.Timeout(20.0)) as session:
        user_id = scrape_user(account)['id']
        posts = list(scrape_user_posts(user_id, session))
        for post in posts:
            post_id = post['id']
            captions = post['captions']
            for caption in captions:
                InstagramData.objects.get_or_create(special_id=post_id, defaults={'caption': caption})
        print(f"Finished scraping account: {account}")

# Example usage: call the scrape_instagram_accounts function
# scrape_instagram_accounts()




























# CLEAN GRAPH API DATA
# CLEAN GRAPH API DATA
import time
import json
from typing import List, Dict
from django.db import IntegrityError
import google.generativeai as genai  # Import the generative AI module
from django.conf import settings
from .models import InstagramData

def fetch_unapproved_posts(limit: int = 55) -> List[Dict]:
    """Fetch the latest unapproved posts from the database."""
    unapproved_posts = InstagramData.objects.filter(approved=False).order_by('-timestamp')[:limit]
    return [{'special_id': post.special_id, 'caption': post.caption} for post in unapproved_posts]

def cleaner_ai(posts: List[Dict]) -> List[str]:
    """Send the posts to the AI for evaluation and return the list of special_ids to delete."""

    # Format the data as expected by the AI model
    formatted_data = [
        {
            'parts': [
                {
                    'text': f"Special ID: {post['special_id']}\nCaption: {post['caption']}"
                }
            ]
        }
        for post in posts
    ]

    prompt = (
        "I have the following data entries that were retrieved from a news api. The goal is to filter out irrelevant information and retain only the data that aligns with the following criteria:\n\n"
        "Data related to emerging issues or major problems, especially trending societal, environmental, economic, or political concerns.\n"
        "Predictions or patterns suggesting future events such as potential crises, natural disasters, or positive outcomes like improvements in crop yield or local infrastructure.\n"
        "Information that can be used to update educational content or enrich virtual classrooms with relevant, up-to-date trends.\n\n"
        "The data should be free of redundancy, and any old or irrelevant information must be excluded.\n\n"
        "Return the special_ids that need to be deleted in a list eg if we found 2 to be deleted return [ 3450435094765006949, 3450495121273903511 ].\n"
        "Don't return any extra information, I just need a list like that as your response. If you found nothing, return an empty list.\n\n"
        f"Data: {json.dumps(formatted_data, indent=2)}"
    )

    model = genai.GenerativeModel('gemini-1.0-pro-latest')  # Use the Generative AI model
    response = model.generate_content(prompt)
    if not hasattr(response, '_result'):
        raise Exception('Error generating AI response.')

    content = response._result.candidates[0].content.parts[0].text.strip()
    try:
        special_ids_to_delete = json.loads(content)
        if not isinstance(special_ids_to_delete, list):
            raise ValueError("AI response is not a list.")
        return special_ids_to_delete
    except json.JSONDecodeError:
        raise Exception('Error decoding AI response.')

def process_posts():
    """Process the posts using the AI and update the database accordingly."""
    genai.configure(api_key=settings.GOOGLE_API_KEY)  # Configure with your Google API key

    max_iterations = 5
    iteration_count = 0

    while iteration_count < max_iterations:
        print(f"Starting iteration {iteration_count + 1}...")
        print("CLEANING DATA")
        # Fetch the latest unapproved posts
        unapproved_posts = fetch_unapproved_posts()
        if not unapproved_posts:
            print("No unapproved posts found. Exiting.")
            break

        print(f"Fetched {len(unapproved_posts)} unapproved posts.")

        # Send the posts to the AI for evaluation
        special_ids_to_delete = cleaner_ai(unapproved_posts)
        print(f"AI response: {special_ids_to_delete}")

        # Delete the irrelevant posts and mark the remaining as approved
        for special_id in special_ids_to_delete:
            InstagramData.objects.filter(special_id=special_id).delete()
            print(f"Deleted post with special_id: {special_id}")

        remaining_posts = InstagramData.objects.filter(special_id__in=[post['special_id'] for post in unapproved_posts])
        remaining_posts.update(approved=True)
        print(f"Marked {remaining_posts.count()} posts as approved.")

        iteration_count += 1
        if iteration_count < max_iterations:
            print(f"Waiting for 1 minute before the next iteration...")
            time.sleep(10)

    print("Processing completed.")




























import json
import time
from typing import List, Dict
from django.conf import settings
import google.generativeai as genai
from .models import *

# CHECK EMERGING ISSUES

def fetch_approved_posts(limit: int = 20) -> List[Dict]:
    """Fetch the latest approved posts that have not been analyzed from the database."""
    approved_posts = InstagramData.objects.filter(approved=True, first_analysis=False).order_by('-timestamp')[:limit]
    return [{'special_id': post.special_id, 'caption': post.caption} for post in approved_posts]

def format_for_ai(posts: List[Dict]) -> List[Dict]:
    """Format the posts for the AI model with expected keys."""
    formatted_posts = []
    for post in posts:
        formatted_posts.append({
            "parts": [{"text": post['caption']}],
            "special_id": post['special_id']
        })
    return formatted_posts

def issues_ai(posts: List[Dict]) -> List[Dict]:
    """Send the posts to the AI for analysis and return the list of emerging issues."""
    formatted_posts = format_for_ai(posts)

    prompt = (
        "Analyze the data provided from Instagram and identify any emerging issues. For each emerging issue found, return a title, description, and location (if available). "
        "In the description, explain why this issue is considered emerging, referencing specific data points that led to this conclusion. "
        "You can return anywhere from zero issues (if no issues are found) to a maximum of five emerging issues at a time. "
        "The description should be a detailed one."
        "Reference The Post id(s) that made you make a certain analysis in the description always"
        "The format you return your data should be like this: "
        "[{'issue': 'landslide', 'location': 'none', 'description': '............more description'}, "
        "{'issue': 'Wild Fires', 'location': 'Nairobi', 'description': '............more description'}]"
        "STICK TO THAT RESPONSE FORMAT NO EXTRA WORDS."
        "STRICTLY JSON FORMAT ONLY!!!!!"
        f"\n\nData: {json.dumps(formatted_posts, indent=2)}"
    )

    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    response = model.generate_content(prompt)
    if not hasattr(response, '_result'):
        raise Exception('Error generating AI response.')

    content = response._result.candidates[0].content.parts[0].text.strip()
    print(f"AI raw response: {content}")

    if content.lower() == "there are currently no emerging issues or concerns in the data you have provided.":
        print("No emerging issues found.")
        return []

    content = content.replace("'", '"')

    try:
        emerging_issues = json.loads(content)
        return emerging_issues
    except json.JSONDecodeError:
        raise Exception('Error decoding AI response.')

def save_emerging_issues(issues: List[Dict]):
    """Save the emerging issues to the TrendingIssue model."""
    for issue_data in issues:
        issue = issue_data.get('issue')
        location = issue_data.get('location', 'none')
        description = issue_data.get('description')

        trending_issue, created = TrendingIssue.objects.get_or_create(
            issue=issue,
            location=location,
            defaults={'description': description}
        )

        if not created:
            trending_issue.count += 1
            trending_issue.description = description
            trending_issue.save()

        print(f"Saved issue: {issue} at location: {location}")

def mark_posts_as_analyzed(posts: List[Dict]):
    """Mark the posts as analyzed."""
    special_ids = [post['special_id'] for post in posts]
    InstagramData.objects.filter(special_id__in=special_ids).update(first_analysis=True)
    print(f"Marked {len(special_ids)} posts as analyzed.")

def process_emerging_issues():
    """Process the approved posts using the AI and save the emerging issues."""
    genai.configure(api_key=settings.GOOGLE_API_KEY)

    max_iterations = 3
    iteration_count = 0

    while iteration_count < max_iterations:
        print(f"Starting iteration {iteration_count + 1}...")

        approved_posts = fetch_approved_posts()
        if not approved_posts:
            print("No approved posts found that have not been analyzed. Exiting.")
            break

        print(f"Fetched {len(approved_posts)} approved posts that have not been analyzed.")

        try:
            emerging_issues = issues_ai(approved_posts)
            print(f"AI response: {emerging_issues}")

            if emerging_issues:
                save_emerging_issues(emerging_issues)

            mark_posts_as_analyzed(approved_posts)

        except Exception as e:
            print(f"Error processing emerging issues: {e}. Moving to the next iteration.")

        iteration_count += 1
        if iteration_count < max_iterations:
            print(f"Waiting for 1 minute before the next iteration...")
            time.sleep(10)

    print("Processing completed.")

















def reset_first_analysis():
    """Reset the first_analysis field to False for all posts."""
    InstagramData.objects.filter(f_analysis=True).update(first_analysis=False)
    print("Reset first_analysis to False for all posts.")



































##CREATE COURSES
import json
import time
from typing import List, Dict
from django.conf import settings
from .models import TrendingIssue, Course, CourseBlock, GoogleSearchResult, YouTubeLink

def fetch_emerging_issues(limit: int = 5) -> List[Dict]:
    """Fetch the latest emerging issues that have not been processed."""
    emerging_issues = TrendingIssue.objects.filter(processed=False).order_by('-last_updated')[:limit]
    return [{'issue_id': issue.id, 'issue': issue.issue, 'description': issue.description, 'location': issue.location} for issue in emerging_issues]

def course_ai(prompt: str) -> str:
    """Send the prompt to the AI for analysis and return the response."""
    model = genai.GenerativeModel('gemini-1.0-pro-latest')  # Use the Generative AI model
    response = model.generate_content(prompt)
    if not hasattr(response, '_result'):
        raise Exception('Error generating AI response.')

    content = response._result.candidates[0].content.parts[0].text.strip()
    print(f"AI raw response: {content}")  # Print the raw AI response for debugging

    # Replace single quotes with double quotes to make it valid JSON
    content = content.replace("'", '"')

    return content

def create_course_content(issue_data: Dict):
    """Create course content based on the emerging issue."""
    issue_id = issue_data.get('issue_id')
    issue = issue_data.get('issue')
    description = issue_data.get('description')
    location = issue_data.get('location')

    # Check if a course already exists for this issue
    existing_course = Course.objects.filter(issue_id=issue_id).first()
    if existing_course:
        print(f"Course already exists for issue: {issue_id}")
        return

    # Create a Course instance
    course = Course.objects.create(
        issue_id=issue_id,
        title=f"Course for {issue}",
        description=description
    )

    # Prompt 3
    prompt3 = f"{issue} in {location}"

    youtube_links = get_youtube_links(prompt3)
    for yt_title, embed_url in youtube_links:
        YouTubeLink.objects.create(
            preparation_material=course,
            title=yt_title,
            embed_url=embed_url
        )

    search_results = search_google(prompt3)
    for result in search_results:
        GoogleSearchResult.objects.create(
            course=course,
            title=result['title'],
            snippet=result['snippet'],
            link=result['link']
        )

    # Prompt 4
    prompt4 = f"Based on this {description}, provide a set of questions and their answers at least ten of them to help in making a course on how citizens can combat this issue. Note The answer part should be very very detailed and start with the word Answer and the question should always have a question mark. write a question along with its answer at a time."
    content4 = course_ai(prompt4)

    # Extract questions and answers from content4
    lines = content4.split('\n')
    questions_and_answers = []
    question = None
    answer = None

    for line in lines:
        if '?' in line.strip().lower():
            if question and answer:
                questions_and_answers.append((question, answer))
                answer = None
            question = line.strip()
        elif 'answer' in line.strip().lower():
            answer = line.strip()
        elif answer is not None:
            answer += ' ' + line.strip()

    if question and answer:
        questions_and_answers.append((question, answer))

    for q, a in questions_and_answers:
        CourseBlock.objects.create(
            course=course,
            question=q,
            answer=a,
            score=0
        )

    course.ready = True
    course.save()
    print(f"Course created for issue: {issue_id}")

    # Mark the issue as processed
    TrendingIssue.objects.filter(id=issue_id).update(processed=True)

def process_course():
    """Process the emerging issues and create course content."""
    genai.configure(api_key=settings.GOOGLE_API_KEY)  # Configure with your Google API key

    max_iterations = 5
    iteration_count = 0

    while iteration_count < max_iterations:
        print(f"Starting iteration {iteration_count + 1}...")

        # Fetch the latest emerging issues that have not been processed
        emerging_issues = fetch_emerging_issues()
        if not emerging_issues:
            print("No emerging issues found that have not been processed. Exiting.")
            break

        print(f"Fetched {len(emerging_issues)} emerging issues that have not been processed.")

        # Process each emerging issue
        for issue_data in emerging_issues:
            create_course_content(issue_data)
            iteration_count += 1
            if iteration_count < max_iterations:
                print(f"Waiting for 30 seconds before the next iteration...")
                time.sleep(20)

    print("Processing completed.")
































##UPDATE EMERGING ISSUES COUNT

import json
import time
from typing import List, Dict
from django.conf import settings
from base.models import InstagramData, TrendingIssue

def fetch_analyzed_posts(limit: int = 20) -> List[Dict]:
    """Fetch the latest posts that have undergone the first analysis but not the second analysis from the database."""
    analyzed_posts = InstagramData.objects.filter(first_analysis=True, second_analysis=False).order_by('-timestamp')[:limit]
    return [{'special_id': post.special_id, 'caption': post.caption} for post in analyzed_posts]

def send_to_ai_for_counting(posts: List[Dict], issues: List[Dict]) -> List[Dict]:
    """Send the posts to the AI for counting occurrences of each trending issue and return the counts."""
    prompt = (
        "Analyze the data provided from Instagram and count the occurrences of each trending issue based on the following list of issues. "
        "For each issue, return the issue ID and the count of occurrences. "
        "The format you return your data should be like this: "
        "[{'issue_id': 1, 'count': 2}, {'issue_id': 2, 'count': 3}]"
        "STICK TO THAT RESPONSE FORMAT NO EXTRA WORDS"
        f"\n\nData: {json.dumps(posts, indent=2)}"
        f"\n\nIssues: {json.dumps(issues, indent=2)}"
    )

    model = genai.GenerativeModel('gemini-1.0-pro-latest')  # Use the Generative AI model
    response = model.generate_content(prompt)
    if not hasattr(response, '_result'):
        raise Exception('Error generating AI response.')

    content = response._result.candidates[0].content.parts[0].text.strip()
    print(f"AI raw response: {content}")  # Print the raw AI response for debugging

    # Replace single quotes with double quotes to make it valid JSON
    content = content.replace("'", '"')

    try:
        # Parse the response based on the pattern
        issue_counts = json.loads(content)
        if not isinstance(issue_counts, list):
            raise ValueError("AI response is not a list")
        return issue_counts
    except (json.JSONDecodeError, ValueError):
        print("AI response could not be parsed. Assuming no issues were detected.")
        return []

def update_issue_counts(issue_counts: List[Dict]):
    """Update the counts of trending issues in the database."""
    for issue_data in issue_counts:
        issue_id = issue_data.get('issue_id')
        count = issue_data.get('count')

        trending_issue = TrendingIssue.objects.get(id=issue_id)
        trending_issue.count += count
        trending_issue.save()

        print(f"Updated issue ID: {issue_id} with count: {count}")

def mark_posts_as_second_analyzed(posts: List[Dict]):
    """Mark the posts as having undergone the second analysis."""
    special_ids = [post['special_id'] for post in posts]
    InstagramData.objects.filter(special_id__in=special_ids).update(second_analysis=True)
    print(f"Marked {len(special_ids)} posts as having undergone the second analysis.")

def process_issue_counts():
    """Process the posts using the AI to count occurrences of trending issues and update the counts."""
    genai.configure(api_key=settings.GOOGLE_API_KEY)  # Configure with your Google API key

    max_iterations = 3
    iteration_count = 0

    while iteration_count < max_iterations:
        print(f"Starting iteration {iteration_count + 1}...")

        # Fetch the latest posts that have undergone the first analysis but not the second analysis
        analyzed_posts = fetch_analyzed_posts()
        if not analyzed_posts:
            print("No posts found that have undergone the first analysis but not the second analysis. Exiting.")
            break

        print(f"Fetched {len(analyzed_posts)} posts that have undergone the first analysis but not the second analysis.")

        # Fetch all trending issues
        issues = list(TrendingIssue.objects.values('id', 'issue', 'location'))

        # Send the posts to the AI for counting occurrences of each trending issue
        issue_counts = send_to_ai_for_counting(analyzed_posts, issues)
        print(f"AI response: {issue_counts}")

        # Update the counts of trending issues in the database
        if issue_counts:
            update_issue_counts(issue_counts)

        # Mark the posts as having undergone the second analysis
        mark_posts_as_second_analyzed(analyzed_posts)

        iteration_count += 1
        if iteration_count < max_iterations:
            print(f"Waiting for 1 minute before the next iteration...")
            time.sleep(10)

    print("Processing completed.")


















































##REMOVE REDUNDANT DATA FOR ISSUES
import json
from typing import List, Dict
from django.conf import settings


def fetch_all_trending_issues() -> List[Dict]:
    """Fetch all trending issues from the database."""
    trending_issues = TrendingIssue.objects.all().values('id', 'issue', 'location', 'description', 'count')
    return list(trending_issues)

def send_to_ai_for_redundancy(issues: List[Dict]) -> List[Dict]:
    """Send the trending issues to the AI for identifying redundant issues and return the list of redundant issue IDs."""
    prompt = (
        "Analyze the trending issues provided and identify any redundant issues. For each set of redundant issues, return the IDs of the issues that are considered redundant. "
        "The format you return your data should be like this: "
        "[{'redundant_ids': [2, 3]}, {'redundant_ids': [4, 5, 6]}]"
        "STICK TO THAT RESPONSE FORMAT NO EXTRA WORDS"
        f"\n\nIssues: {json.dumps(issues, indent=2)}"
    )

    model = genai.GenerativeModel('gemini-1.0-pro-latest')  # Use the Generative AI model
    response = model.generate_content(prompt)
    if not hasattr(response, '_result'):
        raise Exception('Error generating AI response.')

    content = response._result.candidates[0].content.parts[0].text.strip()
    print(f"AI raw response: {content}")  # Print the raw AI response for debugging

    # Replace single quotes with double quotes to make it valid JSON
    content = content.replace("'", '"')

    try:
        # Parse the response based on the pattern
        redundant_issues = json.loads(content)
        return redundant_issues
    except json.JSONDecodeError:
        raise Exception('Error decoding AI response.')

def remove_redundant_issues(redundant_issues: List[Dict]):
    """Remove the redundant trending issues while keeping the one with the highest count."""
    for redundant_set in redundant_issues:
        redundant_ids = redundant_set.get('redundant_ids', [])
        if not redundant_ids:
            continue

        # Fetch the issues with the given IDs
        issues = TrendingIssue.objects.filter(id__in=redundant_ids)

        # Find the issue with the highest count
        highest_count_issue = max(issues, key=lambda issue: issue.count)

        # Remove the other issues
        for issue in issues:
            if issue.id != highest_count_issue.id:
                issue.delete()

        print(f"Removed redundant issues: {redundant_ids}, kept issue ID: {highest_count_issue.id}")

def process_redundant_issues():
    """Process the trending issues using the AI to identify and remove redundant issues."""
    genai.configure(api_key=settings.GOOGLE_API_KEY)  # Configure with your Google API key

    # Fetch all trending issues
    trending_issues = fetch_all_trending_issues()
    print(f"Fetched {len(trending_issues)} trending issues.")

    # Send the trending issues to the AI for identifying redundant issues
    redundant_issues = send_to_ai_for_redundancy(trending_issues)
    print(f"AI response: {redundant_issues}")

    # Remove the redundant trending issues
    remove_redundant_issues(redundant_issues)

    print("Processing completed.")




























##ELIMINATE ISSUES BELOW 30
def ensure_max_trending_issues(max_limit: int = 30):
    """Ensure that the number of trending issues does not exceed the maximum limit."""
    trending_issues = TrendingIssue.objects.all().order_by('-count')

    if trending_issues.count() > max_limit:
        # Calculate the number of issues to remove
        num_to_remove = trending_issues.count() - max_limit

        # Get the issues with the lowest counts
        issues_to_remove = trending_issues[max_limit:]

        # Remove the issues with the lowest counts
        for issue in issues_to_remove:
            issue.delete()

        print(f"Removed {num_to_remove} trending issues to maintain the limit of {max_limit}.")
    else:
        print(f"The number of trending issues ({trending_issues.count()}) is within the limit of {max_limit}.")

def process_trending_issues_limit():
    """Process the trending issues to ensure the maximum limit is maintained."""
    ensure_max_trending_issues()
    print("Processing completed.")
















##MAKE PREDICTIONS



def fetch_approved_posts_for_prediction(limit: int = 25) -> List[Dict]:
    """Fetch the latest approved posts that have not been analyzed for predictions from the database."""
    approved_posts = InstagramData.objects.filter(approved=True, p_analysis=False).order_by('-timestamp')[:limit]
    return [{'special_id': post.special_id, 'caption': post.caption} for post in approved_posts]

def send_to_ai_for_prediction(posts: List[Dict]) -> List[Dict]:
    """Send the posts to the AI for prediction and return the list of predictions."""
    prompt = (
        "Analyze the data provided from Instagram and make predictions on what may happen based on the data e.g there is likely to be Fire in future "
        "I just need you to make future predictions you think may happen so if you dont have any valid prediction its ok"
        "For each prediction, return a title, description, location (if available), and type. "
        "The type should be one of the following: job_shortage, civil_unrest, economic_crisis, climate_risk, misinformation, mental_health, human_rights, youth_unemployment, general. "
        "For you to make a prediction there must be at least 2 datas that support it"
        "In the description, explain why this prediction is made, referencing specific data points that led to this conclusion. "
        "You can return anywhere from zero predictions (if no predictions are made) to a maximum of three predictions at a time. "
        "The description should be a detailed one. "
        "Your Title should clearly indicate what you predict is going to happen"
        "So I dont want you to just identify issues rather predict what you think may hapen in future based on data"
        "The format you return your data should be like this: "
        "YOU CANT MAKE PREDICTIONS BASED ON JUST ONE OCCURENCE E.G THERE HAS TO BE MANY OCCURENCES OF PEOPLE COMPLAINING FOR YOU TO EVEN THINK OF MAKING A CIVIL UNREST PREDICTION, IN OUR CASE AT LEAST 2 DATAS"
        "Reference The Post id(s) that made you make a certain analysis in the description always"
        "[{'title': 'I predict crash in stock market', 'location': 'none', 'description': '............more description', 'type': 'economic_crisis'}, "
        "{'title': 'I predict there will be floods', 'location': 'Nairobi', 'description': '............more description', 'type': 'climate_risk'}]"
        "STICK TO THAT RESPONSE FORMAT NO EXTRA WORDS"
        f"\n\nData: {json.dumps(posts, indent=2)}"
    )

    model = genai.GenerativeModel('gemini-1.0-pro-latest')  # Use the Generative AI model
    response = model.generate_content(prompt)
    if not hasattr(response, '_result'):
        raise Exception('Error generating AI response.')

    content = response._result.candidates[0].content.parts[0].text.strip()
    print(f"AI raw response: {content}")  # Print the raw AI response for debugging

    # Clean up the response to ensure it's valid JSON
    content = content.replace("'", '"').replace("\n", "").replace("\r", "")

    try:
        # Parse the response based on the pattern
        predictions = json.loads(content)
        return predictions
    except json.JSONDecodeError:
        raise Exception('Error decoding AI response.')

def save_predictions(predictions: List[Dict]):
    """Save the predictions to the Prediction model."""
    for prediction_data in predictions:
        title = prediction_data.get('title')
        location = prediction_data.get('location', 'none')
        description = prediction_data.get('description')
        prediction_type = prediction_data.get('type', 'general')

        prediction, created = Prediction.objects.get_or_create(
            title=title,
            location=location,
            defaults={'description': description, 'type': prediction_type}
        )

        if not created:
            prediction.count += 1
            prediction.description = description
            prediction.save()

        print(f"Saved prediction: {title} at location: {location}")

def mark_posts_as_predicted(posts: List[Dict]):
    """Mark the posts as predicted."""
    special_ids = [post['special_id'] for post in posts]
    InstagramData.objects.filter(special_id__in=special_ids).update(p_analysis=True)
    print(f"Marked {len(special_ids)} posts as predicted.")

def process_predictions():
    """Process the approved posts using the AI and save the predictions."""
    genai.configure(api_key=settings.GOOGLE_API_KEY)  # Configure with your Google API key

    max_iterations = 3
    iteration_count = 0

    while iteration_count < max_iterations:
        print(f"Starting iteration {iteration_count + 1}...")

        # Fetch the latest approved posts that have not been analyzed for predictions
        approved_posts = fetch_approved_posts_for_prediction()
        if not approved_posts:
            print("No approved posts found that have not been analyzed for predictions. Exiting.")
            break

        print(f"Fetched {len(approved_posts)} approved posts that have not been analyzed for predictions.")

        # Send the posts to the AI for prediction
        predictions = send_to_ai_for_prediction(approved_posts)
        print(f"AI response: {predictions}")

        # Save the predictions to the database
        save_predictions(predictions)

        # Mark the posts as predicted
        mark_posts_as_predicted(approved_posts)

        iteration_count += 1
        if iteration_count < max_iterations:
            print(f"Waiting for 10 seconds before the next iteration...")
            time.sleep(10)

    print("Processing completed.")





# utils.py

import google.generativeai as genai
from django.conf import settings

def clear_conversation_thread():
    """Send a prompt to the AI to clear the conversation thread and start a new blank conversation."""
    genai.configure(api_key=settings.GOOGLE_API_KEY)

    prompt = (
        "Please clear the current conversation thread and start a new blank conversation. "
        "We are about to discuss something new."
        "FORGET EVRYTHING WE HAVE PREVIOUSLY TALKED ABOUT WE ARE ABOUT TO START A FRESH"
    )

    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    response = model.generate_content(prompt)
    if not hasattr(response, '_result'):
        raise Exception('Error generating AI response.')

    content = response._result.candidates[0].content.parts[0].text.strip()
    print(f"AI response: {content}")
    return content
































#INCREASE PREDICTION COUNTS
def fetch_analyzed_posts2(limit: int = 30) -> List[Dict]:
    """Fetch the latest posts that have undergone the first analysis but not the second prediction analysis from the database."""
    analyzed_posts = InstagramData.objects.filter(p_analysis=True, p_analysis2=False).order_by('-timestamp')[:limit]
    return [{'special_id': post.special_id, 'caption': post.caption} for post in analyzed_posts]

def send_to_ai_for_counting2(posts: List[Dict], predictions: List[Dict]) -> List[Dict]:
    """Send the posts to the AI for counting occurrences of each prediction and return the counts."""
    prompt = (
        "Analyze the data provided from Instagram and count the occurrences of each prediction based on the following list of predictions. "
        "For each prediction, return the prediction ID and the count of occurrences. "
        "The format you return your data should be like this: "
        "[{'prediction_id': 1, 'count': 2}, {'prediction_id': 2, 'count': 3}]"
        "STICK TO THAT RESPONSE FORMAT NO EXTRA WORDS"
        f"\n\nData: {json.dumps(posts, indent=2)}"
        f"\n\nPredictions: {json.dumps(predictions, indent=2)}"
    )

    model = genai.GenerativeModel('gemini-1.0-pro-latest')  # Use the Generative AI model
    response = model.generate_content(prompt)
    if not hasattr(response, '_result'):
        raise Exception('Error generating AI response.')

    content = response._result.candidates[0].content.parts[0].text.strip()
    print(f"AI raw response: {content}")  # Print the raw AI response for debugging

    # Replace single quotes with double quotes to make it valid JSON
    content = content.replace("'", '"')

    try:
        # Parse the response based on the pattern
        prediction_counts = json.loads(content)
        if not isinstance(prediction_counts, list):
            raise ValueError("AI response is not a list")
        return prediction_counts
    except (json.JSONDecodeError, ValueError):
        print("AI response could not be parsed. Assuming no predictions were detected.")
        return []

def update_prediction_counts(prediction_counts: List[Dict]):
    """Update the counts of predictions in the database."""
    for prediction_data in prediction_counts:
        prediction_id = prediction_data.get('prediction_id')
        count = prediction_data.get('count')

        prediction = Prediction.objects.get(id=prediction_id)
        prediction.count += count
        prediction.save()

        print(f"Updated prediction ID: {prediction_id} with count: {count}")

def mark_posts_as_second_prediction_analyzed(posts: List[Dict]):
    """Mark the posts as having undergone the second prediction analysis."""
    special_ids = [post['special_id'] for post in posts]
    InstagramData.objects.filter(special_id__in=special_ids).update(p_analysis2=True)
    print(f"Marked {len(special_ids)} posts as having undergone the second prediction analysis.")

def process_prediction_counts():
    """Process the posts using the AI to count occurrences of predictions and update the counts."""
    genai.configure(api_key=settings.GOOGLE_API_KEY)  # Configure with your Google API key

    max_iterations = 3
    iteration_count = 0

    while iteration_count < max_iterations:
        print(f"Starting iteration {iteration_count + 1}...")

        # Fetch the latest posts that have undergone the first analysis but not the second prediction analysis
        analyzed_posts = fetch_analyzed_posts2()
        if not analyzed_posts:
            print("No posts found that have undergone the first analysis but not the second prediction analysis. Exiting.")
            break

        print(f"Fetched {len(analyzed_posts)} posts that have undergone the first analysis but not the second prediction analysis.")

        # Fetch all predictions
        predictions = list(Prediction.objects.values('id', 'title', 'location'))

        # Send the posts to the AI for counting occurrences of each prediction
        prediction_counts = send_to_ai_for_counting2(analyzed_posts, predictions)
        print(f"AI response: {prediction_counts}")

        # Update the counts of predictions in the database
        if prediction_counts:
            update_prediction_counts(prediction_counts)

        # Mark the posts as having undergone the second prediction analysis
        mark_posts_as_second_prediction_analyzed(analyzed_posts)

        iteration_count += 1
        if iteration_count < max_iterations:
            print(f"Waiting for 1 minute before the next iteration...")
            time.sleep(10)

    print("Processing completed.")
























##REMOVE REDUNDANT PREDICTIONS

def fetch_all_predictions() -> List[Dict]:
    """Fetch all predictions from the database."""
    predictions = Prediction.objects.all().values('id', 'title', 'description', 'location', 'count', 'type')
    return list(predictions)

def send_to_ai_for_redundancy(predictions: List[Dict]) -> List[Dict]:
    """Send the predictions to the AI for identifying redundant predictions and return the list of redundant prediction IDs."""
    prompt = (
        "Analyze the predictions provided and identify any redundant predictions. For each set of redundant predictions, return the IDs of the predictions that are considered redundant consider the prediction title and description while making your decision and not type. "
        "The format you return your data should be like this: "
        "[{'redundant_ids': [2, 3]}, {'redundant_ids': [4, 5, 6]}]"
        "STICK TO THAT RESPONSE FORMAT NO EXTRA WORDS"
        f"\n\nPredictions: {json.dumps(predictions, indent=2)}"
    )

    model = genai.GenerativeModel('gemini-1.0-pro-latest')  # Use the Generative AI model
    response = model.generate_content(prompt)
    if not hasattr(response, '_result'):
        raise Exception('Error generating AI response.')

    content = response._result.candidates[0].content.parts[0].text.strip()
    print(f"AI raw response: {content}")  # Print the raw AI response for debugging

    # Replace single quotes with double quotes to make it valid JSON
    content = content.replace("'", '"')

    try:
        # Parse the response based on the pattern
        redundant_predictions = json.loads(content)
        return redundant_predictions
    except json.JSONDecodeError:
        raise Exception('Error decoding AI response.')

def remove_redundant_predictions(redundant_predictions: List[Dict]):
    """Remove the redundant predictions while keeping the one with the highest count."""
    for redundant_set in redundant_predictions:
        redundant_ids = redundant_set.get('redundant_ids', [])
        if not redundant_ids:
            continue

        # Fetch the predictions with the given IDs
        predictions = Prediction.objects.filter(id__in=redundant_ids)

        # Find the prediction with the highest count
        highest_count_prediction = max(predictions, key=lambda prediction: prediction.count)

        # Remove the other predictions
        for prediction in predictions:
            if prediction.id != highest_count_prediction.id:
                prediction.delete()

        print(f"Removed redundant predictions: {redundant_ids}, kept prediction ID: {highest_count_prediction.id}")

def process_redundant_predictions():
    """Process the predictions using the AI to identify and remove redundant predictions."""
    genai.configure(api_key=settings.GOOGLE_API_KEY)  # Configure with your Google API key

    # Fetch all predictions
    predictions = fetch_all_predictions()
    print(f"Fetched {len(predictions)} predictions.")

    # Send the predictions to the AI for identifying redundant predictions
    redundant_predictions = send_to_ai_for_redundancy(predictions)
    print(f"AI response: {redundant_predictions}")

    # Remove the redundant predictions
    remove_redundant_predictions(redundant_predictions)

    print("Processing completed.")
















#CHECK PREDICTIONS LIMIT

def ensure_max_predictions(max_limit: int = 60):
    """Ensure that the number of predictions does not exceed the maximum limit."""
    predictions = Prediction.objects.all().order_by('-count')

    if predictions.count() > max_limit:
        # Calculate the number of predictions to remove
        num_to_remove = predictions.count() - max_limit

        # Get the predictions with the lowest counts
        predictions_to_remove = predictions[max_limit:]

        # Remove the predictions with the lowest counts
        for prediction in predictions_to_remove:
            prediction.delete()

        print(f"Removed {num_to_remove} predictions to maintain the limit of {max_limit}.")
    else:
        print(f"The number of predictions ({predictions.count()}) is within the limit of {max_limit}.")

def process_predictions_limit():
    """Process the predictions to ensure the maximum limit is maintained."""
    ensure_max_predictions()
    print("Processing completed.")
























#financial analysis
from decimal import Decimal, InvalidOperation





def fetch_approved_posts_for_finance_prediction(limit: int = 35) -> List[Dict]:
    """Fetch the latest approved posts that have not been analyzed for finance predictions from the database."""
    approved_posts = InstagramData.objects.filter(approved=True, f_analysis=False).order_by('-timestamp')[:limit]
    return [{'special_id': post.special_id, 'caption': post.caption} for post in approved_posts]

def send_to_ai_for_finance_prediction(posts: List[Dict]) -> List[Dict]:
    """Send the posts to the AI for finance prediction and return the list of finance predictions."""
    prompt = (
        "Analyze the data provided from Instagram and track any instances where public resources are being used by the government or just government money. "
        "For each instance, return a title, location, amount, description, and last_updated. "
        "The format you return your data should be like this: "
        "Reference The Post id(s) that made you make a certain analysis in the description always"
        "[{'title': 'Government spending on infrastructure', 'location': 'Nairobi', 'amount': 500000, 'description': 'The government has allocated 500000 for infrastructure development in Nairobi.', 'last_updated': '2023-10-01T12:00:00Z'}, "
        "{'title': 'Funding for education', 'location': 'Mombasa', 'amount': 300000, 'description': 'The government has allocated 300000 for education in Mombasa.', 'last_updated': '2023-10-01T12:00:00Z'}]"
        "STICK TO THAT RESPONSE FORMAT NO EXTRA WORDS"
        f"\n\nData: {json.dumps(posts, indent=2)}"
    )

    model = genai.GenerativeModel('gemini-1.0-pro-latest')  # Use the Generative AI model
    response = model.generate_content(prompt)
    if not hasattr(response, '_result'):
        raise Exception('Error generating AI response.')

    content = response._result.candidates[0].content.parts[0].text.strip()
    print(f"AI raw response: {content}")  # Print the raw AI response for debugging

    # Check if the AI response indicates no relevant data
    if content.lower() == "there is no mention of public resources being used by the government or government money in the provided data.":
        print("No relevant data found. Moving to the next iteration.")
        return []

    # Clean up the response to ensure it's valid JSON
    content = content.replace("'", '"').replace("\n", "").replace("\r", "")

    try:
        # Parse the response based on the pattern
        finance_predictions = json.loads(content)
        if not isinstance(finance_predictions, list):
            raise ValueError("AI response is not a list")
        return finance_predictions
    except (json.JSONDecodeError, ValueError):
        print("AI response could not be parsed. Assuming no finance predictions were detected.")
        return []

def save_finance_predictions(finance_predictions: List[Dict]):
    """Save the finance predictions to the Finance model."""
    for finance_data in finance_predictions:
        title = finance_data.get('title')
        location = finance_data.get('location')
        amount = finance_data.get('amount', 0)
        description = finance_data.get('description')
        last_updated = finance_data.get('last_updated')

        # Ensure amount is a positive integer
        try:
            amount = int(amount) if amount is not None else 0
        except ValueError:
            amount = 0

        finance, created = Finance.objects.get_or_create(
            title=title,
            location=location,
            defaults={'amount': amount, 'description': description, 'last_updated': last_updated}
        )

        if not created:
            finance.amount += amount
            finance.description = description
            finance.last_updated = last_updated
            finance.save()

        print(f"Saved finance prediction: {title} at location: {location}")

def mark_posts_as_finance_predicted(posts: List[Dict]):
    """Mark the posts as finance predicted."""
    special_ids = [post['special_id'] for post in posts]
    InstagramData.objects.filter(special_id__in=special_ids).update(f_analysis=True)
    print(f"Marked {len(special_ids)} posts as finance predicted.")

def process_finance_predictions():
    """Process the approved posts using the AI and save the finance predictions."""
    genai.configure(api_key=settings.GOOGLE_API_KEY)  # Configure with your Google API key

    max_iterations = 3
    iteration_count = 0

    while iteration_count < max_iterations:
        print(f"Starting iteration {iteration_count + 1}...")

        # Fetch the latest approved posts that have not been analyzed for finance predictions
        approved_posts = fetch_approved_posts_for_finance_prediction()
        if not approved_posts:
            print("No approved posts found that have not been analyzed for finance predictions. Exiting.")
            break

        print(f"Fetched {len(approved_posts)} approved posts that have not been analyzed for finance predictions.")

        # Send the posts to the AI for finance prediction
        finance_predictions = send_to_ai_for_finance_prediction(approved_posts)
        print(f"AI response: {finance_predictions}")

        # Save the finance predictions to the database
        if finance_predictions:
            save_finance_predictions(finance_predictions)

        # Mark the posts as finance predicted
        mark_posts_as_finance_predicted(approved_posts)

        iteration_count += 1
        if iteration_count < max_iterations:
            print(f"Waiting for 10 seconds before the next iteration...")
            time.sleep(10)

    print("Processing completed.")
