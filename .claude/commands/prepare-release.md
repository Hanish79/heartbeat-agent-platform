Read CLAUDE.md first.

Review approved artifacts under:

documents/03-approved-outputs

Perform release readiness checks:

1. Confirm each artifact exists in artifact-register.csv.
2. Confirm approval status, approver and approval date are populated.
3. Confirm source traceability is valid.
4. Confirm no draft or temporary files are included.
5. Run the Heartbeat local CI pipeline.
6. Produce a release manifest containing:
   - Artifact ID
   - File name
   - Version
   - Sources
   - Related actions
   - Related decisions
   - Related risks
   - Approval details
   - SHA256 hash

Save the manifest under:
documents/04-draft-working-area/release-manifest.md

Do not create a Git tag.
Do not push.
Do not modify approved artifacts.