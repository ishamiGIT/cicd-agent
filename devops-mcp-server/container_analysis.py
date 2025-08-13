from fastapi import APIRouter, HTTPException
import google.auth
from google.cloud.devtools import containeranalysis_v1
from mcp import mcp_capability

router = APIRouter()

@router.post("/containerAnalysis/listVulnerabilities/")
@mcp_capability(
    name="containerAnalysis/listVulnerabilities/",
    description="Lists vulnerabilities for a given image resource URL using Container Analysis.",
    parameters=[
        {
            "name": "project_id",
            "type": "string",
            "description": "The ID of the GCP project where the image resides.",
        },
        {
            "name": "resource_url",
            "type": "string",
            "description": "The full resource URL of the image (e.g., 'https://gcr.io/project-id/image-name@sha256:digest').",
        },
    ],
)
def list_vulnerabilities(project_id: str, resource_url: str):
    """
    Lists vulnerabilities for a given image resource URL using Container Analysis.
    """
    try:
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        client = containeranalysis_v1.ContainerAnalysisClient(credentials=credentials)

        # Construct the parent path for the project
        parent = f"projects/{project_id}"

        # List occurrences (vulnerabilities are a type of occurrence)
        response = client.list_occurrences(
            parent=parent, filter=f'resourceUrl="{resource_url}" AND kind="VULNERABILITY"'
        )

        vulnerabilities = []
        for occurrence in response.occurrences:
            vulnerabilities.append({
                "note_name": occurrence.note_name,
                "severity": occurrence.vulnerability.severity.name,
                "short_description": occurrence.vulnerability.short_description,
                "long_description": occurrence.vulnerability.long_description,
                "effective_severity": occurrence.vulnerability.effective_severity.name,
                "fix_available": occurrence.vulnerability.fix_available,
            })

        return {"vulnerabilities": vulnerabilities}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
