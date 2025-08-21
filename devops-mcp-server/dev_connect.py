from app import mcp
import google.auth
from googleapiclient import discovery
import time

@mcp.tool
def create_developer_connect_connection(project_id: str, location: str, connection_id: str):
    """Creates a new Developer Connect connection.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the connection.
        connection_id: The ID of the connection to create.
    
    Returns:
        A dictionary containing a success message or an error message.
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = discovery.build('developerconnect', 'v1', credentials=credentials)

        parent = f"projects/{project_id}/locations/{location}"
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
        time.sleep(3) # sleep for 3 seconds so that the operation suceeds

        name = f"projects/{project_id}/locations/{location}/connections/{connection_id}"
        get_request = service.projects().locations().connections().get(
            name=name,
        )
        response = get_request.execute()

        return {"connection": response}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def create_developer_connect_git_repository_link(project_id: str, location: str, connection_id: str, repository_link_id: str, repo_uri: str):
    """Creates a new Developer Connect Git Repository Link.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the connection.
        connection_id: The ID of the connection.
        repository_link_id: The ID of the repository link to create.
        repo_uri: The URI of the repository to link.
    
    Returns:
        A dictionary containing a success message or an error message.
    """
    try:
        credentials, _ = google.auth.default()
        service = discovery.build('developerconnect', 'v1', credentials=credentials)

        parent = f'projects/{project_id}/locations/{location}/connections/{connection_id}'
        link_name = f'{parent}/gitRepositoryLinks/{repository_link_id}'
        body = {
            "clone_uri": repo_uri
        }
        create_request = service.projects().locations().connections().gitRepositoryLinks().create(
            parent=parent,
            gitRepositoryLinkId=repository_link_id,
            body=body
        )
        response = create_request.execute()
        return {"message": f"Successfully created Developer Connect repository link: {response}"}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def list_developer_connect_connections(project_id: str, location: str):
    """Lists Developer Connect connections.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the connections.
    
    Returns:
        A dictionary containing a list of connections or an error message.
    """
    try:
        credentials, project = google.auth.default()
        service = discovery.build('developerconnect', 'v1', credentials=credentials)

        parent = f"projects/{project_id}/locations/{location}"
        request = service.projects().locations().connections().list(parent=parent)
        response = request.execute()

        return {"connections": response.get("connections", [])}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def get_developer_connect_connection(project_id: str, location: str, connection_id: str):
    """Gets a Developer Connect connection.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the connection.
        connection_id: The ID of the connection.
    
    Returns:
        A dictionary containing the connection or an error message.
    """
    try:
        credentials, project = google.auth.default()
        service = discovery.build('developerconnect', 'v1', credentials=credentials)

        name = f"projects/{project_id}/locations/{location}/connections/{connection_id}"
        request = service.projects().locations().connections().get(name=name)
        response = request.execute()

        return {"connection": response}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def find_git_repository_links_for_git_repo(project_id: str, location: str, repo_uri: str):
    """Finds already configured Developer Connect Git Repository Links for a particular git repository.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the connections.
        repo_uri: The URI of the repository to link.

    Returns:
        A dictionary containing a list of git repository links or an error message.
    """
    try:
        credentials, project = google.auth.default()
        service = discovery.build('developerconnect', 'v1', credentials=credentials)

        parent = f"projects/{project_id}/locations/{location}/connections/-"
        request = service.projects().locations().connections().gitRepositoryLinks().list(parent=parent, filter=f'clone_uri="{repo_uri}"')
        response = request.execute()

        links = response.get("gitRepositoryLinks", [])
        return {"gitRepositoryLinks": links}

    except Exception as e:
        return {"error": str(e)}