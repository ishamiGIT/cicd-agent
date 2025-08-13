from fastapi import APIRouter, HTTPException
import google.auth
from mcp import mcp_capability
from google.cloud.devtools import cloudbuild_v1

router = APIRouter()

@router.post("/cloudBuild/createTrigger/")
@mcp_capability(
    name="cloudBuild/createTrigger/",
    description="Creates a new Cloud Build trigger.",
    parameters=[
        {
            "name": "project_id",
            "type": "string",
            "description": "The ID of the GCP project.",
        },
        {
            "name": "trigger_id",
            "type": "string",
            "description": "The ID of the new Cloud Build trigger.",
        },
        {
            "name": "developer_connect_project_id",
            "type": "string",
            "description": "The project ID of the Developer Connect Connection.",
        },
        {
            "name": "developer_connect_location",
            "type": "string",
            "description": "The location of the Developer Connect Connection.",
        },
        {
            "name": "developer_connect_application_id",
            "type": "string",
            "description": "The ID of the Developer Connect Connection.",
        },
        {
            "name": "build_config_path",
            "type": "string",
            "description": "The path to the build config file in the repository (e.g., 'cloudbuild.yaml').",
        },
    ],
)
def create_cloud_build_trigger(project_id: str, trigger_id: str,developer_connect_project_id: str, developer_connect_location: str, developer_connect_application_id: str, build_config_path: str):
    """
    Creates a new Cloud Build trigger.
    """
    try:
        credentials, project = google.auth.default()
        client = cloudbuild_v1.CloudBuildClient(credentials=credentials)

        parent = f"projects/{project_id}"
        trigger = {
            "developer_connect_config": {
                "git_repository_link": f"projects/{developer_connect_project_id}/locations/{developer_connect_location}/applications/{developer_connect_application_id}",
                "build_config_path": build_config_path,
            },
        }

        response = client.create_build_trigger(project_id=project_id, trigger=trigger)

        return {"message": f"Successfully created Cloud Build trigger: {response.name}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
