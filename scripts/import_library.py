#!/usr/bin/env python3
"""Import a flat Allegro export and record provenance without editing CAD binaries."""

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from allegro_export import devices, pin_mapping
from validate_library import FIELDS


NATIVE = {".dra", ".psm", ".ssm", ".fsm", ".osm", ".bsm", ".pad"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_write(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def key(value):
    return re.sub(r"\s+", "", value).casefold()


def bom_rows(path):
    result = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            # Source CSV ends with an otherwise empty form-feed line.
            if not (row.get("ID") or "").strip():
                continue
            if None in row or any(v is None for v in row.values()):
                raise ValueError("Malformed nonblank BOM row")
            identifier = row["ID"].strip()
            scope = "subassembly" if re.fullmatch(r"2\.1\.\d+", identifier) else (
                "alternative" if identifier.endswith(".D") else (
                "main_board" if re.fullmatch(r"2\.\d+", identifier) and row["Designator"] else "non_pcb"))
            result.append({"Source_ID": identifier, "Scope": scope,
                           "References": ";".join(s.strip() for s in row["Designator"].split(",") if s.strip()),
                           "Quantity": row["Quantity"], "MPN": row["MPN"],
                           "Manufacturer": row["Manufactor"], "Description": row["Description"]})
    return result


def category(symbol, description):
    text = (symbol + " " + description).upper()
    if symbol in {"R", "CC", "L", "FB", "CC_EMIFIL_3P", "NTC"} or "XTAL" in text:
        return "Passives"
    if any(s in text for s in ("HEADER", "USB", "FPC", "JST", "SD CARD")) and "IC " not in text:
        return "Connectors"
    if "TEST POINT" in text or "MOUNT" in text or "STUD" in text:
        return "Mechanical"
    if "AM62L" in text or "MPU" in text:
        return "MCU"
    if any(s in text for s in ("TPS", "BQ2", "LDO", "DCDC", "NMOS", "PMOS", "DIODE", "PMIC")) or symbol == "D":
        return "Power"
    return "Interfaces"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--update-generated-catalog", action="store_true")
    args = parser.parse_args()
    root, library, source = args.root.resolve(), args.library.resolve(), args.source.resolve()
    if (root / "metadata/personal-import.json").exists():
        raise ValueError("Personal models are integrated here. Use --root with a separate staging directory for baseline re-import; merge reviewed changes manually.")
    overrides_path = root / "metadata/footprint-overrides.json"
    overrides = json.loads(overrides_path.read_text(encoding="utf-8")) if overrides_path.exists() else {}
    parsed = devices(library)
    pins = pin_mapping(parsed)
    bom_path = source / "design/BeagleBadge_BOM.csv"
    bom = bom_rows(bom_path)
    previous = root / "reports/parts.generated.csv"
    if args.update_generated_catalog:
        if not previous.exists() or sha(previous) != sha(root / "parts.csv"):
            raise ValueError("parts.csv differs from its generated snapshot; refusing to overwrite personal edits")
    plan, inventory = [], []
    for path in sorted(library.iterdir()):
        if path.suffix.lower() not in NATIVE:
            continue
        folder = "padstacks" if path.suffix.lower() == ".pad" else "footprints"
        relative = folder + "/" + path.name
        plan.append((path, root / relative))
        inventory.append({"File": relative, "Type": path.suffix.lower(), "Bytes": path.stat().st_size,
                          "SHA256": sha(path), "Origin": "user_added" if path.stem == "r0805" else "board_export",
                          "License": "unconfirmed" if path.stem == "r0805" else "CC-BY-SA-4.0"})
    plan += [(source / "design/LICENSE", root / "sources/LICENSE"),
             (bom_path, root / "sources/BOM.csv"), (library / "devices.map", root / "sources/devices.map")]
    plan += [(library / r["Device_File"], root / "sources/devices" / r["Device_File"]) for r in parsed]
    plan += [(p, root / "sources/export-logs" / p.name) for p in library.glob("*.log*")]
    for src, dest in plan:
        if dest.exists() and sha(src) != sha(dest):
            raise ValueError(f"Refusing to overwrite a different existing file: {dest}")
    groups = defaultdict(list)
    for row in parsed:
        groups[(row["Symbol"], key(row["Package"]), key(row["Value"]))].append(row)
    psms = {p.stem.casefold(): p for p in library.glob("*.psm")}
    dras = {p.stem.casefold(): p for p in library.glob("*.dra")}
    # Locally generated symbols belong to the personal library, not the raw export.
    # Retain and index declared additions without copying back into the input folder.
    for name in overrides:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.+\-]*", name):
            raise ValueError(f"Invalid overridden footprint name: {name}")
        local = root / "footprints" / (name + ".psm")
        if name.casefold() not in psms and local.is_file():
            if name.casefold() not in dras or local.stat().st_size == 0:
                raise ValueError(f"Local PSM has no source DRA or is empty: {local}")
            psms[name.casefold()] = local
            inventory.append({"File": local.relative_to(root).as_posix(), "Type": ".psm",
                              "Bytes": local.stat().st_size, "SHA256": sha(local),
                              "Origin": "local_compiled", "License": "unconfirmed"})
    helpers = {p.stem.casefold() for p in library.iterdir() if p.suffix.lower() in {".ssm", ".fsm", ".osm", ".bsm"}}
    catalog, issues = [], []
    device_ids = {}
    for index, grouped in enumerate(groups.values(), 1):
        device = grouped[0]
        part_id = f"LIB-{index:04d}"
        package = key(device["Package"])
        matched = [b for b in bom if b["Scope"] == "main_board" and b["MPN"] and key(b["MPN"]) == key(device["Value"])]
        unique = matched[0] if len({(b['MPN'], b['Manufacturer'], b['Description']) for b in matched}) == 1 else None
        description = unique["Description"] if unique else f"{device['Symbol']}; {device['Value']}; {device['Package']}"
        record = {f: "" for f in FIELDS}
        record.update(Part_ID=part_id, Category=category(device["Symbol"], description),
                      Manufacturer=unique["Manufacturer"] if unique else "", MPN=unique["MPN"] if unique else "",
                      Description=description, Value=device["Value"], Symbol_Name=device["Symbol"],
                      PCB_Footprint=psms[package].stem if package in psms else device["Package"],
                      Footprint_DRA="footprints/" + dras[package].name if package in dras else "",
                      Footprint_PSM="footprints/" + psms[package].name if package in psms else "",
                      Source_URL="https://github.com/beagleboard/BeagleBadge", License_Notes="CC-BY-SA-4.0; attribution in sources/README.md",
                      Revision="R01", Status="draft", Notes="Symbol name from PCB device export; no OLB; pad dependencies and geometry unverified; device files=" + ";".join(d["Device_File"] for d in grouped))
        catalog.append(record)
        for row in grouped: device_ids[row["Device_File"]] = part_id
        for issue in ["symbol_library_missing", "pad_dependencies_not_verified", "geometry_not_verified"]:
            issues.append({"Item": part_id, "Issue": issue})
    footprints = []
    for name in sorted(set(psms) | (set(dras) - helpers)):
        source_dra, source_psm = dras.get(name), psms.get(name)
        status = "draft" if source_dra and source_psm else "missing_psm" if source_dra else "missing_dra"
        related = [r for r in catalog if key(r["PCB_Footprint"]) == name]
        if not related and source_dra:
            part_id = f"LIB-{len(catalog)+1:04d}"
            extra = {f: "" for f in FIELDS}
            extra.update(Part_ID=part_id, Category="Passives" if name.startswith("r") else "Mechanical",
                         Description=f"用户补充的 {source_dra.stem} 封装" + ("；待生成 PSM" if not source_psm else ""), PCB_Footprint=source_dra.stem,
                         Footprint_DRA="footprints/" + source_dra.name,
                         Footprint_PSM="footprints/" + source_psm.name if source_psm else "", Status="draft", Revision="R01",
                         License_Notes="User-added; source and license require confirmation",
                         Notes=("No compiled PSM; " if not source_psm else "") + "No device export; do not infer pin mapping from file name")
            catalog.append(extra)
            related = [extra]
        footprints.append({"PCB_Footprint": source_psm.stem if source_psm else source_dra.stem,
                           "DRA": "footprints/" + source_dra.name if source_dra else "",
                           "PSM": "footprints/" + source_psm.name if source_psm else "", "Status": status,
                           "Part_IDs": ";".join(r["Part_ID"] for r in related)})
        if status != "draft": issues.append({"Item": name, "Issue": status})
    bom_matches = []
    for record in catalog:
        override = overrides.get(record["PCB_Footprint"], {})
        pads = override.get("Padstack_Paths", [])
        for relative in pads:
            path = Path(relative)
            if path.is_absolute() or ".." in path.parts or path.parent.as_posix() != "padstacks" or path.suffix.lower() != ".pad":
                raise ValueError(f"Invalid declared padstack path: {relative}")
            if not (root / path).is_file() and not (library / path.name).is_file():
                raise ValueError(f"Declared padstack does not exist: {relative}")
        if pads: record["Padstack_Paths"] = ";".join(pads)
        if override.get("Review_Path"): record["Review_Path"] = override["Review_Path"]
        if override.get("Notes"): record["Notes"] += "; " + override["Notes"]
    for footprint in footprints:
        footprint["Padstack_Paths"] = ";".join(overrides.get(footprint["PCB_Footprint"], {}).get("Padstack_Paths", []))
    for b in bom:
        candidates = [d for d in parsed if b["MPN"] and key(d["Value"]) == key(b["MPN"])]
        bom_matches.append({"Source_ID": b["Source_ID"], "Scope": b["Scope"], "References": b["References"],
                            "MPN": b["MPN"], "Match": "device_value_equals_mpn" if candidates and b["Scope"] == "main_board" else "not_assigned",
                            "Candidate_Part_IDs": ";".join(sorted({device_ids[d["Device_File"]] for d in candidates})) if b["Scope"] == "main_board" else ""})
    # Commit copies only after all source text has been parsed and conflicts checked.
    for src, dest in plan:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists(): shutil.copyfile(src, dest)
    report = root / "reports"
    csv_write(report / "models.csv", list(inventory[0]), inventory)
    csv_write(report / "devices.csv", list(parsed[0]), parsed)
    csv_write(report / "pins.csv", list(pins[0]), pins)
    csv_write(report / "footprints.csv", list(footprints[0]), footprints)
    csv_write(report / "bom.normalized.csv", list(bom[0]), bom)
    csv_write(report / "bom-matches.csv", list(bom_matches[0]), bom_matches)
    csv_write(report / "issues.csv", ["Item", "Issue"], issues)
    csv_write(report / "parts.generated.csv", FIELDS, catalog)
    current = root / "parts.csv"
    with current.open(encoding="utf-8-sig", newline="") as f:
        existing = list(csv.DictReader(f))
    if not existing or args.update_generated_catalog:
        csv_write(current, FIELDS, catalog)
    summary = {"source_url": "https://github.com/beagleboard/BeagleBadge",
               "source_commit": subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip(),
               "source_license": "CC-BY-SA-4.0; actual design/LICENSE preserved",
               "bom_sha256": sha(bom_path), "counts": {"native_types": dict(Counter(r['Type'] for r in inventory)),
               "device_exports": len(parsed), "pin_mapping_rows": len(pins), "draft_records": len(catalog),
               "footprints": len(footprints), "bom_rows": len(bom), "bom_scopes": dict(Counter(b['Scope'] for b in bom))},
               "pending": [i for i in issues if i['Issue'].startswith('missing_')],
               "OLB_present": False, "geometry_modified": False}
    (root / "sources/provenance.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
