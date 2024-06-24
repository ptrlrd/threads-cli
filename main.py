import typer
import requests
import time
import threading
import json
import os
from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta, timezone

app = typer.Typer()
console = Console()

ACCESS_TOKEN = ""
BASE_URL = "https://graph.threads.net/v1.0"

HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}
DRAFTS_FILE = 'drafts.json'

def get_user_id():
    response = requests.get(f"{BASE_URL}/me?fields=id", headers=HEADERS)
    response.raise_for_status()
    return response.json()['id']

@app.command()
def get_profile():
    """
    Retrieve and display user profile information, including the last post made by the user.
    """
    user_id = get_user_id()
    profile_fields = "id,username,threads_profile_picture_url,threads_biography"
    profile_response = requests.get(f"{BASE_URL}/{user_id}?fields={profile_fields}", headers=HEADERS)
    profile_response.raise_for_status()
    profile = profile_response.json()
    profile_username = profile.get("username", "N/A")

    post_fields = "id,media_product_type,media_type,media_url,permalink,owner,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post"
    post_response = requests.get(f"{BASE_URL}/{user_id}/threads?fields={post_fields}&limit=1", headers=HEADERS)
    post_response.raise_for_status()
    last_post = post_response.json().get('data', [{}])[0]

    profile_table = Table(title=f'{profile_username}\'s Profile')
    profile_table.add_column("Field", style="cyan", no_wrap=True)
    profile_table.add_column("Value", style="magenta")

    profile_table.add_row("ID", profile.get("id", "N/A"))
    profile_table.add_row("Username", profile.get("username", "N/A"))
    profile_table.add_row("Profile Picture URL", profile.get("threads_profile_picture_url", "N/A"))
    profile_table.add_row("Biography", profile.get("threads_biography", "N/A"))
    if last_post:
        profile_table.add_row("Last Post ID", last_post.get("id", "N/A"))
        profile_table.add_row("Post Type", last_post.get("media_type", "N/A"))
        profile_table.add_row("Post Text", last_post.get("text", "N/A"))
        profile_table.add_row("Post Permalink", last_post.get("permalink", "N/A"))
        profile_table.add_row("Post Timestamp", convert_to_locale(last_post.get("timestamp", "N/A")))
    else:
        profile_table.add_row("Message", "No posts found")

    console.print(profile_table)

def get_post_insights(post_id):
    """
    Retrieve insights for a specific post.
    """
    metrics = "views,likes,replies,reposts,quotes"
    response = requests.get(f"{BASE_URL}/{post_id}/insights?metric={metrics}", headers=HEADERS)
    if response.status_code == 500:
        return {}
    response.raise_for_status()
    insights = response.json().get('data', [])
    insights_dict = {insight['name']: insight['values'][0]['value'] for insight in insights}
    return insights_dict


def fetch_all_posts(user_id):
    """
    Fetch all posts for the user.
    """
    all_posts = []
    fields = "id,media_product_type,media_type,media_url,permalink,owner,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post"
    next_url = f"{BASE_URL}/{user_id}/threads?fields={fields}"
    while next_url:
        response = requests.get(next_url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        all_posts.extend(data.get('data', []))
        next_url = data.get('paging', {}).get('next')
    return all_posts


@app.command()
def get_posts(limit: int = 5):
    """
    Retrieve the last few posts.
    """
    user_id = get_user_id()
    fields = "id,media_product_type,media_type,media_url,permalink,owner,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post"
    response = requests.get(f"{BASE_URL}/{user_id}/threads?fields={fields}&limit={limit}", headers=HEADERS)
    response.raise_for_status()
    posts = response.json().get('data', [])

    table = Table(title="User Posts")
    table.add_column("Username", style="cyan", no_wrap=True)
    table.add_column("Timestamp", style="magenta")
    table.add_column("Media ID", style="green")
    table.add_column("Text", style="yellow")
    table.add_column("Permalink", style="blue")
    table.add_column("Likes", style="red")
    table.add_column("Replies", style="green")
    table.add_column("Reposts", style="blue")
    table.add_column("Quotes", style="yellow")
    table.add_column("Views", style="cyan")

    for post in posts:
        if post.get('media_type') == 'REPOST_FACADE':
            continue
        timestamp = convert_to_locale(post.get('timestamp', 'N/A'))
        insights = get_post_insights(post['id'])
        table.add_row(
            post.get('username', 'N/A'),
            timestamp,
            post.get('id', 'N/A'),
            post.get('text', 'N/A'),
            post.get('permalink', 'N/A'),
            str(insights.get('likes', 'N/A')),
            str(insights.get('replies', 'N/A')),
            str(insights.get('reposts', 'N/A')),
            str(insights.get('quotes', 'N/A')),
            str(insights.get('views', 'N/A'))
        )

    console.print(table)


@app.command()
def get_top_liked_posts(limit: int = 5, time_range: str = None):
    """
    Retrieve the top liked posts of all time or within a specific time range.
    """
    user_id = get_user_id()
    all_posts = fetch_all_posts(user_id)

    if time_range:
        now = datetime.now(timezone.utc)
        if time_range.endswith('w'):
            weeks = int(time_range[:-1])
            start_time = now - timedelta(weeks=weeks)
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            start_time = now - timedelta(days=days)
        elif time_range.endswith('h'):
            hours = int(time_range[:-1])
            start_time = now - timedelta(hours=hours)
        elif time_range.endswith('m'):
            months = int(time_range[:-1])
            start_time = now - timedelta(days=30 * months)
        else:
            typer.echo("Invalid time range format. Use '2w' for 2 weeks, '7d' for 7 days, '24h' for 24 hours, or '7m' for 7 months.")
            return

        all_posts = [post for post in all_posts if datetime.strptime(post['timestamp'], '%Y-%m-%dT%H:%M:%S%z') >= start_time]

    posts_with_likes = []
    for post in all_posts:
        if post.get('media_type') == 'REPOST_FACADE':
            continue
        insights = get_post_insights(post['id'])
        if 'likes' in insights:
            posts_with_likes.append((post, insights['likes']))

    posts_with_likes.sort(key=lambda x: x[1], reverse=True)
    top_liked_posts = posts_with_likes[:limit]

    table = Table(title="Top Liked Posts")
    table.add_column("Username", style="cyan", no_wrap=True)
    table.add_column("Timestamp", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Text", style="yellow")
    table.add_column("Permalink", style="blue")
    table.add_column("Likes", style="red")
    table.add_column("Replies", style="green")
    table.add_column("Reposts", style="blue")
    table.add_column("Quotes", style="yellow")
    table.add_column("Views", style="cyan")

    for post, likes in top_liked_posts:
        timestamp = convert_to_locale(post.get('timestamp', 'N/A'))
        insights = get_post_insights(post['id'])
        table.add_row(
            post.get('username', 'N/A'),
            timestamp,
            post.get('media_type', 'N/A'),
            post.get('text', 'N/A'),
            post.get('permalink', 'N/A'),
            str(insights.get('likes', 'N/A')),
            str(insights.get('replies', 'N/A')),
            str(insights.get('reposts', 'N/A')),
            str(insights.get('quotes', 'N/A')),
            str(insights.get('views', 'N/A'))
        )

    console.print(table)

def convert_to_locale(timestamp):
    """
    Convert timestamp to locale YY-MM-DD hh:mm:ss format.
    """
    if timestamp == 'N/A':
        return timestamp
    dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')
    return dt.strftime('%Y-%m-%d %H:%M:%S')

@app.command()
def create_text_post(text: str):
    """
    Create a post with text.
    """
    user_id = get_user_id()
    payload = {
        "media_type": "TEXT",
        "text": text
    }
    response = requests.post(f"{BASE_URL}/{user_id}/threads", headers=HEADERS, json=payload)
    response.raise_for_status()
    container_id = response.json()['id']

    # Wait for the server to process the upload
    time.sleep(30)

    publish_payload = {
        "creation_id": container_id
    }
    publish_response = requests.post(f"{BASE_URL}/{user_id}/threads_publish", headers=HEADERS, json=publish_payload)
    publish_response.raise_for_status()
    post = publish_response.json()
    typer.echo(f"Post created with ID: {post['id']}")

@app.command()
def create_image_post(text: str, image_url: str):
    """
    Create a post with an image.
    """
    user_id = get_user_id()
    payload = {
        "media_type": "IMAGE",
        "image_url": image_url,
        "text": text
    }
    response = requests.post(f"{BASE_URL}/{user_id}/threads", headers=HEADERS, json=payload)
    response.raise_for_status()
    container_id = response.json()['id']

    # Wait for the server to process the upload
    time.sleep(30)

    publish_payload = {
        "creation_id": container_id
    }
    publish_response = requests.post(f"{BASE_URL}/{user_id}/threads_publish", headers=HEADERS, json=publish_payload)
    publish_response.raise_for_status()
    post = publish_response.json()
    typer.echo(f"Post created with ID: {post['id']}")

@app.command()
def get_latest_replies(media_id: str, limit: int = 5):
    """
    Retrieve the latest replies for a specific media post.
    """
    fields = "id,text,username,permalink,timestamp,media_product_type,media_type,shortcode,has_replies,root_post,replied_to,is_reply,hide_status"
    response = requests.get(f"{BASE_URL}/{media_id}/replies?fields={fields}&limit={limit}&reverse=true", headers=HEADERS)
    response.raise_for_status()
    replies = response.json().get('data', [])

    table = Table(title="Latest Replies")
    table.add_column("Username", style="cyan", no_wrap=True)
    table.add_column("Media ID", style="cyan", no_wrap=True)
    table.add_column("Timestamp", style="magenta")
    table.add_column("Text", style="yellow")
    table.add_column("Permalink", style="blue")

    for reply in replies:
        timestamp = convert_to_locale(reply.get('timestamp', 'N/A'))
        table.add_row(
            reply.get('username', 'N/A'),
            reply.get('id', 'N/A'),
            timestamp,
            reply.get('text', 'N/A'),
            reply.get('permalink', 'N/A')
        )

    console.print(table)


@app.command()
def send_reply(media_id: str, text: str):
    """
    Send a reply to a specific media post.
    """
    user_id = get_user_id()
    payload = {
        "media_type": "TEXT",
        "text": text,
        "reply_to_id": media_id
    }
    response = requests.post(f"{BASE_URL}/{user_id}/threads", headers=HEADERS, json=payload)
    response.raise_for_status()
    container_id = response.json()['id']

    # Wait for the server to process the upload
    time.sleep(30)

    publish_payload = {
        "creation_id": container_id
    }
    publish_response = requests.post(f"{BASE_URL}/{user_id}/threads_publish", headers=HEADERS, json=publish_payload)
    publish_response.raise_for_status()
    reply = publish_response.json()
    typer.echo(f"Reply created with ID: {reply['id']}")

def job_create_text_post(text: str):
    """
    Job function to create a post with text.
    """
    create_text_post(text)

@app.command()
def schedule_post(text: str, post_time: str):
    """
    Schedule a post with text at a specific time.
    """
    post_time_dt = datetime.strptime(post_time, '%Y-%m-%d %H:%M:%S')
    current_time = datetime.now()
    delay = (post_time_dt - current_time).total_seconds()

    if delay <= 0:
        typer.echo("Scheduled time must be in the future.")
        return

    timer = threading.Timer(delay, job_create_text_post, [text])
    timer.start()
    typer.echo(f"Post scheduled for {post_time} with text: '{text}'")

@app.command()
def create_draft(text: str):
    """
    Create a draft with text.
    """
    if os.path.exists(DRAFTS_FILE):
        with open(DRAFTS_FILE, 'r') as file:
            drafts = json.load(file)
    else:
        drafts = []

    next_id = max([draft['id'] for draft in drafts], default=0) + 1

    draft = {
        "id": next_id,
        "text": text,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    drafts.append(draft)

    with open(DRAFTS_FILE, 'w') as file:
        json.dump(drafts, file, indent=4)

    typer.echo(f"Draft created with ID: {next_id}")

@app.command()
def get_drafts():
    """
    Retrieve all drafts.
    """
    if not os.path.exists(DRAFTS_FILE):
        typer.echo("No drafts found.")
        return

    with open(DRAFTS_FILE, 'r') as file:
        drafts = json.load(file)

    table = Table(title="Drafts")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Text", style="yellow")
    table.add_column("Timestamp", style="magenta")

    for draft in drafts:
        table.add_row(
            str(draft['id']),
            draft['text'],
            draft['timestamp']
        )

    console.print(table)

@app.command()
def send_draft(draft_id: int):
    """
    Sends a draft with a specific ID and removes it from drafts.
    """
    if not os.path.exists(DRAFTS_FILE):
        typer.echo("No drafts found.")
        return

    with open(DRAFTS_FILE, 'r') as file:
        drafts = json.load(file)

    draft = next((draft for draft in drafts if draft['id'] == draft_id), None)

    if draft is None:
        typer.echo(f"Draft with ID {draft_id} not found.")
        return

    create_text_post(draft['text'])

    drafts = [draft for draft in drafts if draft['id'] != draft_id]

    with open(DRAFTS_FILE, 'w') as file:
        json.dump(drafts, file, indent=4)

    typer.echo(f"Draft with ID {draft_id} sent and removed from drafts.")


if __name__ == "__main__":
    app()