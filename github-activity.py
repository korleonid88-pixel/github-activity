# github-activity.py
# Запуск: python github-activity.py <username>

import json
import sys
import urllib.request
import urllib.error

API_URL = "https://api.github.com/users/{}/events"


def fetch_events(username):
    """Возвращает список событий пользователя или выбрасывает понятную ошибку."""
    url = API_URL.format(username)

    request = urllib.request.Request(url, headers={
        "User-Agent": "github-activity-cli",      # GitHub требует User-Agent
        "Accept": "application/vnd.github+json",
    })

    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            sys.exit(f'Error: user "{username}" not found.')
        if e.code == 403:
            sys.exit("Error: API rate limit reached. Try again later.")
        sys.exit(f"Error: GitHub API returned status {e.code}.")
    except urllib.error.URLError:
        sys.exit("Error: could not connect to GitHub API.")


def describe_event(event):
    """Превращает событие в читаемую строку."""
    repo = event.get("repo", {}).get("name", "unknown repo")
    event_type = event.get("type", "Unknown")

    if event_type == "PushEvent":
        count = len(event.get("payload", {}).get("commits", []))
        suffix = "" if count == 1 else "s"
        return f"Pushed {count} commit{suffix} to {repo}"
    if event_type == "IssuesEvent":
        return f"Opened a new issue in {repo}"
    if event_type == "IssueCommentEvent":
        return f"Commented on an issue in {repo}"
    if event_type == "PullRequestEvent":
        return f"Opened a pull request in {repo}"
    if event_type == "WatchEvent":
        return f"Starred {repo}"
    if event_type == "ForkEvent":
        return f"Forked {repo}"
    if event_type == "CreateEvent":
        return f"Created a repository or branch in {repo}"
    if event_type == "DeleteEvent":
        return f"Deleted a branch in {repo}"
    if event_type == "PullRequestReviewEvent":
        return f"Reviewed a pull request in {repo}"
    if event_type == "PublicEvent":
        return f"Made {repo} public"
    return f"Did something ({event_type}) in {repo}"


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python github-activity.py <username>")

    username = sys.argv[1]
    events = fetch_events(username)

    if not events:
        print(f'No recent activity found for user "{username}".')
        return

    for event in events:
        print(f"- {describe_event(event)}")


if __name__ == "__main__":
    main()
