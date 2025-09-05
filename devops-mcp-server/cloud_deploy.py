from app import mcp
import google.auth
from google.cloud import deploy_v1
from typing import Dict, Any, List

def _get_cloud_deploy_service():
    """Gets the Cloud Deploy service client."""
    credentials, _ = google.auth.default()
    return deploy_v1.CloudDeployClient(credentials=credentials)

@mcp.tool
def create_delivery_pipeline(project_id: str, location: str, delivery_pipeline_id: str, description: str = "") -> Dict[str, Any]:
    """Creates a new Cloud Deploy delivery pipeline.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the delivery pipeline.
        delivery_pipeline_id: The ID of the delivery pipeline to create.
        description: A description of the delivery pipeline.

    Returns:
        A dictionary containing a success message or an error message.
    """
    try:
        client = _get_cloud_deploy_service()

        parent = f"projects/{project_id}/locations/{location}"
        delivery_pipeline = {
            "description": description,
            "serial_pipeline": {
                "stages": []
            }
        }

        response = client.create_delivery_pipeline(
            parent=parent, delivery_pipeline=delivery_pipeline, delivery_pipeline_id=delivery_pipeline_id
        )
        result = response.result()

        return {"message": f"Successfully created Cloud Deploy delivery pipeline: {result}"}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def create_gke_target(project_id: str, location: str, target_id: str, gke_cluster: str, description: str = "") -> Dict[str, Any]:
    """Creates a new Cloud Deploy GKE target.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the target.
        target_id: The ID of the target to create.
        gke_cluster: The GKE cluster to deploy to.
        description: A description of the target.

    Returns:
        A dictionary containing a success message or an error message.
    """
    try:
        client = _get_cloud_deploy_service()

        parent = f"projects/{project_id}/locations/{location}"
        target = {
            "description": description,
            "gke": {
                "cluster": gke_cluster
            }
        }

        response = client.create_target(
            parent=parent, target=target, target_id=target_id
        )
        result = response.result()

        return {"message": f"Successfully created Cloud Deploy GKE target: {result}"}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def create_cloud_run_target(project_id: str, location: str, target_id: str, description: str = "") -> Dict[str, Any]:
    """Creates a new Cloud Deploy Cloud Run target.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the target.
        target_id: The ID of the target to create.
        description: A description of the target.

    Returns:
        A dictionary containing a success message or an error message.
    """
    try:
        client = _get_cloud_deploy_service()

        parent = f"projects/{project_id}/locations/{location}"
        target = {
            "description": description,
            "run": {
                "location": f"projects/{project_id}/locations/{location}"
            }
        }

        response = client.create_target(
            parent=parent, target=target, target_id=target_id
        )
        result = response.result()

        return {"message": f"Successfully created Cloud Deploy Cloud Run target: {result}"}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def create_rollout(project_id: str, location: str, delivery_pipeline_id: str, release_id: str, rollout_id: str, target_id: str) -> Dict[str, Any]:
    """Creates a new Cloud Deploy rollout.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the rollout.
        delivery_pipeline_id: The ID of the delivery pipeline.
        release_id: The ID of the release.
        rollout_id: The ID of the rollout to create.
        target_id: The ID of the target to deploy to.

    Returns:
        A dictionary containing a success message or an error message.
    """
    try:
        client = _get_cloud_deploy_service()

        parent = f"projects/{project_id}/locations/{location}/deliveryPipelines/{delivery_pipeline_id}/releases/{release_id}"
        rollout = {
            "target_id": target_id
        }

        response = client.create_rollout(
            parent=parent, rollout=rollout, rollout_id=rollout_id
        )
        result = response.result()

        return {"message": f"Successfully created Cloud Deploy rollout: {result}"}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def list_delivery_pipelines(project_id: str, location: str) -> Dict[str, Any]:
    """Lists all Cloud Deploy delivery pipelines.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the delivery pipelines.

    Returns:
        A dictionary containing a list of delivery pipelines or an error message.
    """
    try:
        client = _get_cloud_deploy_service()

        parent = f"projects/{project_id}/locations/{location}"

        response = client.list_delivery_pipelines(parent=parent)
        
        pipelines = []
        for pipeline in response:
            pipelines.append(pipeline.name)

        return {"pipelines": pipelines}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def list_targets(project_id: str, location: str) -> Dict[str, Any]:
    """Lists all Cloud Deploy targets.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the targets.

    Returns:
        A dictionary containing a list of targets or an error message.
    """
    try:
        client = _get_cloud_deploy_service()

        parent = f"projects/{project_id}/locations/{location}"

        response = client.list_targets(parent=parent)

        targets = []
        for target in response:
            targets.append(target.name)

        return {"targets": targets}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def list_releases(project_id: str, location: str, delivery_pipeline_id: str) -> Dict[str, Any]:
    """Lists all Cloud Deploy releases for a given delivery pipeline.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the releases.
        delivery_pipeline_id: The ID of the delivery pipeline.

    Returns:
        A dictionary containing a list of releases or an error message.
    """
    try:
        client = _get_cloud_deploy_service()

        parent = f"projects/{project_id}/locations/{location}/deliveryPipelines/{delivery_pipeline_id}"

        response = client.list_releases(parent=parent)

        releases = []
        for release in response:
            releases.append(release.name)

        return {"releases": releases}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def list_rollouts(project_id: str, location: str, delivery_pipeline_id: str, release_id: str) -> Dict[str, Any]:
    """Lists all Cloud Deploy rollouts for a given release.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the rollouts.
        delivery_pipeline_id: The ID of the delivery pipeline.
        release_id: The ID of the release.

    Returns:
        A dictionary containing a list of rollouts or an error message.
    """
    try:
        client = _get_cloud_deploy_service()

        parent = f"projects/{project_id}/locations/{location}/deliveryPipelines/{delivery_pipeline_id}/releases/{release_id}"

        response = client.list_rollouts(parent=parent)

        rollouts = []
        for rollout in response:
            rollouts.append(rollout.name)

        return {"rollouts": rollouts}

    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def promote_release(project_id: str, location: str, delivery_pipeline_id: str, release_id: str, to_target: str) -> Dict[str, Any]:
    """Promotes a Cloud Deploy release to a specified target.

    Args:
        project_id: The ID of the Google Cloud project.
        location: The location of the delivery pipeline.
        delivery_pipeline_id: The ID of the delivery pipeline.
        release_id: The ID of the release to promote.
        to_target: The ID of the target to promote to.

    Returns:
        A dictionary containing a success message or an error message.
    """
    try:
        client = _get_cloud_deploy_service()

        parent = f"projects/{project_id}/locations/{location}/deliveryPipelines/{delivery_pipeline_id}/releases/{release_id}"
        rollout = {
            "target_id": to_target
        }
        rollout_id = f"rollout-{release_id}-{to_target}"

        response = client.create_rollout(
            parent=parent, rollout=rollout, rollout_id=rollout_id
        )
        result = response.result()

        return {"message": f"Successfully created rollout to promote release: {result}"}

    except Exception as e:
        return {"error": str(e)}