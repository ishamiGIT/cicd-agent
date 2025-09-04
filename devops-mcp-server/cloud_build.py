import google.auth
from googleapiclient import discovery
from app import mcp
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)
@mcp.tool
def create_cloud_build_trigger(
    project_id: str,
    location_id: str,
    trigger_id: str,
    developer_connect_git_repository_link: str,
    service_account: str,
    *,  #  Makes subsequent arguments keyword-only
    git_branch_push: Optional[str] = None,
    git_tag_push: Optional[str] = None
    ):
    """Creates a new Cloud Build trigger.

    Args:
        project_id: The ID of the Google Cloud project.
        location_id: The ID of the location for the trigger.
        trigger_id: The ID of the trigger to create.
        developer_connect_git_repository_link: The resource name of the Developer Connect GitRepositoryLink.
        git_branch_push (Optional[str]): The branch pattern to trigger on (e.g., "^main$").
        git_tag_push (Optional[str]): The tag pattern to trigger on (e.g., "v*.*").
    
    Raises:
        ValueError: If both or neither of git_branch_push and git_tag_push are provided.    
    """
    try:
        logger.info(f"Creating Cloud Build trigger '{trigger_id}' in project '{project_id}' and location '{location_id}'.")
        logger.debug(f"Developer Connect Git Repository Link: {developer_connect_git_repository_link}")
        logger.debug(f"Service Account: {service_account}")
        logger.debug(f"Git Branch Push: {git_branch_push}")
        logger.debug(f"Git Tag Push: {git_tag_push}")

        if (git_branch_push and git_tag_push) or (not git_branch_push and not git_tag_push):
            raise ValueError(
                "Exactly one of 'git_branch_push' or 'git_tag_push' must be provided."
            )
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = discovery.build('cloudbuild', 'v1', credentials=credentials)

        parent = f"projects/{project_id}/locations/{location_id}"
        push_config = None
        if git_branch_push:
            push_config = {
                "branch": git_branch_push,
            }
    
        if git_tag_push:
            push_config = {
                "tag": git_tag_push,
            }
        trigger = {
            "name": trigger_id,
            "developer_connect_event_config": {
                "git_repository_link": developer_connect_git_repository_link,
                "push": push_config,
            },
            "autodetect": True,
            "service_account" : service_account,
        }
        logger.debug(f"Trigger object: {trigger}")

        request = service.projects().locations().triggers().create(parent=parent, body=trigger)
        response = request.execute() # CreateBuildTrigger is not an LRO
        logger.info(f"Successfully created Cloud Build trigger: {response['name']}")
        return {"message": f"Successfully created Cloud Build trigger: {response['name']}"}

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool
def run_build_trigger(project_id: str, location: str, trigger_id: str):
    """Runs a Cloud Build trigger.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the trigger.
        trigger_id: The ID of the trigger to run.
    """
    try:
        logger.info(f"Running Cloud Build trigger '{trigger_id}' in project '{project_id}' and location '{location}'.")
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = discovery.build('cloudbuild', 'v1', credentials=credentials)

        name = f"projects/{project_id}/locations/{location}/triggers/{trigger_id}"
        request = service.projects().locations().triggers().run(name=name, body={})
        try:
            response = request.execute()
        except Exception as e:
            logger.error(f"Error running Cloud Build trigger: {e}", exc_info=True)
            return {"error": str(e)}

        logger.info(f"Successfully ran Cloud Build trigger: {trigger_id}")
        logger.debug(f"Operation response: {response}")
        return {"message": f"Successfully ran Cloud Build trigger: {trigger_id}", "operation": response}

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return {"error": str(e)}

@mcp.tool
def list_build_triggers(project_id: str, location: str):
    """Lists all Cloud Build triggers in a given location.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the triggers.
    """
    try:
        logger.info(f"Listing Cloud Build triggers in project '{project_id}' and location '{location}'.")
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        service = discovery.build('cloudbuild', 'v1', credentials=credentials)

        parent = f"projects/{project_id}/locations/{location}"
        request = service.projects().locations().triggers().list(parent=parent)
        try:
            response = request.execute()
        except Exception as e:
            logger.error(f"Error listing Cloud Build triggers: {e}", exc_info=True)
            return {"error": str(e)}

        triggers = response.get("triggers", [])
        logger.info(f"Found {len(triggers)} Cloud Build triggers.")
        logger.debug(f"Triggers: {triggers}")
        return triggers

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return {"error": str(e)}

# @mcp.tool
# def get_build_details(project_id: str, location: str, build_id: str):
#     """Gets the details of a specific build.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the build.
#         build_id: The ID of the build.
#     """
#     try:
#         logger.info(f"Getting details for build '{build_id}' in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/builds/{build_id}"
#         request = service.projects().locations().builds().get(name=name)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error getting build details: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully got details for build: {build_id}")
#         logger.debug(f"Build details: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def list_builds(project_id: str, location: str):
#     """Lists all builds in a given location.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the builds.
#     """
#     try:
#         logger.info(f"Listing builds in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         parent = f"projects/{project_id}/locations/{location}"
#         request = service.projects().locations().builds().list(parent=parent)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error listing builds: {e}", exc_info=True)
#             return {"error": str(e)}

#         builds = response.get("builds", [])
#         logger.info(f"Found {len(builds)} builds.")
#         logger.debug(f"Builds: {builds}")
#         return builds

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def cancel_build(project_id: str, location: str, build_id: str):
#     """Cancels a running build.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the build.
#         build_id: The ID of the build to cancel.
#     """
#     try:
#         logger.info(f"Canceling build '{build_id}' in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/builds/{build_id}"
#         request = service.projects().locations().builds().cancel(name=name, body={})
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error canceling build: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully canceled build: {build_id}")
#         logger.debug(f"Cancel build response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def retry_build(project_id: str, location: str, build_id: str):
#     """Retries a failed build.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the build.
#         build_id: The ID of the build to retry.
#     """
#     try:
#         logger.info(f"Retrying build '{build_id}' in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/builds/{build_id}"
#         request = service.projects().locations().builds().retry(name=name, body={})
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error retrying build: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully retried build: {build_id}")
#         logger.debug(f"Retry build response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def approve_build(project_id: str, location: str, build_id: str):
#     """Approves a pending build.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the build.
#         build_id: The ID of the build to approve.
#     """
#     try:
#         logger.info(f"Approving build '{build_id}' in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/builds/{build_id}"
#         request = service.projects().locations().builds().approve(name=name, body={})
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error approving build: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully approved build: {build_id}")
#         logger.debug(f"Approve build response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def delete_build_trigger(project_id: str, location: str, trigger_id: str):
#     """Deletes a build trigger.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the trigger.
#         trigger_id: The ID of the trigger to delete.
#     """
#     try:
#         logger.info(f"Deleting build trigger '{trigger_id}' in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/triggers/{trigger_id}"
#         request = service.projects().locations().triggers().delete(name=name)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error deleting build trigger: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully deleted build trigger: {trigger_id}")
#         logger.debug(f"Delete build trigger response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def get_build_trigger(project_id: str, location: str, trigger_id: str):
#     """Gets the details of a build trigger.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the trigger.
#         trigger_id: The ID of the trigger to get.
#     """
#     try:
#         logger.info(f"Getting details for build trigger '{trigger_id}' in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/triggers/{trigger_id}"
#         request = service.projects().locations().triggers().get(name=name)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error getting build trigger details: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully got details for build trigger: {trigger_id}")
#         logger.debug(f"Build trigger details: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def update_build_trigger(project_id: str, location: str, trigger_id: str, trigger_body: dict):
#     """Updates a build trigger.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the trigger.
#         trigger_id: The ID of the trigger to update.
#         trigger_body: The new trigger body.
#     """
#     try:
#         logger.info(f"Updating build trigger '{trigger_id}' in project '{project_id}' and location '{location}'.")
#         logger.debug(f"New trigger body: {trigger_body}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/triggers/{trigger_id}"
#         request = service.projects().locations().triggers().patch(name=name, body=trigger_body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error updating build trigger: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully updated build trigger: {trigger_id}")
#         logger.debug(f"Update build trigger response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def receive_trigger_callback(request: dict):
#     """Receives a trigger callback.

#     Args:
#         request: The request object.
#     """
#     try:
#         logger.info(f"Received trigger callback: {request}")
#         return {"message": "Successfully received trigger callback."}

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def create_worker_pool(project_id: str, location: str, worker_pool_body: dict):
#     """Creates a worker pool.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the worker pool.
#         worker_pool_body: The worker pool body.
#     """
#     try:
#         logger.info(f"Creating worker pool in project '{project_id}' and location '{location}'.")
#         logger.debug(f"Worker pool body: {worker_pool_body}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         parent = f"projects/{project_id}/locations/{location}"
#         request = service.projects().locations().workerPools().create(parent=parent, body=worker_pool_body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error creating worker pool: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully created worker pool.")
#         logger.debug(f"Create worker pool response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def delete_worker_pool(project_id: str, location: str, worker_pool_id: str):
#     """Deletes a worker pool.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the worker pool.
#         worker_pool_id: The ID of the worker pool to delete.
#     """
#     try:
#         logger.info(f"Deleting worker pool '{worker_pool_id}' in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/workerPools/{worker_pool_id}"
#         request = service.projects().locations().workerPools().delete(name=name)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error deleting worker pool: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully deleted worker pool: {worker_pool_id}")
#         logger.debug(f"Delete worker pool response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def get_worker_pool(project_id: str, location: str, worker_pool_id: str):
#     """Gets the details of a worker pool.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the worker pool.
#         worker_pool_id: The ID of the worker pool to get.
#     """
#     try:
#         logger.info(f"Getting details for worker pool '{worker_pool_id}' in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/workerPools/{worker_pool_id}"
#         request = service.projects().locations().workerPools().get(name=name)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error getting worker pool details: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully got details for worker pool: {worker_pool_id}")
#         logger.debug(f"Worker pool details: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def list_worker_pools(project_id: str, location: str):
#     """Lists all worker pools in a given location.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the worker pools.
#     """
#     try:
#         logger.info(f"Listing worker pools in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         parent = f"projects/{project_id}/locations/{location}"
#         request = service.projects().locations().workerPools().list(parent=parent)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error listing worker pools: {e}", exc_info=True)
#             return {"error": str(e)}

#         worker_pools = response.get("workerPools", [])
#         logger.info(f"Found {len(worker_pools)} worker pools.")
#         logger.debug(f"Worker pools: {worker_pools}")
#         return worker_pools

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def update_worker_pool(project_id: str, location: str, worker_pool_id: str, worker_pool_body: dict):
#     """Updates a worker pool.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the worker pool.
#         worker_pool_id: The ID of the worker pool to update.
#         worker_pool_body: The new worker pool body.
#     """
#     try:
#         logger.info(f"Updating worker pool '{worker_pool_id}' in project '{project_id}' and location '{location}'.")
#         logger.debug(f"New worker pool body: {worker_pool_body}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/workerPools/{worker_pool_id}"
#         request = service.projects().locations().workerPools().patch(name=name, body=worker_pool_body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error updating worker pool: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully updated worker pool: {worker_pool_id}")
#         logger.debug(f"Update worker pool response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def get_iam_policy(resource: str):
#     """Gets the IAM policy for a resource.

#     Args:
#         resource: The resource for which to get the IAM policy.
#     """
#     try:
#         logger.info(f"Getting IAM policy for resource '{resource}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         request = service.projects().triggers().getIamPolicy(resource=resource)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error getting IAM policy: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully got IAM policy for resource: {resource}")
#         logger.debug(f"IAM policy: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def set_iam_policy(resource: str, policy_body: dict):
#     """Sets the IAM policy for a resource.

#     Args:
#         resource: The resource for which to set the IAM policy.
#         policy_body: The new policy body.
#     """
#     try:
#         logger.info(f"Setting IAM policy for resource '{resource}'.")
#         logger.debug(f"New policy body: {policy_body}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         request = service.projects().triggers().setIamPolicy(resource=resource, body=policy_body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error setting IAM policy: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully set IAM policy for resource: {resource}")
#         logger.debug(f"Set IAM policy response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def test_iam_permissions(resource: str, permissions: list):
#     """Tests the IAM permissions for a resource.

#     Args:
#         resource: The resource for which to test the IAM permissions.
#         permissions: The permissions to test.
#     """
#     try:
#         logger.info(f"Testing IAM permissions for resource '{resource}'.")
#         logger.debug(f"Permissions to test: {permissions}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         body = {
#             "permissions": permissions
#         }
#         request = service.projects().triggers().testIamPermissions(resource=resource, body=body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error testing IAM permissions: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully tested IAM permissions for resource: {resource}")
#         logger.debug(f"Test IAM permissions response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def get_github_enterprise_config(project_id: str, location: str, config_id: str):
#     """Gets the details of a GitHub Enterprise config.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the config.
#         config_id: The ID of the config to get.
#     """
#     try:
#         logger.info(f"Getting details for GitHub Enterprise config '{config_id}' in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/githubEnterpriseConfigs/{config_id}"
#         request = service.projects().locations().githubEnterpriseConfigs().get(name=name)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error getting GitHub Enterprise config details: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully got details for GitHub Enterprise config: {config_id}")
#         logger.debug(f"GitHub Enterprise config details: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def create_github_enterprise_config(project_id: str, location: str, config_body: dict):
#     """Creates a GitHub Enterprise config.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the config.
#         config_body: The config body.
#     """
#     try:
#         logger.info(f"Creating GitHub Enterprise config in project '{project_id}' and location '{location}'.")
#         logger.debug(f"Config body: {config_body}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         parent = f"projects/{project_id}/locations/{location}"
#         request = service.projects().locations().githubEnterpriseConfigs().create(parent=parent, body=config_body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error creating GitHub Enterprise config: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully created GitHub Enterprise config.")
#         logger.debug(f"Create GitHub Enterprise config response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def delete_github_enterprise_config(project_id: str, location: str, config_id: str):
#     """Deletes a GitHub Enterprise config.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the config.
#         config_id: The ID of the config to delete.
#     """
#     try:
#         logger.info(f"Deleting GitHub Enterprise config '{config_id}' in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/githubEnterpriseConfigs/{config_id}"
#         request = service.projects().locations().githubEnterpriseConfigs().delete(name=name)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error deleting GitHub Enterprise config: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully deleted GitHub Enterprise config: {config_id}")
#         logger.debug(f"Delete GitHub Enterprise config response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def list_github_enterprise_configs(project_id: str, location: str):
#     """Lists all GitHub Enterprise configs in a given location.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the configs.
#     """
#     try:
#         logger.info(f"Listing GitHub Enterprise configs in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         parent = f"projects/{project_id}/locations/{location}"
#         request = service.projects().locations().githubEnterpriseConfigs().list(parent=parent)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error listing GitHub Enterprise configs: {e}", exc_info=True)
#             return {"error": str(e)}

#         configs = response.get("configs", [])
#         logger.info(f"Found {len(configs)} GitHub Enterprise configs.")
#         logger.debug(f"GitHub Enterprise configs: {configs}")
#         return configs

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def update_github_enterprise_config(project_id: str, location: str, config_id: str, config_body: dict):
#     """Updates a GitHub Enterprise config.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the config.
#         config_id: The ID of the config to update.
#         config_body: The new config body.
#     """
#     try:
#         logger.info(f"Updating GitHub Enterprise config '{config_id}' in project '{project_id}' and location '{location}'.")
#         logger.debug(f"New config body: {config_body}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/githubEnterpriseConfigs/{config_id}"
#         request = service.projects().locations().githubEnterpriseConfigs().patch(name=name, body=config_body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error updating GitHub Enterprise config: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully updated GitHub Enterprise config: {config_id}")
#         logger.debug(f"Update GitHub Enterprise config response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def get_repository(project_id: str, location: str, connection_id: str, repository_id: str):
#     """Gets the details of a repository.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the repository.
#         connection_id: The ID of the connection.
#         repository_id: The ID of the repository to get.
#     """
#     try:
#         logger.info(f"Getting details for repository '{repository_id}' in project '{project_id}', location '{location}', and connection '{connection_id}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/connections/{connection_id}/repositories/{repository_id}"
#         request = service.projects().locations().connections().repositories().get(name=name)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error getting repository details: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully got details for repository: {repository_id}")
#         logger.debug(f"Repository details: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def create_repository(project_id: str, location: str, connection_id: str, repository_body: dict):
#     """Creates a repository.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the repository.
#         connection_id: The ID of the connection.
#         repository_body: The repository body.
#     """
#     try:
#         logger.info(f"Creating repository in project '{project_id}', location '{location}', and connection '{connection_id}'.")
#         logger.debug(f"Repository body: {repository_body}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         parent = f"projects/{project_id}/locations/{location}/connections/{connection_id}"
#         request = service.projects().locations().connections().repositories().create(parent=parent, body=repository_body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error creating repository: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully created repository.")
#         logger.debug(f"Create repository response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def delete_repository(project_id: str, location: str, connection_id: str, repository_id: str):
#     """Deletes a repository.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the repository.
#         connection_id: The ID of the connection.
#         repository_id: The ID of the repository to delete.
#     """
#     try:
#         logger.info(f"Deleting repository '{repository_id}' in project '{project_id}', location '{location}', and connection '{connection_id}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/connections/{connection_id}/repositories/{repository_id}"
#         request = service.projects().locations().connections().repositories().delete(name=name)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error deleting repository: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully deleted repository: {repository_id}")
#         logger.debug(f"Delete repository response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def list_repositories(project_id: str, location: str, connection_id: str):
#     """Lists all repositories in a given connection.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the repositories.
#         connection_id: The ID of the connection.
#     """
#     try:
#         logger.info(f"Listing repositories in project '{project_id}', location '{location}', and connection '{connection_id}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         parent = f"projects/{project_id}/locations/{location}/connections/{connection_id}"
#         request = service.projects().locations().connections().repositories().list(parent=parent)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error listing repositories: {e}", exc_info=True)
#             return {"error": str(e)}

#         repositories = response.get("repositories", [])
#         logger.info(f"Found {len(repositories)} repositories.")
#         logger.debug(f"Repositories: {repositories}")
#         return repositories

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def get_repository_iam_policy(project_id: str, location: str, connection_id: str, repository_id: str):
#     """Gets the IAM policy for a repository.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the repository.
#         connection_id: The ID of the connection.
#         repository_id: The ID of the repository to get the IAM policy for.
#     """
#     try:
#         logger.info(f"Getting IAM policy for repository '{repository_id}' in project '{project_id}', location '{location}', and connection '{connection_id}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         resource = f"projects/{project_id}/locations/{location}/connections/{connection_id}/repositories/{repository_id}"
#         request = service.projects().locations().connections().repositories().getIamPolicy(resource=resource)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error getting repository IAM policy: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully got IAM policy for repository: {repository_id}")
#         logger.debug(f"Repository IAM policy: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def set_repository_iam_policy(project_id: str, location: str, connection_id: str, repository_id: str, policy_body: dict):
#     """Sets the IAM policy for a repository.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the repository.
#         connection_id: The ID of the connection.
#         repository_id: The ID of the repository to set the IAM policy for.
#         policy_body: The new policy body.
#     """
#     try:
#         logger.info(f"Setting IAM policy for repository '{repository_id}' in project '{project_id}', location '{location}', and connection '{connection_id}'.")
#         logger.debug(f"New policy body: {policy_body}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         resource = f"projects/{project_id}/locations/{location}/connections/{connection_id}/repositories/{repository_id}"
#         request = service.projects().locations().connections().repositories().setIamPolicy(resource=resource, body=policy_body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error setting repository IAM policy: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully set IAM policy for repository: {repository_id}")
#         logger.debug(f"Set repository IAM policy response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def test_repository_iam_permissions(project_id: str, location: str, connection_id: str, repository_id: str, permissions: list):
#     """Tests the IAM permissions for a repository.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the repository.
#         connection_id: The ID of the connection.
#         repository_id: The ID of the repository to test the IAM permissions for.
#         permissions: The permissions to test.
#     """
#     try:
#         logger.info(f"Testing IAM permissions for repository '{repository_id}' in project '{project_id}', location '{location}', and connection '{connection_id}'.")
#         logger.debug(f"Permissions to test: {permissions}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         resource = f"projects/{project_id}/locations/{location}/connections/{connection_id}/repositories/{repository_id}"
#         body = {
#             "permissions": permissions
#         }
#         request = service.projects().locations().connections().repositories().testIamPermissions(resource=resource, body=body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error testing repository IAM permissions: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully tested IAM permissions for repository: {repository_id}")
#         logger.debug(f"Test repository IAM permissions response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def get_connection(project_id: str, location: str, connection_id: str):
#     """Gets the details of a connection.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the connection.
#         connection_id: The ID of the connection to get.
#     """
#     try:
#         logger.info(f"Getting details for connection '{connection_id}' in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/connections/{connection_id}"
#         request = service.projects().locations().connections().get(name=name)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error getting connection details: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully got details for connection: {connection_id}")
#         logger.debug(f"Connection details: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def create_connection(project_id: str, location: str, connection_body: dict):
#     """Creates a connection.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the connection.
#         connection_body: The connection body.
#     """
#     try:
#         logger.info(f"Creating connection in project '{project_id}' and location '{location}'.")
#         logger.debug(f"Connection body: {connection_body}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         parent = f"projects/{project_id}/locations/{location}"
#         request = service.projects().locations().connections().create(parent=parent, body=connection_body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error creating connection: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully created connection.")
#         logger.debug(f"Create connection response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def delete_connection(project_id: str, location: str, connection_id: str):
#     """Deletes a connection.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the connection.
#         connection_id: The ID of the connection to delete.
#     """
#     try:
#         logger.info(f"Deleting connection '{connection_id}' in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/connections/{connection_id}"
#         request = service.projects().locations().connections().delete(name=name)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error deleting connection: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully deleted connection: {connection_id}")
#         logger.debug(f"Delete connection response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def list_connections(project_id: str, location: str):
#     """Lists all connections in a given location.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the connections.
#     """
#     try:
#         logger.info(f"Listing connections in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         parent = f"projects/{project_id}/locations/{location}"
#         request = service.projects().locations().connections().list(parent=parent)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error listing connections: {e}", exc_info=True)
#             return {"error": str(e)}

#         connections = response.get("connections", [])
#         logger.info(f"Found {len(connections)} connections.")
#         logger.debug(f"Connections: {connections}")
#         return connections

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def update_connection(project_id: str, location: str, connection_id: str, connection_body: dict):
#     """Updates a connection.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the connection.
#         connection_id: The ID of the connection to update.
#         connection_body: The new connection body.
#     """
#     try:
#         logger.info(f"Updating connection '{connection_id}' in project '{project_id}' and location '{location}'.")
#         logger.debug(f"New connection body: {connection_body}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         name = f"projects/{project_id}/locations/{location}/connections/{connection_id}"
#         request = service.projects().locations().connections().patch(name=name, body=connection_body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error updating connection: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully updated connection: {connection_id}")
#         logger.debug(f"Update connection response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def get_connection_iam_policy(project_id: str, location: str, connection_id: str):
#     """Gets the IAM policy for a connection.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the connection.
#         connection_id: The ID of the connection to get the IAM policy for.
#     """
#     try:
#         logger.info(f"Getting IAM policy for connection '{connection_id}' in project '{project_id}' and location '{location}'.")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         resource = f"projects/{project_id}/locations/{location}/connections/{connection_id}"
#         request = service.projects().locations().connections().getIamPolicy(resource=resource)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error getting connection IAM policy: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully got IAM policy for connection: {connection_id}")
#         logger.debug(f"Connection IAM policy: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def set_connection_iam_policy(project_id: str, location: str, connection_id: str, policy_body: dict):
#     """Sets the IAM policy for a connection.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the connection.
#         connection_id: The ID of the connection to set the IAM policy for.
#         policy_body: The new policy body.
#     """
#     try:
#         logger.info(f"Setting IAM policy for connection '{connection_id}' in project '{project_id}' and location '{location}'.")
#         logger.debug(f"New policy body: {policy_body}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         resource = f"projects/{project_id}/locations/{location}/connections/{connection_id}"
#         request = service.projects().locations().connections().setIamPolicy(resource=resource, body=policy_body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error setting connection IAM policy: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully set IAM policy for connection: {connection_id}")
#         logger.debug(f"Set connection IAM policy response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}

# @mcp.tool
# def test_connection_iam_permissions(project_id: str, location: str, connection_id: str, permissions: list):
#     """Tests the IAM permissions for a connection.

#     Args:
#         project_id: The ID of the Google Cloud project.
#         location: The location of the connection.
#         connection_id: The ID of the connection to test the IAM permissions for.
#         permissions: The permissions to test.
#     """
#     try:
#         logger.info(f"Testing IAM permissions for connection '{connection_id}' in project '{project_id}' and location '{location}'.")
#         logger.debug(f"Permissions to test: {permissions}")
#         credentials, project = google.auth.default(
#             scopes=["https://www.googleapis.com/auth/cloud-platform"]
#         )
#         service = discovery.build('cloudbuild', 'v1', credentials=credentials)

#         resource = f"projects/{project_id}/locations/{location}/connections/{connection_id}"
#         body = {
#             "permissions": permissions
#         }
#         request = service.projects().locations().connections().testIamPermissions(resource=resource, body=body)
#         try:
#             response = request.execute()
#         except Exception as e:
#             logger.error(f"Error testing connection IAM permissions: {e}", exc_info=True)
#             return {"error": str(e)}

#         logger.info(f"Successfully tested IAM permissions for connection: {connection_id}")
#         logger.debug(f"Test connection IAM permissions response: {response}")
#         return response

#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}", exc_info=True)
#         return {"error": str(e)}