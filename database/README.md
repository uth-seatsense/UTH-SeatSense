# Database

PostgreSQL initialization scripts in `init/` run automatically the first time
the Compose database volume is created. Demo rows are kept separately in
`seeds/` so they can be applied deliberately during development.

The current schema is an initial relational foundation, not a production
migration strategy. Use versioned migrations for subsequent schema changes.
