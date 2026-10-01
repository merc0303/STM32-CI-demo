#!/usr/bin/env python3
"""Generate a CycloneDX 1.5 SBOM for the firmware image (standard library only).

Sources of truth, so the SBOM cannot drift from the build:
  * linked components  -> archives the linker actually pulled in (firmware.map)
  * test-only deps     -> FetchContent entries in tests/CMakeLists.txt
  * versions           -> dpkg inside the build container
  * artifact identity  -> SHA-256 of the firmware ELF
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import uuid

# Linker archive -> Debian package that ships it (extend as the firmware grows).
ARCHIVE_PACKAGES = {
    "libc_nano.a": "libnewlib-arm-none-eabi",
    "libc.a": "libnewlib-arm-none-eabi",
    "libm.a": "libnewlib-arm-none-eabi",
    "libnosys.a": "libnewlib-arm-none-eabi",
    "libgcc.a": "gcc-arm-none-eabi",
}
BUILD_TOOLS = ("gcc-arm-none-eabi", "cmake")


def dpkg_version(package):
    if not shutil.which("dpkg-query"):
        return None
    r = subprocess.run(["dpkg-query", "-W", "-f=${Version}", package],
                       capture_output=True, text=True, check=False)
    return r.stdout.strip() or None if r.returncode == 0 else None


def distro():
    try:
        info = dict(l.strip().split("=", 1) for l in open("/etc/os-release") if "=" in l)
        return info["ID"].strip('"'), info["VERSION_ID"].strip('"')
    except (OSError, KeyError):
        return None, None


def deb_purl(name, version):
    d_id, d_ver = distro()
    purl = f"pkg:deb/{d_id or 'debian'}/{name}"
    if version:
        purl += "@" + urllib.parse.quote(version, safe="~+.-_")
    if d_id and d_ver:
        purl += f"?distro={d_id}-{d_ver}"
    return purl


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def linked_third_party_archives(map_path):
    """Archives from outside the project that the linker pulled objects from."""
    text = open(map_path, errors="replace").read()
    start = text.find("Archive member included")
    end = text.find("Discarded input sections", start)
    if start < 0 or end < 0:
        sys.exit(f"error: no archive section found in {map_path}")
    found = set()
    for path in re.findall(r"(\S+\.a)\(", text[start:end]):
        if os.path.isabs(path) and not path.startswith(os.getcwd() + os.sep):
            found.add(os.path.basename(path))
    return sorted(found)


def fetchcontent_deps(cmake_path):
    txt = open(cmake_path).read()
    deps = []
    for block in re.findall(r"FetchContent_Declare\((.*?)\)", txt, re.S):
        name = block.split()[0]
        repo = re.search(r"GIT_REPOSITORY\s+(\S+)", block)
        tag = re.search(r"GIT_TAG\s+(\S+)", block)
        if repo and tag:
            deps.append((name, repo.group(1), tag.group(1)))
    return deps


def github_purl(repo, tag):
    m = re.match(r"https://github\.com/([^/]+)/([^/.]+)(?:\.git)?$", repo)
    if not m:
        return None
    return f"pkg:github/{m.group(1).lower()}/{m.group(2).lower()}@{tag}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", required=True)
    ap.add_argument("--map", required=True)
    ap.add_argument("--cmake-tests", default="tests/CMakeLists.txt")
    ap.add_argument("--name", default="stm32-ci-demo")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    version = os.environ.get("SBOM_VERSION") or "0.0.0-unknown"
    root_ref = f"firmware:{args.name}"
    components, required_refs = [], []

    # 1. Third-party code that is linked into the image (scope: required)
    by_package = {}
    for archive in linked_third_party_archives(args.map):
        by_package.setdefault(ARCHIVE_PACKAGES.get(archive, archive), []).append(archive)
    for package, archives in sorted(by_package.items()):
        ver = dpkg_version(package)
        if ver is None:
            print(f"warning: no version found for {package}", file=sys.stderr)
        ref = deb_purl(package, ver)
        comp = {"type": "library", "bom-ref": ref, "name": package, "scope": "required",
                "purl": ref,
                "properties": [{"name": "stm32-ci-demo:linked-archives",
                                "value": ",".join(archives)}]}
        if ver:
            comp["version"] = ver
        components.append(comp)
        required_refs.append(ref)

    # 2. Test-only dependencies (scope: excluded -> not part of the firmware)
    for name, repo, tag in fetchcontent_deps(args.cmake_tests):
        purl = github_purl(repo, tag)
        comp = {"type": "library", "bom-ref": purl or f"{name}@{tag}", "name": name,
                "version": tag, "scope": "excluded",
                "externalReferences": [{"type": "vcs", "url": repo}],
                "properties": [{"name": "stm32-ci-demo:usage",
                                "value": "host unit tests only; not linked into the firmware"}]}
        if purl:
            comp["purl"] = purl
        components.append(comp)

    # 3. Build tools
    tools = []
    for package in BUILD_TOOLS:
        ver = dpkg_version(package)
        if ver:
            tools.append({"type": "application", "name": package, "version": ver})

    bom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.datetime.now(datetime.timezone.utc)
                         .strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tools": {"components": tools},
            "component": {
                "type": "firmware", "bom-ref": root_ref, "name": args.name,
                "version": version,
                "hashes": [{"alg": "SHA-256", "content": sha256(args.elf)}],
            },
        },
        "components": components,
        "dependencies": [{"ref": root_ref, "dependsOn": required_refs}]
                        + [{"ref": c["bom-ref"]} for c in components],
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(bom, f, indent=2)
        f.write("\n")
    print(f"wrote {args.out}: {len(required_refs)} linked, "
          f"{len(components) - len(required_refs)} test-only component(s)")


if __name__ == "__main__":
    main()
