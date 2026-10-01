#!/usr/bin/env python3
"""Validate the SBOM against the CycloneDX 1.5 schema and our own sanity rules.

Needs: pip install "cyclonedx-python-lib[validation]"
"""
import json
import sys

from cyclonedx.schema import SchemaVersion
from cyclonedx.validation.json import JsonStrictValidator


def main(path):
    text = open(path).read()
    error = JsonStrictValidator(SchemaVersion.V1_5).validate_str(text)
    if error:
        sys.exit(f"SBOM schema validation failed:\n{error}")

    bom = json.loads(text)
    root = bom["metadata"]["component"]
    problems = []
    if root["type"] != "firmware":
        problems.append("root component must be of type 'firmware'")
    if not any(h["alg"] == "SHA-256" for h in root.get("hashes", [])):
        problems.append("root component has no SHA-256 hash")
    linked = [c for c in bom["components"] if c.get("scope") == "required"]
    if not linked:
        problems.append("no linked third-party component found "
                        "(map parsing may have silently failed)")
    for c in linked:
        if "version" not in c:
            problems.append(f"linked component {c['name']} has no version")
    if problems:
        sys.exit("SBOM sanity check failed:\n- " + "\n- ".join(problems))
    print(f"SBOM OK: {len(linked)} linked component(s), "
          f"{len(bom['components']) - len(linked)} test-only")


if __name__ == "__main__":
    main(sys.argv[1])
