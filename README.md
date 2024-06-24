
# Threads CLI

This CLI tool allows you to interact with the Threads API to perform various actions like creating posts, 
getting profile information, retrieving recent posts, scheduling posts, and managing drafts. 
The tool is built using Python and leverages the `typer` library for command-line interface creation and the `rich` 
library for pretty-printing tables.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/threads-cli.git
    cd threads-cli
    ```

2. **Set up a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**
    Create a `.env` file in the root directory with the following content:
    ```env
    ACCESS_TOKEN=your_access_token
    ```

## Usage

### Commands

1. **Get Profile Information:**
    Retrieve and display user profile information, including the last post made by the user.
    ```bash
    python main.py get-profile
    ```

2. **Get Recent Posts:**
    Retrieve the most recent posts.
    ```bash
    python main.py get-recent-posts --limit 5
    ```

3. **Get Top Liked Posts:**
    Retrieve the top liked posts of all time or within a specific time range.
    ```bash
    python main.py get-top-liked-posts --limit 5 --time-range 2w
    ```

4. **Create a Text Post:**
    Create a post with text.
    ```bash
    python main.py create-text-post "This is a text post."
    ```

5. **Create an Image Post:**
    Create a post with an image.
    ```bash
    python main.py create-image_post "This is an image post." "https://example.com/image.jpg"
    ```

6. **Get Latest Replies:**
    Retrieve the latest replies for a specific media post.
    ```bash
    python main.py get-latest-replies --media-id <media_id> --limit 5
    ```

7. **Send a Reply:**
    Send a reply to a specific media post.
    ```bash
    python main.py send-reply --media-id <media_id> --text "This is a reply."
    ```

8. **Schedule a Post:**
    Schedule a post with text at a specific time.
    ```bash
    python main.py schedule-post --text "This is a scheduled post." --post-time "2024-06-22 23:22:00"
    ```

9. **Create a Draft:**
    Create a draft with text.
    ```bash
    python main.py create-draft "This is a draft."
    ```

10. **Get Drafts:**
    Retrieve all drafts.
    ```bash
    python main.py get-drafts
    ```

11. **Send a Draft:**
    Send a draft with a specific ID and remove it from drafts.
    ```bash
    python main.py send-draft --draft-id 1
    ```

## Additional Information

### Dependencies
- `typer`
- `requests`
- `rich`
- `python-dotenv`

### Environment Variables
- `ACCESS_TOKEN`: Your Threads API access token.

## Development

Feel free to contribute to this project by creating pull requests. Make sure to follow the standard coding guidelines and thoroughly test your changes.

### Things to do
- [ ] Add tests for the CLI commands.
- [ ] Add support for creating polls.
- [ ] Validate that creating videos/image posts works

