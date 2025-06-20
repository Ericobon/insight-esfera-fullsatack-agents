"""
Tool for adding new data sources to a Vertex AI RAG corpus.
"""

import logging
import os
import re
import shutil
from typing import List, Tuple

import git  # Make sure 'pip install GitPython' is done
from google.adk.tools.tool_context import ToolContext
from google.cloud import storage  # Make sure 'pip install google-cloud-storage' is done
from vertexai import rag

# Assuming these are defined in rag_agent/config.py
from ..config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
)
# Assuming these are in rag_agent/tools/utils.py
from .utils import check_corpus_exists, get_corpus_resource_name

logger = logging.getLogger(__name__)

# --- Configuration for GitHub processing ---
# This bucket will be used for temporary uploads of GitHub repository contents.
# It should exist in your GCP project (e.g., 'insightesfera-companies').
# The 'temp_github_ingest' is a subfolder/prefix within that bucket.
TEMP_GCS_BUCKET_NAME = "insightesfera-companies"  # Your existing bucket name
TEMP_GCS_PREFIX = "temp_github_ingest"  # A subfolder within the bucket

# Environment variable name for GitHub Personal Access Token (PAT)
GITHUB_PAT_ENV_VAR = "GITHUB_PERSONAL_ACCESS_TOKEN"

# --- Helper function to process GitHub repositories ---
def _process_github_repo(repo_url: str) -> Tuple[List[str], str]:
    """
    Clones a GitHub repository, uploads its content (excluding .git) to a
    temporary GCS location, and returns a list of GCS URIs for these files.
    Handles private repositories using a PAT from environment variable.

    Args:
        repo_url (str): The URL of the GitHub repository (HTTPS or SSH format).

    Returns:
        Tuple[List[str], str]: A tuple containing:
            - A list of GCS URIs of the uploaded files.
            - An error message string if an error occurred, otherwise an empty string.
    """
    local_repo_dir = f"temp_repo_{os.urandom(8).hex()}"  # Unique temporary directory
    gcs_uris = []
    error_message = ""

    try:
        repo_url_to_clone = repo_url

        # Check for PAT for private repositories via HTTPS
        if GITHUB_PAT_ENV_VAR in os.environ:
            pat = os.environ[GITHUB_PAT_ENV_VAR]
            if repo_url.startswith("https://github.com/"):
                # Embed PAT into the HTTPS URL for authentication
                repo_url_to_clone = repo_url.replace(
                    "https://github.com/", f"https://oauth2:{pat}@github.com/"
                )
                logger.info(f"Using PAT for HTTPS cloning of {repo_url}.")
            else:
                logger.warning(
                    f"PAT provided but GitHub URL is not HTTPS: {repo_url}. "
                    "PAT authentication is typically for HTTPS. Attempting direct clone."
                )
        
        # 1. Clone the repository
        logger.info(f"Cloning GitHub repository from {repo_url_to_clone} to {local_repo_dir}...")
        git.Repo.clone_from(repo_url_to_clone, local_repo_dir)
        logger.info("GitHub repository cloning completed.")

        # 2. Upload content to Google Cloud Storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(TEMP_GCS_BUCKET_NAME)

        # Base path in GCS for this cloned repository's content
        repo_base_gcs_path = f"{TEMP_GCS_PREFIX}/{os.path.basename(local_repo_dir)}"

        for root, _, files in os.walk(local_repo_dir):
            for file_name in files:
                local_file_path = os.path.join(root, file_name)

                # Skip Git internal files and common ignore files
                if ".git" in local_file_path or ".DS_Store" in file_name or "__pycache__" in root:
                    continue
                
                # Construct the relative path for GCS blob name
                relative_path = os.path.relpath(local_file_path, local_repo_dir)
                gcs_blob_name = f"{repo_base_gcs_path}/{relative_path.replace(os.sep, '/')}" # Ensure '/' for GCS paths

                # Upload to GCS
                blob = bucket.blob(gcs_blob_name)
                blob.upload_from_filename(local_file_path)
                uri = f"gs://{TEMP_GCS_BUCKET_NAME}/{gcs_blob_name}"
                gcs_uris.append(uri)
                logger.info(f"Uploaded {local_file_path} to {uri}")

    except git.GitCommandError as e:
        error_message = f"Git command error cloning {repo_url}: {e}"
        logger.error(error_message, exc_info=True)
    except Exception as e:
        error_message = f"Unexpected error processing GitHub repository {repo_url}: {e}"
        logger.error(error_message, exc_info=True)
    finally:
        # Clean up the local temporary directory, even if an error occurred
        if os.path.exists(local_repo_dir):
            try:
                shutil.rmtree(local_repo_dir)
                logger.info(f"Temporary directory {local_repo_dir} removed.")
            except Exception as e:
                logger.error(f"Error removing temporary directory {local_repo_dir}: {e}")

    return gcs_uris, error_message

# --- Main add_data tool function ---
def add_data(
    corpus_name: str,
    paths: List[str],
    tool_context: ToolContext,
) -> dict:
    """
    Add new data sources to a Vertex AI RAG corpus.

    Args:
        corpus_name (str): The name of the corpus to add data to. If empty, the current corpus will be used.
        paths (List[str]): List of URLs or GCS paths to add to the corpus.
                            Supported formats:
                            - Google Drive: "https://drive.google.com/file/d/{FILE_ID}/view"
                            - Google Docs/Sheets/Slides: "https://docs.google.com/{type}/d/{FILE_ID}/..."
                            - Google Cloud Storage: "gs://{BUCKET}/{PATH}"
                            - GitHub Repository: "https://github.com/{user}/{repo}" or "git@github.com:{user}/{repo}.git"
                            Example: ["https://drive.google.com/file/d/123", "gs://my_bucket/my_files_dir", "https://github.com/my-org/my-repo"]
        tool_context (ToolContext): The tool context

    Returns:
        dict: Information about the added data and status
    """
    # Check if the corpus exists
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"Corpus '{corpus_name}' does not exist. Please create it first using the create_corpus tool.",
            "corpus_name": corpus_name,
            "paths": paths,
        }

    # Validate inputs
    if not paths or not all(isinstance(path, str) for path in paths):
        return {
            "status": "error",
            "message": "Invalid paths: Please provide a list of URLs, GCS paths, or GitHub repository URLs.",
            "corpus_name": corpus_name,
            "paths": paths,
        }

    # Lists to collect validated paths and track issues
    validated_paths_for_rag = []
    invalid_paths = []
    conversions_log = []
    github_processing_errors = []

    for path in paths:
        if not path or not isinstance(path, str):
            invalid_paths.append(f"{path} (Not a valid string)")
            continue

        # --- EXISTING LOGIC: Validate and convert Google Docs/Drive/GCS URLs ---
        docs_match = re.match(
            r"https:\/\/docs\.google\.com\/(?:document|spreadsheets|presentation)\/d\/([a-zA-Z0-9_-]+)(?:\/|$)",
            path,
        )
        if docs_match:
            file_id = docs_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths_for_rag.append(drive_url)
            conversions_log.append(f"{path} → {drive_url} (Google Docs/Sheets/Slides to Drive)")
            continue

        drive_match = re.match(
            r"https:\/\/drive\.google\.com\/(?:file\/d\/|open\?id=)([a-zA-Z0-9_-]+)(?:\/|$)",
            path,
        )
        if drive_match:
            file_id = drive_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths_for_rag.append(drive_url)
            if drive_url != path:
                conversions_log.append(f"{path} → {drive_url} (Drive URL normalization)")
            continue

        if path.startswith("gs://"):
            validated_paths_for_rag.append(path)
            continue

        # --- NEW LOGIC: Process GitHub repositories ---
        if path.startswith("https://github.com/") or path.startswith("git@github.com:"):
            gcs_uris, error = _process_github_repo(path)
            if gcs_uris:
                validated_paths_for_rag.extend(gcs_uris)
                conversions_log.append(f"GitHub repo {path} → {len(gcs_uris)} file(s) uploaded to GCS.")
            if error:
                github_processing_errors.append(f"GitHub: {path} - {error}")
            continue

        # If we reach here, the path was not in a recognized format
        invalid_paths.append(f"{path} (Invalid format or unsupported source)")

    # If no valid paths could be processed for RAG ingestion
    if not validated_paths_for_rag:
        final_message = "No valid data sources found for ingestion."
        if invalid_paths:
            final_message += f" Invalid paths were detected: {'; '.join(invalid_paths)}."
        if github_processing_errors:
            final_message += f" Errors occurred during GitHub processing: {'; '.join(github_processing_errors)}."
        
        return {
            "status": "error",
            "message": final_message.strip(),
            "corpus_name": corpus_name,
            "paths": paths,
            "invalid_paths": invalid_paths,
            "github_processing_errors": github_processing_errors,
        }

    try:
        # Get the corpus resource name (assuming this is handled by utils.py)
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Set up chunking configuration
        transformation_config = rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=DEFAULT_CHUNK_SIZE,
                chunk_overlap=DEFAULT_CHUNK_OVERLAP,
            ),
        )

        # Import files to the corpus
        logger.info(f"Importing {len(validated_paths_for_rag)} files to corpus '{corpus_name}'...")
        import_result = rag.import_files(
            corpus_resource_name,
            validated_paths_for_rag, # Use the list of GCS/Drive/Docs URIs
            transformation_config=transformation_config,
            max_embedding_requests_per_min=DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
        )
        logger.info(f"Import result: Imported {import_result.imported_rag_files_count} files, failed {import_result.failed_rag_files_count}.")

        # Set this as the current corpus if not already set (managed by ADK state)
        if not tool_context.state.get("current_corpus"):
            tool_context.state["current_corpus"] = corpus_name

        # Build the comprehensive success message
        message_parts = [
            f"Successfully added {import_result.imported_rag_files_count} file(s) to corpus '{corpus_name}'."
        ]
        if conversions_log:
            message_parts.append(f"({len(conversions_log)} paths converted: {'; '.join(conversions_log)})")
        if import_result.failed_rag_files_count > 0:
            message_parts.append(f"Note: {import_result.failed_rag_files_count} file(s) failed to import to RAG corpus.")
        if invalid_paths:
            message_parts.append(f"Skipped {len(invalid_paths)} invalid paths: {'; '.join(invalid_paths)}.")
        if github_processing_errors:
            message_parts.append(f"Encountered {len(github_processing_errors)} errors during GitHub processing: {'; '.join(github_processing_errors)}.")

        return {
            "status": "success",
            "message": " ".join(message_parts).strip(),
            "corpus_name": corpus_name,
            "files_added_to_corpus": import_result.imported_rag_files_count,
            "files_failed_to_add": import_result.failed_rag_files_count,
            "original_paths_provided": paths, # Original paths for reference
            "processed_gcs_drive_paths": validated_paths_for_rag, # Paths sent to Vertex AI RAG
            "invalid_paths_skipped": invalid_paths,
            "path_conversions_log": conversions_log,
            "github_errors_details": github_processing_errors,
        }

    except Exception as e:
        error_msg = f"Error adding data to corpus '{corpus_name}': {str(e)}"
        logger.error(error_msg, exc_info=True) # Log full traceback
        
        # Include context in the error return for better debugging
        return {
            "status": "error",
            "message": error_msg,
            "corpus_name": corpus_name,
            "paths": paths,
            "invalid_paths": invalid_paths,
            "github_processing_errors": github_processing_errors,
        }
