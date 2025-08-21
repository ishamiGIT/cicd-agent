import google.auth
from googleapiclient import discovery
from app import mcp


@mcp.tool
def create_service_account(project_id: str, display_name: str, account_id: str):
    """Creates a new Google Cloud Platform service account.

    Args:
        project_id: The ID of the GCP project.
        display_name: The display name for the service account.
        account_id: The ID for the service account (lowercase, alphanumeric, hyphen allowed).
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = discovery.build("iam", "v1", credentials=credentials)

        project_path = f"projects/{project_id}"
        service_account_body = {
            "displayName": display_name,
        }

        request = service.projects().serviceAccounts().create(
            name=project_path,
            body={
                "accountId": account_id,
                "serviceAccount": service_account_body,
            },
        )
        response = request.execute()

        return {"message": f"Successfully created service account: {response['email']}"}

    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def add_iam_role_binding(resource_type: str, resource_id: str, role: str, member: str):
    """Adds an IAM role binding to a Google Cloud Platform resource.

    Args:
        resource_type: The type of resource (e.g., 'projects', 'folders', 'organizations').
        resource_id: The ID of the resource. my-project, 1234320592234
        role: The role to bind (e.g., 'roles/editor', 'roles/viewer').
        member: The member to bind the role to (e.g., 'user:example@example.com', 'serviceAccount:my-service-account@project-id.iam.gserviceaccount.com').
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = discovery.build("cloudresourcemanager", "v1", credentials=credentials)

        # Get the current IAM policy
        policy_request = service.projects().getIamPolicy(
            resource=resource_id, body={}
        )
        policy = policy_request.execute()

        # Add the new binding
        new_binding = {"role": role, "members": [member]}
        policy["bindings"].append(new_binding)

        # Set the updated IAM policy
        set_policy_request = service.projects().setIamPolicy(
            resource=resource_id, body={"policy": policy}
        )
        set_policy_request.execute()

        return {"message": f"Successfully added role binding for {member} with role {role} to {resource_type}/{resource_id}"}

    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def list_service_accounts(project_id: str):
    """Lists all service accounts in a project.

    Args:
        project_id: The ID of the Google Cloud project.
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = discovery.build("iam", "v1", credentials=credentials)

        parent = f"projects/{project_id}"
        request = service.projects().serviceAccounts().list(name=parent)
        response = request.execute()

        return response.get("accounts", [])

    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def get_iam_role_binding(project_id: str, service_account_email: str):
    """Gets the IAM role bindings for a service account.

    Args:
        project_id: The ID of the GCP project.
        service_account_email: The email of the service account.
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = discovery.build("cloudresourcemanager", "v1", credentials=credentials)

        # Get the current IAM policy
        policy_request = service.projects().getIamPolicy(
            resource=project_id, body={}
        )
        policy = policy_request.execute()

        bindings = []
        for binding in policy.get("bindings", []):
            if f"serviceAccount:{service_account_email}" in binding.get("members", []):
                bindings.append(binding.get("role"))

        return {"roles": bindings}

    except Exception as e:
        return {"error": str(e)}
