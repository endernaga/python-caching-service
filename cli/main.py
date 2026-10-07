import json
import sys
from pathlib import Path
from typing import Any

from .client import ApiClient
from .settings import CLISettings


def read_input(settings: CLISettings) -> dict[str, Any]:
    """Load the payload JSON from --json or --input."""
    if settings.json_payload is not None:
        return json.loads(settings.json_payload)

    assert settings.input is not None
    if str(settings.input) == "-":
        content = sys.stdin.read()
    else:
        content = settings.input.read_text(encoding="utf-8")

    return json.loads(content)


def write_output(result: Any, output: Path | None) -> None:
    """Write JSON results to --output or stdout."""
    content = json.dumps(result, indent=2)

    if output is None or str(output) == "-":
        sys.stdout.write(content + "\n")
    else:
        output.write_text(content + "\n", encoding="utf-8")


def main() -> None:
    """Create and read payloads against the caching service."""
    settings = CLISettings()
    data = read_input(settings)
    client = ApiClient(str(settings.host))

    results: list[dict[str, Any]] = []
    for _ in range(settings.repeat):
        payload_id = client.create_payload(data)
        payload = client.get_payload(payload_id)
        results.append(payload)

    write_output(results, settings.output)


if __name__ == "__main__":
    main()
