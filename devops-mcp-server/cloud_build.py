import google.auth
from googleapiclient import discovery
from app import mcp
import time
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def _get_cloud_build_service():
    """Gets the Cloud Build service client."""
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return discovery.build('cloudbuild', 'v1', credentials=credentials)

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
    ) -> Dict[str, Any]:
    """Creates a new Cloud Build trigger.

    Args:
        project_id: The ID of the Google Cloud project.
        location_id: The ID of the location for the trigger.
        trigger_id: The ID of the trigger to create.
        developer_connect_git_repository_link: The resource name of the Developer Connect GitRepositoryLink.
        service_account: The service account to use for the trigger.
        git_branch_push (Optional[str]): The branch pattern to trigger on (e.g., "^main$").
        git_tag_push (Optional[str]): The tag pattern to trigger on (e.g., "v*.*").
    
    Raises:
        ValueError: If both or neither of git_branch_push and git_tag_push are provided.

    Returns:
        A dictionary containing the created trigger or an error message.
    """
    try:
        logger.info(f"Creating Cloud Build trigger '{trigger_id}' in project '{project_id}' and location '{location_id}'.")
        logger.debug(f"Developer Connect Git Repository Link: {developer_connect_git_repository_link}")
        logger.debug(f"Service Account: {service_account}")
        logger.debug(f"Git Branch Push: {git_branch_push}")
        logger.debug(f"Git Tag Push: {git_tag_push}")

        if (git_branch_push and git_tag_push) or (not git_branch_push and not git_tag_push):
            raise ValueError(
                "Exactly one of 'git_branch_push' or 'git_tag_push' must be provided."
            )
        
        service = _get_cloud_build_service()

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
        logger.debug(f"Trigger object: {trigger}")

        request = service.projects().locations().triggers().create(parent=parent, body=trigger)
        response = request.execute() # CreateBuildTrigger is not an LRO
        logger.info(f"Successfully created Cloud Build trigger: {response['name']}")
        return {"message": f"Successfully created Cloud Build trigger: {response['name']}"}

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return {"error": str(e)}



@mcp.tool
def run_build_trigger(project_id: str, location: str, trigger_id: str) -> Dict[str, Any]:
    """Runs a Cloud Build trigger.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the trigger.
        trigger_id: The ID of the trigger to run.

    Returns:
        A dictionary containing the operation of the triggered build or an error message.
    """
    try:
        logger.info(f"Running Cloud Build trigger '{trigger_id}' in project '{project_id}' and location '{location}'.")
        service = _get_cloud_build_service()

        name = f"projects/{project_id}/locations/{location}/triggers/{trigger_id}"
        request = service.projects().locations().triggers().run(name=name, body={})
        try:
            response = request.execute()
        except Exception as e:
            logger.error(f"Error running Cloud Build trigger: {e}", exc_info=True)
            return {"error": str(e)}

        logger.info(f"Successfully ran Cloud Build trigger: {trigger_id}")
        logger.debug(f"Operation response: {response}")
        return {"message": f"Successfully ran Cloud Build trigger: {trigger_id}", "operation": response}

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return {"error": str(e)}

@mcp.tool
def list_build_triggers(project_id: str, location: str) -> List[Dict[str, Any]]:
    """Lists all Cloud Build triggers in a given location.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the triggers.

    Returns:
        A list of triggers or a dictionary with an error message.
    """
    try:
        logger.info(f"Listing Cloud Build triggers in project '{project_id}' and location '{location}'.")
        service = _get_cloud_build_service()

        parent = f"projects/{project_id}/locations/{location}"
        request = service.projects().locations().triggers().list(parent=parent)
        try:
            response = request.execute()
        except Exception as e:
            logger.error(f"Error listing Cloud Build triggers: {e}", exc_info=True)
            return {"error": str(e)}

        triggers = response.get("triggers", [])
        logger.info(f"Found {len(triggers)} Cloud Build triggers.")
        logger.debug(f"Triggers: {triggers}")
        return triggers

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return {"error": str(e)}
