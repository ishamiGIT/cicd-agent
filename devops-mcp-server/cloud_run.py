from app import mcp
import google.auth
from google.cloud import run_v2


@mcp.tool
def create_cloud_run_service(project_id: str, location: str, service_name: str, image_url: str, port: int):
    """Creates a new Cloud Run service.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the service.
        service_name: The name of the service to create.
        image_url: The URL of the container image to deploy.
        port: The port that the container listens on.
    """
    try:
        credentials, project = google.auth.default()
        client = run_v2.ServicesClient(credentials=credentials)

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

        operation = client.create_service(
            parent=parent, service=service, service_id=service_name
        )
        response = operation.result()

        return {"message": f"Successfully created Cloud Run service: {response}"}

    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def create_cloud_run_revision(project_id: str, location: str, service_name: str, image_url: str, revision_name: str = None):
    """Creates a new Cloud Run revision for a service with a new Docker image.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the service.
        service_name: The name of the service to update.
        image_url: The URL of the new container image to deploy.
        revision_name: The name of the new revision. If not specified, a name will be generated automatically.
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
        return {"error": str(e)}