## Cloud Build Agent
- Knows cloudbuild.yaml best practices:

- - Use specific builder versions: Pin builder images to a specific version digest (e.g., `gcr.io/cloud-builders/gcloud@sha256:...`) instead of using floating tags like `latest` to ensure repeatable builds.

- - Minimize build step scope: Each step should perform a single, logical task. This improves caching, readability, and debugging.

- - Leverage substitutions: Use default and user-defined substitutions (`_VARIABLE_NAME`, `$VARIABLE_NAME`) for dynamic configurations instead of hardcoding values like project IDs or tags.

- - Optimize for caching: Structure steps so that frequently changing operations (like running tests) come after less frequently changing ones (like installing dependencies) to make better use of Cloud Build's layer caching.

Links to Cloud Build documentation: Cloud Build Documentation

Link to Cloud Build API documentation: Cloud Build API Documentation

Tools to access Cloud Build APIs: While Cloud Build doesn't expose a direct MCP (Managed Cloud Protocol) endpoint, you can interact with its API using:

Google Cloud CLI (gcloud builds ...)

Google Cloud Client Libraries (e.g., Python, Go, Node.js)

Direct REST/gRPC API calls

Cloud Deploy Agent
Knows clouddeploy.yaml best practices:

Automate promotion: Set up a serialPipeline with distinct stages (e.g., dev, staging, prod) to create a structured promotion path.

Use strategy.standard.verify = true: Enforce a verification job (e.g., running integration tests) before a release can be promoted to the next stage, ensuring quality gates.

Define targets clearly: Each Target in your pipeline should correspond to a specific runtime environment, such as a distinct GKE cluster or Cloud Run service.

Integrate Skaffold profiles: Use different Skaffold profiles (skaffold.yaml) for each deployment environment to manage environment-specific configurations like resource limits or environment variables.

Links to Cloud Deploy documentation: Cloud Deploy Documentation

Link to Cloud Deploy API documentation: Cloud Deploy API Documentation

Artifact Registry Agent
Knows Artifact Registry best practices:

Use immutable tags: For production deployments, push images with specific, non-changing tags like a git commit SHA (`sha-a1b2c3d`) or semantic version (`1.2.3`) instead of mutable tags like `latest`.

Employ granular permissions: Use repository-level IAM permissions to control access instead of project-wide roles. This ensures teams can only access the artifacts they need.

Enable vulnerability scanning: Configure automated scanning on your repositories to detect known vulnerabilities in your container images and OS packages.

Use remote repository caching: Create a remote repository to act as a pull-through cache for public registries like Docker Hub. This improves reliability and speed while centralizing dependency management.

Links to Artifact Registry documentation: Artifact Registry Documentation

Link to Artifact Registry API documentation: Artifact Registry API Documentation

Cloud Run Agent
Knows Cloud Run service deployment best practices:

Configure resource limits: Explicitly set CPU and memory limits (`--memory`, `--cpu`) to manage costs and ensure stable performance. Start with low values and adjust based on metrics.

Set concurrency: Adjust the `--concurrency` setting to define how many simultaneous requests a single instance handles. Higher concurrency can lower costs but requires a non-blocking, thread-safe application.

Secure services: Assign a dedicated IAM service account (`--service-account`) with the principle of least privilege. Use Secret Manager to inject secrets securely rather than using plaintext environment variables.

Configure health checks: Implement startup and liveness probes to ensure traffic is only routed to healthy, fully initialized container instances, preventing request failures during startup or crashes.

Links to Cloud Run documentation: Cloud Run Documentation

Link to Cloud Run API documentation: Cloud Run Admin API Documentation

GCP Terraform Agent
Knows GCP Terraform best practices:

Use a remote backend: Configure a Google Cloud Storage bucket as the backend for your Terraform state (.tfstate) file. This enables collaboration, state locking, and prevents state loss.

Structure with modules: Organize your infrastructure code into reusable modules for different components (e.g., networking, compute). This improves readability, reduces code duplication, and simplifies maintenance.

Isolate environments with workspaces: Use Terraform Workspaces to manage different environments (dev, staging, prod) with the same configuration but different variable values, preventing configuration drift.

Manage IAM carefully: Prefer granular IAM resources (`google_project_iam_member`) over authoritative ones (`google_project_iam_binding`). Authoritative resources can inadvertently remove default permissions needed by Google Cloud services.

Links to Terraform on GCP documentation: Google Provider for Terraform Documentation

Link to API documentation: Terraform interacts directly with the individual GCP service APIs (e.g., Compute Engine API, Cloud Storage API). The provider documentation above details which APIs are used for each resource.


CICD Agent

- Has access to all these tools, and knows when to call them.
- has custom instrctions on it makes a plan based on user prompt and then calls the other agents to finish the task.
- has a snapshot of the user envrironment.
 - asks user clarifying questions.