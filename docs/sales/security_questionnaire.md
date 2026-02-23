# Security Questionnaire (Summary)

## Data Storage
- On-prem storage with Postgres and MinIO
- Data isolation per club instance

## Access Control
- Network-level access via firewall rules
- Optional SSO integration at reverse proxy

## Transmission
- HTTPS termination via Nginx
- WebSocket over TLS

## Logging and Auditing
- Structured JSON logs
- Request ID tracking

## Backup
- Daily database backup recommended
- MinIO bucket snapshot schedule

## Compliance
- Designed for on-prem security policy alignment
- No external data transfer by default
