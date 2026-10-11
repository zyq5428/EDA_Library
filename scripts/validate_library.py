#!/usr/bin/env python3
"""Validate the catalog and file references; never parse Cadence binary models."""

import argparse
import csv
from pathlib import Path, PurePosixPath
import re
import sys


FIELDS = (
    "Part_ID Category Manufacturer MPN Description Value Parameters "
    "Symbol_Library Symbol_Name PCB_Footprint Footprint_DRA Footprint_PSM "
    "Padstack_Paths STEP_Path Datasheet_URL Source_URL License_Notes Revision "
    "Status Review_Path Workspace_Revision Notes"
).split()
STATUSES = {"draft", "reviewed", "board_tested", "deprecated"}
BASE_REQUIRED = {"Part_ID", "Category", "Description", "Status"}
READY_REQUIRED = BASE_REQUIRED | {
    "Manufacturer", "MPN", "Symbol_Library", "Symbol_Name", "PCB_Footprint",
    "Footprint_DRA", "Footprint_PSM", "Padstack_Paths", "License_Notes",
    "Revision", "Review_Path",
}
FILE_FIELDS = {
    "Symbol_Library": ("capture", {".olb"}),
    "Footprint_DRA": ("footprints", {".dra"}),
    "Footprint_PSM": ("footprints", {".psm"}),
    "STEP_Path": ("step", {".step", ".stp"}),
    "Review_Path": ("docs/components", {".md"}),
}


def read_csv(path, expected_headers=None):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        if expected_headers is not None and reader.fieldnames != expected_headers:
            raise ValueError(f"{path.name}: CSV 表头或顺序不匹配")
        if reader.fieldnames is None:
            raise ValueError(f"{path.name}: 缺少 CSV 表头")
        records = []
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"{path.name}: 第 {reader.line_num} 行列数不匹配")
            records.append((reader.line_num, {
                key: value.strip() for key, value in row.items()
            }))
        return records


def validate(root):
    errors = []
    try:
        category_rows = read_csv(root / "templates/categories.csv", ["Category", "Description"])
        category_names = [row["Category"] for _, row in category_rows]
        if not category_names or any(not name for name in category_names):
            raise ValueError("categories.csv: 类别不能为空")
        if len(category_names) != len(set(category_names)):
            raise ValueError("categories.csv: 类别重复")
        categories = set(category_names)
        records = read_csv(root / "parts.csv", FIELDS)
    except (OSError, UnicodeError, ValueError, csv.Error) as exc:
        return [str(exc)], 0

    def check_file(value, folder, suffixes, label):
        relative = PurePosixPath(value)
        if (
            relative.is_absolute() or ".." in relative.parts
            or "\\" in value or ":" in value
        ):
            errors.append(f"{label}: 必须是仓库内相对路径，使用 /")
            return
        if not value.startswith(folder + "/") or relative.suffix.lower() not in suffixes:
            errors.append(f"{label}: 目录或扩展名错误 ({value})")
            return
        target = root / value
        if not target.resolve().is_relative_to(root):
            errors.append(f"{label}: 路径指向仓库外")
        elif not target.is_file():
            errors.append(f"{label}: 文件不存在 ({value})")
        elif target.stat().st_size == 0:
            errors.append(f"{label}: 文件为空 ({value})")

    seen_ids = set()
    for line, row in records:
        label = f"parts.csv:{line} [{row['Part_ID'] or '无编号'}]"
        part_id = row["Part_ID"]
        if not re.fullmatch(r"[A-Z][A-Z0-9]*-[0-9]{4,}", part_id):
            errors.append(f"{label}: Part_ID 应类似 IC-0001")
        if part_id in seen_ids:
            errors.append(f"{label}: Part_ID 重复")
        seen_ids.add(part_id)
        if row["Category"] not in categories:
            errors.append(f"{label}: 未知 Category {row['Category']!r}")
        if row["Status"] not in STATUSES:
            errors.append(f"{label}: 未知 Status {row['Status']!r}")
        required = BASE_REQUIRED if row["Status"] == "draft" else READY_REQUIRED
        for field in sorted(required):
            if not row[field]:
                errors.append(f"{label}: 缺少 {field}")
        for field, (folder, suffixes) in FILE_FIELDS.items():
            if row[field]:
                check_file(row[field], folder, suffixes, f"{label} {field}")
        pads = row["Padstack_Paths"]
        if pads and pads != "NONE":
            for value in pads.split(";"):
                value = value.strip()
                if not value:
                    errors.append(f"{label}: Padstack_Paths 存在空条目")
                else:
                    check_file(value, "padstacks", {".pad"}, f"{label} Padstack_Paths")
        footprint = row["PCB_Footprint"]
        if footprint:
            if not re.fullmatch(r"MY_[A-Z0-9_]+", footprint):
                errors.append(f"{label}: PCB_Footprint 应以 MY_ 开头并使用大写字母、数字、下划线")
            for field in ("Footprint_DRA", "Footprint_PSM"):
                if row[field] and PurePosixPath(row[field]).stem != footprint:
                    errors.append(f"{label}: {field} 文件名与 PCB_Footprint 不一致")

    # Windows searches are commonly case insensitive: reject ambiguous file names.
    for folder, suffixes in (
        ("footprints", {".dra", ".psm"}),
        ("padstacks", {".pad"}),
        ("capture", {".olb"}),
        ("step", {".step", ".stp"}),
    ):
        seen_names = {}
        for path in sorted((root / folder).rglob("*")):
            if path.is_file() and path.suffix.lower() in suffixes:
                key = path.name.casefold()
                if key in seen_names:
                    errors.append(f"{folder}: 同名或大小写冲突 {seen_names[key]} / {path.relative_to(root)}")
                seen_names[key] = path.relative_to(root)
    return errors, len(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors, count = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"检查失败：{len(errors)} 项错误。", file=sys.stderr)
        return 1
    print(f"检查通过：{count} 个器件记录。仅验证清单与文件关联，不验证 Cadence 模型内部内容。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
