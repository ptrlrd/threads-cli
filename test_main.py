import unittest
import os
import json
from unittest.mock import patch
from typer.testing import CliRunner
from main import app

TEST_DRAFTS_FILE = "test-drafts.json"

class TestThreadsCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        if os.path.exists(TEST_DRAFTS_FILE):
            os.remove(TEST_DRAFTS_FILE)

    def test_get_profile(self):
        result = self.runner.invoke(app, ["get-profile"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Profile", result.stdout)

    def test_get_recent_posts(self):
        result = self.runner.invoke(app, ["get-recent-posts", "--limit", "5"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Recent Posts", result.stdout)

    def test_create_text_post(self):
        with patch("main.create_post") as mock_create_post:
            mock_create_post.return_value = {"id": "123"}
            result = self.runner.invoke(app, ["create-text-post", "Test post"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Post created with ID: 123", result.stdout)

    def test_create_draft(self):
        result = self.runner.invoke(app, ["create-draft", "Test draft", "--drafts-file", TEST_DRAFTS_FILE])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(TEST_DRAFTS_FILE))
        with open(TEST_DRAFTS_FILE, "r") as file:
            drafts = json.load(file)
            self.assertEqual(len(drafts), 1)
            self.assertEqual(drafts[0]["text"], "Test draft")

    def test_get_drafts(self):
        self.runner.invoke(app, ["create-draft", "Test draft 1", "--drafts-file", TEST_DRAFTS_FILE])
        self.runner.invoke(app, ["create-draft", "Test draft 2", "--drafts-file", TEST_DRAFTS_FILE])
        result = self.runner.invoke(app, ["get-drafts", "--drafts-file", TEST_DRAFTS_FILE])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Test draft 1", result.stdout)
        self.assertIn("Test draft 2", result.stdout)

    def test_send_draft(self):
        self.runner.invoke(app, ["create-draft", "Test draft", "--drafts-file", TEST_DRAFTS_FILE])
        with open(TEST_DRAFTS_FILE, "r") as file:
            drafts = json.load(file)
            draft_id = drafts[0]["id"]

        # Test sending an existing draft
        with patch("main.create_text_post") as mock_create_text_post:
            result = self.runner.invoke(app, ["send-draft", str(draft_id), "--drafts-file", TEST_DRAFTS_FILE])
            self.assertEqual(result.exit_code, 0)
            self.assertIn(f"Draft with ID {draft_id} sent and removed from drafts.", result.stdout)
        with open(TEST_DRAFTS_FILE, "r") as file:
            drafts = json.load(file)
            self.assertEqual(len(drafts), 0)

        # Test sending a non-existing draft
        result = self.runner.invoke(app, ["send-draft", "999", "--drafts-file", TEST_DRAFTS_FILE])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Draft with ID 999 not found.", result.stdout)

if __name__ == "__main__":
    unittest.main()