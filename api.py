import requests
from utils import convert_to_locale

BASE_URL = "https://graph.threads.net/v1.0"

def get_user_id(headers):
    response = requests.get(f"{BASE_URL}/me?fields=id", headers=headers)
    response.raise_for_status()
    return response.json()['id']

def get_user_profile(user_id, headers):
    profile_fields = "id,username,threads_profile_picture_url,threads_biography"
    response = requests.get(f"{BASE_URL}/{user_id}?fields={profile_fields}", headers=headers)
    response.raise_for_status()
    return response.json()

def get_user_posts(user_id, headers, limit=5):
    post_fields = "id,media_product_type,media_type,media_url,permalink,owner,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post"
    response = requests.get(f"{BASE_URL}/{user_id}/threads?fields={post_fields}&limit={limit}", headers=headers)
    response.raise_for_status()
    return response.json().get('data', [])

def get_post_insights(post_id, headers):
    metrics = "views,likes,replies,reposts,quotes"
    response = requests.get(f"{BASE_URL}/{post_id}/insights?metric={metrics}", headers=headers)
    if response.status_code == 500:
        return {}
    response.raise_for_status()
    insights = response.json().get('data', [])
    return {insight['name']: insight['values'][0]['value'] for insight in insights}

def fetch_all_posts(user_id, headers):
    all_posts = []
    fields = "id,media_product_type,media_type,media_url,permalink,owner,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post"
    next_url = f"{BASE_URL}/{user_id}/threads?fields={fields}"
    while next_url:
        response = requests.get(next_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        all_posts.extend(data.get('data', []))
        next_url = data.get('paging', {}).get('next')
    return all_posts

def create_post(user_id, headers, payload):
    response = requests.post(f"{BASE_URL}/{user_id}/threads", headers=headers, json=payload)
    response.raise_for_status()
    container_id = response.json()['id']

    publish_payload = {
        "creation_id": container_id
    }
    publish_response = requests.post(f"{BASE_URL}/{user_id}/threads_publish", headers=headers, json=publish_payload)
    publish_response.raise_for_status()
    return publish_response.json()

def get_post_replies(media_id, headers, limit=5):
    fields = "id,text,username,permalink,timestamp,media_product_type,media_type,shortcode,has_replies,root_post,replied_to,is_reply,hide_status"
    response = requests.get(f"{BASE_URL}/{media_id}/replies?fields={fields}&limit={limit}&reverse=true", headers=headers)
    response.raise_for_status()
    return response.json().get('data', [])

def get_post_replies_count(post_id, headers):
    response = requests.get(f"{BASE_URL}/{post_id}/replies", headers=headers)
    response.raise_for_status()
    replies = response.json().get('data', [])
    return len(replies)