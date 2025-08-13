from fastapi import FastAPI, HTTPException
import google.auth
from googleapiclient.discovery import build
from mcp import mcp_capability, mcp_capabilities_registry

from artifact_registry import router as artifact_registry_router # New import
from iam import router as iam_router # New import
from container_analysis import router as container_analysis_router # New import
from cloud_run import router as cloud_run_router # New import
from dev_connect import router as dev_connect_router # New import

app = FastAPI()

app.include_router(artifact_registry_router) # Include the new router
app.include_router(iam_router) # Include the new router
app.include_router(container_analysis_router) # Include the new router
app.include_router(cloud_run_router) # Include the new router
app.include_router(dev_connect_router) # Include the new router

@app.get("/mcp/capabilities")
def get_mcp_capabilities():
    """
    Returns the MCP capabilities.
    """
    return {"capabilities": mcp_capabilities_registry}

@app.post("/cloudResourceManager/createProject/")
@mcp_capability(
    name="cloudResourceManager/createProject/",
    description="Creates a new Google Cloud Platform project.",
    parameters=[
        {
            "name": "project_id",
            "type": "string",
            "description": "The desired ID for the new GCP project.",
        }
    ],
)
def create_gcp_project(project_id: str):
    """
    Creates a new Google Cloud Platform project.
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = build("cloudresourcemanager", "v1", credentials=credentials)

        project_body = {
            "projectId": project_id,
            "name": project_id,
        }

        request = service.projects().create(body=project_body)
        request.execute()

        return {"message": f"Successfully created GCP project: {project_id}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/serviceUsage/enableGoogleApi/")
@mcp_capability(
    name="serviceUsage/enableGoogleApi/",
    description="Enables a Google API for a given project.",
    parameters=[
        {
            "name": "project_id",
            "type": "string",
            "description": "The ID of the GCP project.",
        },
        {
            "name": "api_name",
            "type": "string",
            "description": "The name of the API to enable (e.g., 'compute.googleapis.com').",
        },
    ],
)
def enable_google_api(project_id: str, api_name: str):
    """
    Enables a Google API for a given project.
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/service.management"]
        )
        service = build("serviceusage", "v1", credentials=credentials)

        parent = f"projects/{project_id}"
        request = service.services().enable(name=f"{parent}/services/{api_name}")
        request.execute()

        return {"message": f"Successfully enabled API {api_name} for project {project_id}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
