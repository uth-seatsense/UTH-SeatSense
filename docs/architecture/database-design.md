# Database design

The initial PostgreSQL schema defines:

- `rooms`: room identity, building, and capacity.
- `reservations`: room, time interval, requester, and workflow status.
- `occupancy_records`: timestamped observed occupancy by room.

Add reviewed, versioned migrations before making schema changes beyond the
initial development database.
