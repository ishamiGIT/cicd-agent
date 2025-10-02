import google.auth
from googleapiclient import discovery
from app import mcp
import time
from typing import Optional, Dict, Any, List
import logging
import subprocess
import json
import os

logger = logging.getLogger(__name__)

GCLOUD_EXECUTABLE = "gcloud_dci/google-cloud-sdk/bin/gcloud"

def _run_gcloud_command(command_args: List[str]) -> Dict[str, Any] | List[Dict[str, Any]] | Dict[str, Any]:
    """
    Private helper to execute a gcloud command and return parsed JSON or an error dict.
    
    Args:
        command_args: The arguments (excluding the executable name) to pass to gcloud.
    
    Returns:
        The parsed JSON output (list or dict) or a dict containing an "error" key.
    """
    full_command = [GCLOUD_EXECUTABLE] + command_args
    command_str = ' '.join(full_command)
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Preparing to execute: {command_str}")
    logger.info(f"Prinitng full_command: {full_command}")

    try:
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            check=True,  # Raise CalledProcessError on non-zero exit code
            timeout=300,  # 5 minute timeout for safety
            shell=False
        )
        
        raw_json_output = result.stdout.strip()
        
        if not raw_json_output:
            logger.warning(f"Command executed successfully but returned no output for: {command_str}")
            # Assume list commands return an empty list, and describe commands return an empty dict
            return [] if 'list' in command_args else {}
            
        try:
            # Parse the JSON output
            parsed_json = json.loads(raw_json_output)
            return parsed_json
        except json.JSONDecodeError:
            error_msg = f"Could not parse output as JSON for command: {command_str}. Raw start: {raw_json_output[:100]}..."
            logger.error(error_msg)
            return {"error": error_msg}

    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed (Code {e.returncode}). STDERR: {e.stderr.strip()}"
        logger.error(f"Error executing command: {command_str}. {error_msg}")
        return {"error": error_msg}
    except FileNotFoundError:
        error_msg = f"The executable '{GCLOUD_EXECUTABLE}' was not found. Ensure it is in your system PATH."
        logger.error(error_msg)
        return {"error": error_msg}
    except subprocess.TimeoutExpired:
        error_msg = f"Command timed out after 300 seconds: {command_str}"
        logger.error(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg, exc_info=True)
        return {"error": error_msg}

@mcp.tool
def list_deployment_events(insights_config_id: str,
    location: str,
    project_id: str
    ) -> List[Dict[str, Any]] | Dict[str, Any]:
    """Lists Deployment Events of an Insights Config

    Args:
        insights_config: The name of the Insights Config.
        project_id: The ID of the Google Cloud project.
        location: The location of the insghts config.
    
    Returns:
        A dictionary containing a list of deployment events.

    gcloud_dci alpha developer-connect insights-configs deployment-events list \
    --insights-config=view-test-ic \
    --location=us-central1 \
    --project=ishamirulinda-sdlc \
    --sort-by=~deployTime \
    --format=json
    """
    logger.info(f"Listing deployment events for config '{insights_config_id}' in project '{project_id}'.")
    
    command_args = [
        'alpha', 'developer-connect', 'insights-configs', 'deployment-events', 'list',
        f'--insights-config={insights_config_id}',
        f'--location={location}',
        f'--project={project_id}',
        '--sort-by=~deployTime',
        '--format=json'
    ]
    return _run_gcloud_command(command_args)

@mcp.tool
def describe_deployment_event(deployment_id: str,
    insights_config_id: str,
    location: str,
    project_id: str
    ) -> Dict[str, Any]:
    """Describe a single Deployment Event of an Insights Config

    This command can tell you specifics about a particular deployment event, including vulnerabilites that it's subject to 
    and packages that are included.

    You can obtain the <DEPLOYMENT_ID> by the list_deployment_events function and extrapolating from the name field the DEPLOYMENT_ID.
    For example, from this name:
    "name": "projects/<PROJECT_ID>/locations/<LOCATION>/insightsConfigs/<NISIGHTS_CONFIG>/deploymentEvents/1a2b3c4d5e6f7g8h9i0j"
    the DEPLOYMENT_ID = 1234567890

    Args:
        insights_config: The name of the Insights Config.
        project_id: The ID of the Google Cloud project.
        location: The location of the insghts config.
    
    Returns:
        A dictionary containing a single deployment event.

    gcloud_dci alpha developer-connect insights-configs deployment-events describe <DEPLOYMENT_ID>  \
    --insights-config=view-test-ic \
    --location=us-central1 \
    --project=ishamirulinda-sdlc \
    --format=json
    """
    logger.info(f"Describing SDLC context for deployment ID '{deployment_id}' in project '{project_id}'.")
    
    command_args = [
        'alpha', 'developer-connect', 'insights-configs', 'deployment-events', 'describe',
        deployment_id,
        f'--insights-config={insights_config_id}',
        f'--location={location}',
        f'--project={project_id}',
        '--format=json'
    ]
    
    return _run_gcloud_command(command_args)

@mcp.tool
def describe_deployment_diff_content(deployment_id: str,
    insights_config_id: str,
    location: str,
    project_id: str
    ) -> Dict[str, Any]:
    """Show the diff content of a single Deployment Event and the previously running one of an Insights Config

    Use to find vulnerability changes, package changes that are present in the newer deployment.

    You can obtain the <DEPLOYMENT_ID> by the list_deployment_events function and extrapolating from the name field the DEPLOYMENT_ID.
    For example, from this name:
    "name": "projects/<PROJECT_ID>/locations/<LOCATION>/insightsConfigs/<NISIGHTS_CONFIG>/deploymentEvents/1a2b3c4d5e6f7g8h9i0j"
    the DEPLOYMENT_ID = 1234567890

    Args:
        insights_config: The name of the Insights Config.
        project_id: The ID of the Google Cloud project.
        location: The location of the insghts config.
    
    Returns:
        A dictionary containing diff information of the deployment event.

    gcloud_dci alpha developer-connect insights-configs deployment-events describe --show-previous-diff <DEPLOYMENT_ID>  \
    --insights-config=view-test-ic \
    --location=us-central1 \
    --project=ishamirulinda-sdlc \
    --format=json

    example output should be:
    Found previous deployment: projects/66214305248/locations/us-central1/insightsConfigs/view-api-ic/deploymentEvents/b49025e057f1150db0d93e612156afafeabeb6c442e1c6aee86394926b50bf7c
    {
    "artifactDiffs": {
        "newArtifacts": [
        "us-central1-docker.pkg.dev/ishamirulinda-sdlc/sdlc-demo/recommendation-app@sha256:0a5a81d5a5a8e68d9783bdab3026af0b4885fde34ff24bcda6bca31abc765a99"
        ],
        "packageDiff": {
        "addedPackages": "click==8.1.8, flask==2.0.0, itsdangerous==2.2.0, jinja2==3.1.6, markupsafe==3.0.3, werkzeug==3.1.3"
        },
        "vulnerabilityDiff": {
        "addedVulnerabilities": "CVE-2023-30861"
        }
    },
    "gitDiffUri": "https://github.com/sdlc-graph/sdlc-test-project/compare/1a773a773a7e2b4570755a4f50aea1f9acd1d7fb...45b6b2403cfabbab4a0998335d778d242ef80a94"
    }
    """
    logger.info(f"Describing diff context for deployment ID '{deployment_id}' in project '{project_id}'.")
    
    command_args = [
        'alpha', 'developer-connect', 'insights-configs', 'deployment-events', 'describe',
        '--show-previous-diff',
        deployment_id,
        f'--insights-config={insights_config_id}',
        f'--location={location}',
        f'--project={project_id}',
        '--format=json'
    ]
    
    return _run_gcloud_command(command_args)
