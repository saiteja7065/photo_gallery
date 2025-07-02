def has_changelog_and_url(repo_link):
    """
    Returns (has_changelog: bool, changelog_url: str or None)
    """
    project_id = get_project_id_from_repo_link(repo_link)
    if not project_id:
        return False, None
    try:
        # Check if CHANGELOG exists in main branch
        url = f"https://code.swecha.org/api/v4/projects/{project_id}/repository/files/CHANGELOG"
        headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
        response = make_api_request(url, headers, params={"ref": "main"})
        if response:
            # Construct the CHANGELOG web URL
            changelog_url = repo_link.rstrip('/') + "/-/blob/main/CHANGELOG"
            return True, changelog_url
        else:
            return False, None
    except Exception as e:
        print(f"⚠ Error checking CHANGELOG: {str(e)}")
        return False, None
def has_contributing_and_url(repo_link):
    """
    Returns (has_contributing: bool, contributing_url: str or None)
    """
    project_id = get_project_id_from_repo_link(repo_link)
    if not project_id:
        return False, None
    try:
        # Check if CONTRIBUTING.md exists in main branch
        url = f"https://code.swecha.org/api/v4/projects/{project_id}/repository/files/CONTRIBUTING.md"
        headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
        response = make_api_request(url, headers, params={"ref": "main"})
        if response:
            # Construct the CONTRIBUTING.md web URL
            contributing_url = repo_link.rstrip('/') + "/-/blob/main/CONTRIBUTING.md"
            return True, contributing_url
        else:
            return False, None
    except Exception as e:
        print(f"⚠ Error checking CONTRIBUTING.md: {str(e)}")
        return False, None
from urllib.parse import quote
import requests
import os
from dotenv import load_dotenv

def make_api_request(url, headers=None, params=None, method="GET", data=None):
    try:
        response = requests.request(method, url, headers=headers, params=params, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠ Error making API request: {e}")
        return None

# Load environment variables from .env file
load_dotenv()
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")


def get_project_id_from_repo_link(repo_link):
    try:
        # Remove base URL
        base_url = "https://code.swecha.org/"
        if repo_link.startswith(base_url):
            repo_path = repo_link[len(base_url):].rstrip("/")
        else:
            print("❌ Invalid repository link. Must start with:", base_url)
            return None

        # GitLab requires URL-encoded full path
        encoded_path = quote(repo_path, safe='')
        url = f"https://code.swecha.org/api/v4/projects/{encoded_path}"
        headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
        project = make_api_request(url, headers)
        return project["id"] if project else None
    except Exception as e:
        print(f"⚠ Error extracting project ID: {e}")
        return None



def has_readme_and_url(repo_link):
    """
    Returns (has_readme: bool, readme_url: str or None)
    """
    project_id = get_project_id_from_repo_link(repo_link)
    if not project_id:
        return False, None
    try:
        # Check if README.md exists in main branch
        url = f"https://code.swecha.org/api/v4/projects/{project_id}/repository/files/README.md"
        headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
        response = make_api_request(url, headers, params={"ref": "main"})
        if response:
            # Construct the README.md web URL
            readme_url = repo_link.rstrip('/') + "/-/blob/main/README.md"
            return True, readme_url
        else:
            return False, None
    except Exception as e:
        print(f"⚠ Error checking README.md: {str(e)}")
        return False, None



# Run from CLI if this file is executed directly
if __name__ == "__main__":
    while True:
        repo_link = input("🔗 Enter full repository link (e.g., https://code.swecha.org/username/project): ").strip()
        if not repo_link:
            print("❌ Repository link cannot be empty.")
            break


        has_changelog, changelog_url = has_changelog_and_url(repo_link)
        if has_changelog:
            print(f"✅ CHANGELOG found: {changelog_url}")
        else:
            print("❌ CHANGELOG not found in the repository.")

        again = input("\n🔁 Check another repository? (y/n): ").strip().lower()
        if again != 'y':
            break