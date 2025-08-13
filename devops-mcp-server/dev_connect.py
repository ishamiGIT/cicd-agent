from fastapi import HTTPException
import google.auth
from google.cloud import developerconnect_v1
from mcp import mcp_capability

@mcp_capability(
    name="developerConnect/createConnection/",
    description="Creates a new Developer Connect connection.",
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
            "name": "connection_id",
            "type": "string",
            "description": "The ID of the new Developer Connect connection.",
        },
        {
            "name": "display_name",
            "type": "string",
            "description": "The display name of the new Developer Connect connection.",
        },
        {
            "name": "github_config_app_id",
            "type": "string",
            "description": "The GitHub App ID for the connection.",
        },
        {
            "name": "github_config_app_slug",
            "type": "string",
            "description": "The GitHub App slug for the connection.",
        },
        {
            "name": "github_config_installation_id",
            "type": "string",
            "description": "The GitHub App installation ID for the connection.",
        },
        {
            "name": "github_config_authorizer_credential_token",
            "type": "string",
            "description": "The GitHub App authorizer credential token for the connection.",
        },
    ],
)
def create_developer_connect_connection(project_id: str, location: str, connection_id: str, display_name: str, github_config_app_id: str, github_config_app_slug: str, github_config_installation_id: str, github_config_authorizer_credential_token: str):
    """
    Creates a new Developer Connect connection.
    """
    try:
        credentials, project = google.auth.default()
        client = developerconnect_v1.DeveloperConnectClient(credentials=credentials)

        parent = f"projects/{project_id}/locations/{location}"
        connection = {
            "github_config": {
                "app_id": github_config_app_id,
                "app_slug": github_config_app_slug,
                "installation_id": github_config_installation_id,
                "authorizer_credential": {
                    "oauth_token": {
                        "access_token": github_config_authorizer_credential_token,
                    }
                },
            },
        }

        operation = client.create_connection(
            parent=parent, connection=connection, connection_id=connection_id
        )

        response = operation.result()

        return {"message": f"Successfully created Developer Connect connection: {response.name}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))