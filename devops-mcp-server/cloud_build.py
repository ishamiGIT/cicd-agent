import google.auth
from googleapiclient import discovery
from app import mcp
import time


@mcp.tool
def create_cloud_build_trigger(project_id: str, location_id: str, trigger_id: str, developer_connect_git_repository_link: str, service_account: str):
    """Creates a new Cloud Build trigger.

    Args:
        project_id: The ID of the Google Cloud project.
        location_id: The ID of the location for the trigger.
        trigger_id: The ID of the trigger to create.
        developer_connect_git_repository_link: The resource name of the Developer Connect GitRepositoryLink.
        build_config_path: The path to the build configuration file.
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = discovery.build('cloudbuild', 'v1', credentials=credentials)

        parent = f"projects/{project_id}/locations/{location_id}"
        trigger = {
            "name": trigger_id,
            "developer_connect_event_config": {
                "git_repository_link": developer_connect_git_repository_link,
                "push": {
                    "branch": "^main$",
                },
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
