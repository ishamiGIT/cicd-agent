from fastapi import APIRouter, HTTPException
import google.auth
from googleapiclient.discovery import build
from mcp import mcp_capability

router = APIRouter()

@router.post("/iam/createServiceAccount/")
@mcp_capability(
    name="iam/createServiceAccount/",
    description="Creates a new Google Cloud Platform service account.",
    parameters=[
        {
            "name": "project_id",
            "type": "string",
            "description": "The ID of the GCP project.",
        },
        {
            "name": "display_name",
            "type": "string",
            "description": "The display name for the service account.",
        },
        {
            "name": "account_id",
            "type": "string",
            "description": "The ID for the service account (lowercase, alphanumeric, hyphen allowed).",
        },
    ],
)
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
        service = build("iam", "v1", credentials=credentials)

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
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/iam/addRoleBinding/")
@mcp_capability(
    name="iam/addRoleBinding/",
    description="Adds an IAM role binding to a Google Cloud Platform resource.",
    parameters=[
        {
            "name": "resource_type",
            "type": "string",
            "description": "The type of resource (e.g., 'projects', 'folders', 'organizations').",
        },
        {
            "name": "resource_id",
            "type": "string",
            "description": "The ID of the resource.",
        },
        {
            "name": "role",
            "type": "string",
            "description": "The role to bind (e.g., 'roles/editor', 'roles/viewer').",
        },
        {
            "name": "member",
            "type": "string",
            "description": "The member to bind the role to (e.g., 'user:example@example.com', 'serviceAccount:my-service-account@project-id.iam.gserviceaccount.com').",
        },
    ],
)
def add_iam_role_binding(resource_type: str, resource_id: str, role: str, member: str):
    """Adds an IAM role binding to a Google Cloud Platform resource.

    Args:
        resource_type: The type of resource (e.g., 'projects', 'folders', 'organizations').
        resource_id: The ID of the resource.
        role: The role to bind (e.g., 'roles/editor', 'roles/viewer').
        member: The member to bind the role to (e.g., 'user:example@example.com', 'serviceAccount:my-service-account@project-id.iam.gserviceaccount.com').
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = build("cloudresourcemanager", "v1", credentials=credentials)

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
        raise HTTPException(status_code=500, detail=str(e))
