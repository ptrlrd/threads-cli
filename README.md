# Threads Command-Line Interface (CLI) Tool
The Threads CLI Tool is a powerful and efficient command-line application designed to provide another way to interact
with Threads. Developed using Python and leveraging the `typer` library for a user-friendly interface and the `rich`
library for visual output, this tool can do a range of actions, including creating posts, retrieving 
profile information, managing drafts, and more.

## Key Features
- User Profile: Retrieve and display comprehensive user profile information, including the user's last post.
- Recent Posts: Fetch and showcase the most recent posts made by the user.
- Top Liked Posts: Retrieve the top liked posts of all time or within a specific time range.
- Post Creation: Create text posts and image posts.
- Replies: Get the latest replies for a specific media post and send replies to engage with the community.
- Scheduling: Schedule posts to be automatically published at a specified future date and time.
- Drafts: Create, manage, and send drafts, providing flexibility in your content creation workflow.

## Getting Started
To get started with the Threads CLI Tool, follow these steps:

Clone the repository:
```
git clone https://github.com/your-repo/threads-cli.git
cd threads-cli
```

Set up a virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:
```
pip install -r requirements.txt
```

Configure environment variables:
Create a `.env` file in the project's root directory and add the following:


```
ACCESS_TOKEN=your_access_token
```

## Usage
The Threads CLI Tool provides a wide range of commands to interact with the Threads API. Here are a few examples:

Retrieve user profile:
```
python main.py get-profile
```

Get recent posts:
```
python main.py get-recent-posts --limit 10
```

Create a text post:
```
python main.py create-text-post "Hello, Threads!"
```

Schedule a post:
```
python main.py schedule-post "Scheduled post" "2024-06-22 09:00:00"
```

For a complete list of available commands and their descriptions, run:
```
python main.py --help
```