from fastapi import APIRouter, HTTPException
import google.auth
from mcp import mcp_capability
from google.cloud import artifactregistry_v1

router = APIRouter()

@router.post("/artifactRegistry/createRepository/")
@mcp_capability(
    name="artifactRegistry/createRepository/",
    description="Creates a new Artifact Registry repository.",
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
            "name": "repository_id",
            "type": "string",
            "description": "The ID of the new Artifact Registry repository.",
        },
        {
            "name": "format",
            "type": "string",
            "description": "The format of the repository (e.g., 'DOCKER', 'MAVEN').",
        },
    ],
)
def create_artifact_registry_repository(project_id: str, location: str, repository_id: str, format: str):
    """
    Creates a new Artifact Registry repository.
    """
    try:
        credentials, project = google.auth.default()
        client = artifactregistry_v1.ArtifactRegistryClient(credentials=credentials)

        parent = f"projects/{project_id}/locations/{location}"
        repository = {
            "format": format,
        }

        response = client.create_repository(
            parent=parent, repository=repository, repository_id=repository_id
        )

        return {"message": f"Successfully created Artifact Registry repository: {response.name}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
