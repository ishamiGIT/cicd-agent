from fastmcp import FastMCP

# Create a server instance
mcp = FastMCP(name="test-mcp-server")

@mcp.resource("resource://config")
def get_config() -> dict:
    """Provides the application's configuration."""
    return {"version": "1.0", "author": "MyTeam"}



# def create_gcp_project(project_id: str):
#     """
#     Creates a new Google Cloud Platform project.
#     """
#     try:
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = build("cloudresourcemanager", "v1", credentials=credentials)

#         project_body = {
#             "projectId": project_id,
#             "name": project_id,
#         }

#         request = service.projects().create(body=project_body)
#         request.execute()

#         return {"message": f"Successfully created GCP project: {project_id}"}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# def enable_google_api(project_id: str, api_name: str):
#     """
#     Enables a Google API for a given project.
#     """
#     try:
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/service.management"]
#         )
#         service = build("serviceusage", "v1", credentials=credentials)

#         parent = f"projects/{project_id}"
#         request = service.services().enable(name=f"{parent}/services/{api_name}")
#         request.execute()

#         return {"message": f"Successfully enabled API {api_name} for project {project_id}"}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
