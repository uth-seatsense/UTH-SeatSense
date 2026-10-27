# Architecture decisions

## Initial service boundaries

- **Status:** Accepted for the project scaffold
- **Decision:** Keep the web UI, business API, and CV processing in separate
  service directories, with PostgreSQL as the shared persistence layer.
- **Reason:** The components have distinct responsibilities and runtime needs.
- **Follow-up:** Validate deployment, authentication, and inter-service
  communication requirements with the team.
