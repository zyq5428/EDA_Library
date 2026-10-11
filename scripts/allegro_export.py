"""Read Allegro exported device text; never edit native geometry."""
import json
import re
import shlex

def devices(export):
    mapping = re.findall(r"^'([^']+)'\s+'([^']+)';", (export / "devices.map").read_text(), re.M)
    name_by_file = {filename: name for name, filename in mapping}
    result = []
    # devices.map lists renamed/collision-prone devices only, not every device file.
    for path in sorted(export.glob("*.txt")):
        filename = path.name
        device_name = name_by_file.get(filename, path.stem.upper())
        props = {}
        record = {"Device": device_name, "Device_File": filename, "Package": "", "Pin_Count": "",
                  "Symbol": "", "Value": "", "Pin_Order": "", "Pin_Use": "", "Functions": ""}
        functions = []
        orders, uses = {}, {}
        logical_lines, pending = [], ""
        for physical_line in path.read_text(encoding="utf-8-sig").splitlines():
            stripped = physical_line.strip()
            if not stripped or stripped.startswith("("):
                continue
            pending += " " + stripped.removesuffix(",")
            if not stripped.endswith(","):
                logical_lines.append(pending.strip())
                pending = ""
        if pending:
            raise ValueError(f"Unterminated continuation in {path}")
        for line in logical_lines:
            if not line.strip() or line.startswith("("):
                continue
            tokens = shlex.split(line, posix=True)
            if not tokens:
                continue
            if tokens[0] == "PACKAGE": record["Package"] = tokens[1]
            elif tokens[0] == "PINCOUNT": record["Pin_Count"] = tokens[1]
            elif tokens[0] == "PACKAGEPROP": props[tokens[1]] = " ".join(tokens[2:])
            elif tokens[0] == "PINORDER": orders[tokens[1]] = tokens[2:]
            elif tokens[0] == "PINUSE": uses[tokens[1]] = tokens[2:]
            elif tokens[0] == "FUNCTION": functions.append(tokens[1:])
        record["Symbol"] = props.get("PART_NAME", "")
        record["Value"] = props.get("VALUE", "")
        record["Functions"] = json.dumps(functions, ensure_ascii=False)
        record["Pin_Order"] = json.dumps(orders, ensure_ascii=False)
        record["Pin_Use"] = json.dumps(uses, ensure_ascii=False)
        if record["Package"]:
            result.append(record)
    return result

def pin_mapping(device_rows):
    result = []
    for device in device_rows:
        orders = json.loads(device["Pin_Order"])
        uses = json.loads(device["Pin_Use"])
        physical_pins = set()
        for gate, section, *pins in json.loads(device["Functions"]):
            names = orders[section]
            types = uses.get(section, [])
            if len(names) != len(pins) or (types and len(types) != len(pins)):
                raise ValueError(f"Inconsistent pin mapping: {device['Device_File']} {gate}")
            for index, (name, pin) in enumerate(zip(names, pins)):
                physical_pins.add(pin)
                result.append({"Device_File": device["Device_File"], "Symbol": device["Symbol"],
                               "Package": device["Package"], "Gate": gate, "Section": section,
                               "Pin_Name": name, "Physical_Pin": pin,
                               "Pin_Use": types[index] if types else ""})
        if len(physical_pins) != int(device["Pin_Count"]):
            raise ValueError(f"PINCOUNT mismatch: {device['Device_File']}")
    return result
