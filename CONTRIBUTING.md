# Contributing

SecData Forge keeps the default development path intentionally small.

## Local Checks

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m compileall -q src tests
python -m secdata_forge profile --input examples/flows/raw_open_security_flows.csv --config configs/security_flow.json
```

## Development Notes

- Keep the standard-library path working.
- Prefer config-driven dataset rules over hard-coded dataset names.
- Do not commit raw malware, private packet payloads, secrets, or personal data.
- Keep generated example artifacts small enough to review in pull requests.

