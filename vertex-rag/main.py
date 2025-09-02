import os
import tempfile

RAG_PATTERNS_CORPUS_ID = "projects/haroonc-exp/locations/us-east4/ragCorpora/5476377146882523136"
RAG_KNOWLEDGE_CORPUS_ID = "projects/haroonc-exp/locations/us-east4/ragCorpora/2017612633061982208"

KNOWLEDGE_RAG_SOURCES = [
    {
    "name":"GCP_DOCS",
    "extract":"devsite-content",
    "type":"webpage",
    "exclude_pattern":r'.*\?hl=.+$',
    "dir":"GCP_DOCS",
    "urls":[
        "https://cloud.google.com/developer-connect/docs/api/reference/rest",
        "https://cloud.google.com/developer-connect/docs/authentication",
        "https://cloud.google.com/build/docs/api/reference/rest",
        "https://cloud.google.com/deploy/docs/api/reference/rest",
        "https://cloud.google.com/artifact-analysis/docs/reference/rest",
        "https://cloud.google.com/artifact-registry/docs/reference/rest",
        "https://cloud.google.com/infrastructure-manager/docs/reference/rest",
        "https://cloud.google.com/docs/buildpacks/stacks",
        "https://cloud.google.com/docs/buildpacks/base-images",
        "https://cloud.google.com/docs/buildpacks/build-application",
        "https://cloud.google.com/docs/buildpacks/python",
        "https://cloud.google.com/docs/buildpacks/nodejs",
        "https://cloud.google.com/docs/buildpacks/java",
        "https://cloud.google.com/docs/buildpacks/go",
        "https://cloud.google.com/docs/buildpacks/ruby",
        "https://cloud.google.com/docs/buildpacks/php",
        "https://cloud.google.com/build/docs/build-config-file-schema",
        "https://cloud.google.com/build/docs/private-pools/use-in-private-network",
        "https://cloud.google.com/deploy/docs/config-files",
        "https://cloud.google.com/deploy/docs/deploy-app-gke",
        "https://cloud.google.com/deploy/docs/deploy-app-run",
        "https://cloud.google.com/deploy/docs/overview",
        "https://cloud.google.com/build/docs/build-push-docker-image",
        "https://cloud.google.com/build/docs/deploy-containerized-application-cloud-run",
        "https://cloud.google.com/build/docs/automate-builds",
        "https://cloud.google.com/build/docs/configuring-builds/create-basic-configuration",
        "https://cloud.google.com/build/docs/automating-builds/create-manage-triggers",
        "https://cloud.google.com/build/docs/building/build-containers",
        "https://cloud.google.com/build/docs/building/build-nodejs",
        "https://cloud.google.com/build/docs/building/build-java",
        "https://cloud.google.com/build/docs/deploying-builds/deploy-cloud-run",
        "https://cloud.google.com/build/docs/deploying-builds/deploy-gke"
        ]
    }
    ,
    {
    "name":"Python_Specific_Docs",
    "extract":"article",
    "type":"webpage",
    "url_pattern":r'.*(?<!\?hl=..)$',
    "dir":"Python_Specific_Docs",
    "urls":[
        "https://packaging.python.org/en/latest/guides/tool-recommendations/",
        "https://packaging.python.org/en/latest/guides/section-build-and-publish/",
        "https://packaging.python.org/en/latest/tutorials/managing-dependencies/",
        "https://packaging.python.org/en/latest/tutorials/installing-packages/",
        "https://packaging.python.org/en/latest/tutorials/packaging-projects/",
        "https://packaging.python.org/en/latest/overview/",
        "https://packaging.python.org/en/latest/guides/",
        "https://packaging.python.org/en/latest/guides/tool-recommendations",
        "https://packaging.python.org/en/latest/glossary/",
        "https://packaging.python.org/en/latest/key_projects/",
        "https://py-pkgs.org/08-ci-cd.html",
        "https://switowski.com/blog/ci-101/",
    ]
    }
    ,
    {
    "name":"cloud_builder_docs",
    "extract":"section",
    "type":"git_repo",
    "url_pattern":r'\.md$',
    "exclude_pattern":r'.*(vendor|third_party|.github).*$',
    "urls":[
        "https://github.com/GoogleCloudPlatform/cloud-builders/archive/refs/heads/master.zip",
        "https://github.com/GoogleCloudPlatform/cloud-builders-community/archive/refs/heads/master.zip"
        ]
    },
    {
    "name":"GCP_Terraform_Docs",
    "extract":"section",
    "type":"git_repo",
    "url_pattern":r'website/docs/.*\.markdown$',
    "exclude_pattern":r'.*(vendor|third_party|.github).*$',
    #"dir":"rag_data",
    "urls":[
        "https://github.com/hashicorp/terraform-provider-google/archive/refs/heads/main.zip"
        ]
    }
]

import os
import logging
from fetch_docs import *
from vertex_rag import upload_dir_to_rag

# Configure basic logging (e.g., to console with INFO level)
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # Load rag from checked in data
    PWD=os.path.dirname(__file__)
    upload_dir_to_rag(PWD,["patterns"],RAG_PATTERNS_CORPUS_ID)
    upload_dir_to_rag(PWD,["knowledge"],RAG_KNOWLEDGE_CORPUS_ID)

    # Download larger dataset and load in rag
    with tempfile.TemporaryDirectory() as tmpdirname:
        for source in KNOWLEDGE_RAG_SOURCES:
            if source["type"] == "webpage":
                collected_urls = download_websites(source,tmpdirname)
            elif source["type"] == "git_repo":
                download_git_repo(source,tmpdirname)
            else:
                logging.error("RAG Source type [%s] is not supported",source["type"])

        logging.info(f"Upload all files in these dirs to rag:{os.listdir(tmpdirname)}")
        upload_dir_to_rag(tmpdirname,os.listdir(tmpdirname),RAG_KNOWLEDGE_CORPUS_ID)
