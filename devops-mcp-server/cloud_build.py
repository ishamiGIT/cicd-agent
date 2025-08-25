import google.auth
from googleapiclient import discovery
from app import mcp
import time
from typing import Optional

@mcp.tool
def create_cloud_build_trigger(
    project_id: str,
    location_id: str,
    trigger_id: str,
    developer_connect_git_repository_link: str,
    service_account: str,
    *,  #  Makes subsequent arguments keyword-only
    git_branch_push: Optional[str] = None,
    git_tag_push: Optional[str] = None
    ):
    """Creates a new Cloud Build trigger.

    Args:
        project_id: The ID of the Google Cloud project.
        location_id: The ID of the location for the trigger.
        trigger_id: The ID of the trigger to create.
        developer_connect_git_repository_link: The resource name of the Developer Connect GitRepositoryLink.
        git_branch_push (Optional[str]): The branch pattern to trigger on (e.g., "^main$").
        git_tag_push (Optional[str]): The tag pattern to trigger on (e.g., "v*.*").
    
    Raises:
        ValueError: If both or neither of git_branch_push and git_tag_push are provided.    
    """
    try:
        if (git_branch_push and git_tag_push) or (not git_branch_push and not git_tag_push):
            raise ValueError(
                "Exactly one of 'git_branch_push' or 'git_tag_push' must be provided."
            )
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = discovery.build('cloudbuild', 'v1', credentials=credentials)

        parent = f"projects/{project_id}/locations/{location_id}"
        push_config = None
        if git_branch_push:
            push_config = {
                "branch": git_branch_push,
            }
    
        if git_tag_push:
            push_config = {
                "tag": git_tag_push,
            }
        trigger = {
            "name": trigger_id,
            "developer_connect_event_config": {
                "git_repository_link": developer_connect_git_repository_link,
                "push": push_config,
            },
            "autodetect": True,
            "service_account" : service_account,
        }

        request = service.projects().locations().triggers().create(parent=parent, body=trigger)
        operation = request.execute()

        operation_name = operation['name']
        while 'done' not in operation or not operation['done']:
            time.sleep(1)
            operation = service.projects().locations().operations().get(name=operation_name).execute()

        if 'error' in operation:
            return {'error': operation['error']}

        return {"message": f"Successfully created Cloud Build trigger: {operation.get('response').get('name')}"}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def run_build_trigger(project_id: str, location: str, trigger_id: str):
    """Runs a Cloud Build trigger.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the trigger.
        trigger_id: The ID of the trigger to run.
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = discovery.build('cloudbuild', 'v1', credentials=credentials)

        name = f"projects/{project_id}/locations/{location}/triggers/{trigger_id}"
        request = service.projects().locations().triggers().run(name=name, body={})
        response = request.execute()

        return {"message": f"Successfully ran Cloud Build trigger: {trigger_id}", "operation": response}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def list_build_triggers(project_id: str, location: str):
    """Lists all Cloud Build triggers in a given location.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the triggers.
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = discovery.build('cloudbuild', 'v1', credentials=credentials)

        parent = f"projects/{project_id}/locations/{location}"
        request = service.projects().locations().triggers().list(parent=parent)
        response = request.execute()

        return response.get("triggers", [])

    except Exception as e:
        return {"error": str(e)}
