from fastapi import APIRouter, HTTPException
import google.auth
from google.cloud import run_v2 # Changed from 'run' to 'run_v2' for the new function
from mcp import mcp_capability

router = APIRouter()

@router.post("/cloudRun/createService/")
@mcp_capability(
    name="cloudRun/createService/",
    description="Creates a new Cloud Run service.",
    parameters=[
        {
            "name": "project_id",
            "type": "string",
            "description": "The ID of the GCP project.",
        },
        {
            "name": "location",
            "type": "string",
            "description": "The GCP location (e.g., 'us-east1').",
        },
        {
            "name": "service_name",
            "type": "string",
            "description": "The name of the new Cloud Run service.",
        },
        {
            "name": "image_url",
            "type": "string",
            "description": "The URL of the container image (e.g., 'gcr.io/cloudrun/hello').",
        },
        {
            "name": "port",
            "type": "integer",
            "description": "The port that the container listens on.",
        },
    ],
)
def create_cloud_run_service(project_id: str, location: str, service_name: str, image_url: str, port: int):
    """
    Creates a new Cloud Run service.
    """
    try:
        credentials, project = google.auth.default()
        client = run_v2.ServicesClient(credentials=credentials) # Changed from 'run.ServicesClient' to 'run_v2.ServicesClient'

        parent = f"projects/{project_id}/locations/{location}"
        service = {
            "template": {
                "containers": [
                    {
                        "image": image_url,
                        "ports": [
                            {
                                "container_port": port,
                            }
                        ],
                    }
                ]
            }
        }

        response = client.create_service(
            parent=parent, service=service, service_id=service_name
        )

        return {"message": f"Successfully created Cloud Run service: {response.name}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cloudRun/createRevision/")
@mcp_capability(
    name="cloudRun/createRevision/",
    description="Creates a new Cloud Run revision for a service with a new Docker image.",
    parameters=[
        {
            "name": "project_id",
            "type": "string",
            "description": "The ID of the GCP project.",
        },
        {
            "name": "location",
            "type": "string",
            "description": "The GCP location (e.g., 'us-central1').",
        },
        {
            "name": "service_name",
            "type": "string",
            "description": "The name of the Cloud Run service.",
        },
        {
            "name": "image_url",
            "type": "string",
            "description": "The URL of the new Docker image (e.g., 'gcr.io/project-id/image-name:tag').",
        },
        {
            "name": "revision_name",
            "type": "string",
            "description": "The name of the new revision. If not provided, Cloud Run generates one.",
            "optional": True
        },
    ],
)
def create_cloud_run_revision(project_id: str, location: str, service_name: str, image_url: str, revision_name: str = None):
    """
    Creates a new Cloud Run revision for a service with a new Docker image.
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        client = run_v2.ServicesClient(credentials=credentials)

        service_path = client.service_path(project_id, location, service_name)

        # Get the current service to get its template
        service = client.get_service(name=service_path)

        # Create a new revision template based on the current service's template
        new_template = service.template
        new_template.containers[0].image = image_url
        if revision_name:
            new_template.revision = revision_name

        # Update the service with the new revision template
        updated_service = run_v2.Service(
            name=service_path,
            template=new_template
        )

        operation = client.update_service(service=updated_service)
        response = operation.result()

        return {"message": f"Successfully created Cloud Run revision: {response.latest_ready_revision}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
