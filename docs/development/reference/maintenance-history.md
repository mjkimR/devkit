# Maintenance history commands

`CAP-DLV-maintenance-history` owns the command and record contracts. Use `uv run devkit maintenance history <command> --help` for flags.

```sh
uv run devkit maintenance history start --playbook weekly-report --scope "delivery" --into scratch/history --report scratch/report.md
uv run devkit maintenance history finish --run <returned-dir> --outcome completed --file scratch/evidence.txt
# Only after explicit user authority for owner/repo#maintenance-history:
uv run devkit maintenance history init --repository owner/repo --authority "<authority>"
uv run devkit maintenance history publish --run <returned-dir> --repository owner/repo --authority "<authority>" --file scratch/evidence.txt
uv run devkit maintenance history list --playbook weekly-report
uv run devkit maintenance history get --run-id <run-id> --file report.md
uv run devkit maintenance history update --run <returned-dir> --integration-state integrated --authority "<authority>"
```

The report path is fixed at start; finish freezes report and declared extra evidence. Publish selects only registered files, and retries retain destination and bytes. Get returns base64 bytes in one result. Later integration state is an amendment, preserving report and published record.
