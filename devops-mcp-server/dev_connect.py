from fastapi import APIRouter, HTTPException
import google.auth
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from mcp import mcp_capability

router = APIRouter()

@router.post("/developerConnect/createConnection/")
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
            "name": "region",
            "type": "string",
            "description": "The GCP region/location (e.g., 'us-east1').",
        },
        {
            "name": "connection_id",
            "type": "string",
            "description": "The ID of the new Developer Connect connection.",
        },
    ],
)
def create_developer_connect_connection(project_id: str, region: str, connection_id: str):
    """Gets a Developer Connect connection, creating it if it doesn't exist."""
    credentials, _ = google.auth.default()
    service = discovery.build('developerconnect', 'v1', credentials=credentials)
    parent = f'projects/{project_id}/locations/{region}'
    connection_name = f'{parent}/connections/{connection_id}'

    try:
        # Try to get the connection first
        print(f"--- Checking for existing connection: {connection_name} ---")
        request = service.projects().locations().connections().get(name=connection_name)
        response = request.execute()
        print("--- Connection already exists. ---")
        return response
    except HttpError as e:
        # If it's not found, create it
        if e.resp.status == 404:
            print("--- Connection not found. Creating new connection... ---")
            body = {
                "github_config": {
                    "github_app": "DEVELOPER_CONNECT"
                }
            }
            create_request = service.projects().locations().connections().create(
                parent=parent,
                connectionId=connection_id,
                body=body
            )
            response = create_request.execute()
            return {"message": f"Successfully created Developer Connect connection: {response.name}"}
        
        else:
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/developerConnect/createConnection/")
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
            "name": "region",
            "type": "string",
            "description": "The GCP region/location (e.g., 'us-east1').",
        },
        {
            "name": "connection_id",
            "type": "string",
            "description": "The ID of the new Developer Connect connection.",
        },
        {
            "name": "repository_link_id",
            "type": "string",
            "description": "The ID of the new Developer Connect repository link.",
        },
        {
            "name": "repo_uri",
            "type": "string",
            "description": "GitHub URI for the repository to link.",
        },
    ],
)
def create_git_repository_link(project_id: str, region: str, connection_id: str, repository_link_id: str, repo_uri: str):
    """Creates a new Developer Connect Git Repository Link."""
    credentials, _ = google.auth.default()
    service = discovery.build('developerconnect', 'v1', credentials=credentials)

    parent = f'projects/{project_id}/locations/{region}/connections/{connection_id}'
    link_name = f'{parent}/gitRepositoryLinks/{repository_link_id}'

    try:
        print(f"--- Checking for existing git repository link: {link_name} ---")
        request = service.projects().locations().connections().gitRepositoryLinks().get(name=link_name)
        response = request.execute()
        print("--- Git repository link already exists. ---")
        return response
    except HttpError as e:
        if e.resp.status == 404:
            print("--- Git repository link not found. Creating new link... ---")
            body = {
                "clone_uri": repo_uri
            }
            create_request = service.projects().locations().connections().gitRepositoryLinks().create(
                parent=parent,
                gitRepositoryLinkId=repository_link_id,
                body=body
            )
            response = create_request.execute()
            return {"message": f"Successfully created Developer Connect repository link: {response.name}"}        
        else:
            raise HTTPException(status_code=500, detail=str(e))

    pass


@router.post("/developerConnect/listConnections/")
@mcp_capability(
    name="developerConnect/listConnections/",
    description="List Developer Connect connections.",
    parameters=[
        {
            "name": "project_id",
            "type": "string",
            "description": "The ID of the GCP project.",
        },
        {
            "name": "region",
            "type": "string",
            "description": "The GCP region/location (e.g., 'us-east1').",
        },
    ],
)
def list_connections(project_id, region):
    """Lists Developer Connect resources in a GCP project."""
    try:
        credentials, project_id = google.auth.default()
        service = discovery.build('developerconnect', 'v1', credentials=credentials)

        parent = f'projects/{project_id}/locations/{region}'
        request = service.projects().locations().connections().list(parent=parent)
        response = request.execute()
        
        connection_list=[]
        for connection in response.get('connections', []):
            connection_list.append(f"{connection['name']}")

        return {"message": f"Developer Connect connections: {' '.join(connection_list)}"}        

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    pass
