from app import mcp
import google.auth
from google.cloud import artifactregistry_v1
from typing import Dict, Any

def _get_artifact_registry_service():
    """Gets the Artifact Registry service client."""
    credentials, _ = google.auth.default()
    return artifactregistry_v1.ArtifactRegistryClient(credentials=credentials)

@mcp.tool
def create_artifact_registry_repository(project_id: str, location: str, repository_id: str, format: str) -> Dict[str, Any]:
    """Creates a new Artifact Registry repository.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the repository.
        repository_id: The ID of the repository to create.
        format: The format of the repository. One of DOCKER, MAVEN, NPM, PYPI
    
    Returns:
        A dictionary containing a success message or an error message.
    """
    try:
        client = _get_artifact_registry_service()

        parent = f"projects/{project_id}/locations/{location}"
        repository = {
            "format": format,
        }

        response = client.create_repository(
            parent=parent, repository=repository, repository_id=repository_id
        )
        result = response.result()

        return {"message": f"Successfully created Artifact Registry repository: {result}"}

    except Exception as e:
        return {"error": str(e)}