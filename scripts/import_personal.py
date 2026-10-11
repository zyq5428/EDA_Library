#!/usr/bin/env python3
"""Merge a user's OLB and FPX exports while preserving native names and existing data."""

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re
import shlex
import shutil

from capture_library import package_streams, ascii_tokens
from import_library import csv_write, sha
from validate_library import FIELDS


def files_by_name(paths):
    result = {}
    for p in sorted(paths):
        key = p.name.casefold()
        if key in result and sha(result[key]) != sha(p):
            raise ValueError(f"Conflicting input names: {result[key]} and {p}")
        result[key] = p
    return result


def script_references(paths):
    result = defaultdict(lambda: {"pads": set(), "steps": set(), "scripts": []})
    for path in sorted(paths):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        match = re.search(r'newdrawfillin\s+"([^"]+\.dra)"\s+"Package Symbol"', text, re.I)
        if not match: continue
        name = Path(match[1]).stem.casefold()
        info = result[name]
        info["scripts"].append(path)
        info["pads"].update(re.findall(r"(?im)^FORM\s+mini\s+pad_name\s+(\S+)", text))
        for line in text.splitlines():
            if re.match(r"(?i)^FORM\s+pkgmap3d\s+stplist\s+", line):
                tokens = shlex.split(line)
                if tokens[-1].lower().endswith((".step", ".stp")): info["steps"].add(tokens[-1])
    return result


def family(name):
    name = name.upper()
    if name.startswith(("RES", "CAP", "XTAL")) or "MHZ" in name or "KHZ" in name: return "Passives"
    if name.startswith(("HEADER", "HDR", "USB", "HC-TYPE")): return "Connectors"
    if name.startswith(("MTG", "SCREW")): return "Mechanical"
    if name.startswith("STM32"): return "MCU"
    if name.startswith(("RT90", "TP40", "DIO", "SOD", "SOT", "TVS", "ESD", "TR_")): return "Power"
    return "Interfaces"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--olb", type=Path, required=True)
    parser.add_argument("--fpx", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root, fpx, olb = args.root.resolve(), args.fpx.resolve(), args.olb.resolve()
    streams = package_streams(olb)
    paths = [p for p in fpx.rglob("*") if p.is_file()]
    steps = files_by_name(p for p in paths if p.suffix.lower() in {".step", ".stp"})
    pads = files_by_name(p for p in paths if p.suffix.lower()==".pad")
    models = files_by_name(p for p in paths if p.suffix.lower() in {".dra", ".psm", ".ssm", ".fsm", ".osm"})
    refs = script_references(p for p in paths if p.suffix.lower()==".scr")
    plan, manifest, conflicts = [], [], []
    active = {p.name.casefold(): p for p in (root/"footprints").iterdir() if p.is_file()}
    conflict_stems = {p.stem.casefold() for k,p in models.items() if k in active and sha(p)!=sha(active[k])}
    def add(src, destination, role):
        plan.append((src,destination))
        manifest.append({"Source": src.relative_to(fpx).as_posix() if src.is_relative_to(fpx) else src.name,
                         "File": destination.relative_to(root).as_posix(), "Role": role,
                         "Bytes": src.stat().st_size, "SHA256": sha(src)})
    for filename,p in models.items():
        if p.stem.casefold() in conflict_stems:
            dest=root/"alternatives"/p.stem.casefold()/p.name
            conflicts.append({"Name":p.name, "Existing":active[filename].relative_to(root).as_posix() if filename in active else "",
                              "Alternative":dest.relative_to(root).as_posix(), "Resolution":"preserve existing; rename alternative inside Cadence before shared use"})
        else: dest=active.get(filename,root/"footprints"/p.name)
        add(p,dest,"native_model")
    for p in pads.values():
        existing={q.name.casefold():q for q in (root/"padstacks").iterdir() if q.is_file()}
        dest=existing.get(p.name.casefold(),root/"padstacks"/p.name)
        add(p,dest,"padstack")
    for p in steps.values():
        existing={q.name.casefold():q for q in (root/"step").iterdir() if q.is_file()}
        add(p,existing.get(p.name.casefold(),root/"step"/p.name),"3d_model")
    add(olb,root/"capture"/olb.name,"capture_library")
    for p in paths:
        if p.suffix.lower()==".fpx": add(p,root/"projects"/p.name,"fpx_project")
        elif p.suffix.lower() in {".scr", ".txt", ".bat", ".psx", ".xml"} or '.log' in p.suffix.lower() or '.rpt' in p.suffix.lower():
            add(p,root/"projects/exports"/p.relative_to(fpx),"generation_reference")
    # Fail before any write if an existing target would be changed.
    target_hashes = {}
    for src,dest in plan:
        if dest in target_hashes and target_hashes[dest]!=sha(src): raise ValueError(f"Duplicate different destinations: {dest}")
        target_hashes[dest]=sha(src)
        if dest.exists() and sha(dest)!=sha(src): raise ValueError(f"Refusing to overwrite personal file: {dest}")
    current = list(csv.DictReader((root/"parts.csv").open(encoding="utf-8-sig",newline="")))
    previous = root/"reports/personal-parts.generated.csv"
    if previous.exists():
        old=list(csv.DictReader(previous.open(encoding="utf-8-sig",newline="")))
        byid={r['Part_ID']:r for r in current}
        if any(byid.get(r['Part_ID'])!=r for r in old):
            raise ValueError("Personal catalog rows were edited; refusing to regenerate them")
        current=[r for r in current if r['Part_ID'] not in {r['Part_ID'] for r in old}]
    generated, fp_report, issues, symbol_report = [], [], [], []
    psm_by_stem={p.stem.casefold():p for p in models.values() if p.suffix.lower()=='.psm'}
    dra_by_stem={p.stem.casefold():p for p in models.values() if p.suffix.lower()=='.dra'}
    fp_links={}
    for index,(name,psm) in enumerate(sorted(psm_by_stem.items()),1):
        part={f:"" for f in FIELDS};part_id=f"FOOT-{index:04d}"
        reference=refs[name];problem=[]
        pad_paths=[]
        for pad in sorted(reference['pads']):
            source_pad=pads.get((pad+'.pad').casefold())
            if source_pad: pad_paths.append('padstacks/'+source_pad.name)
            else: problem.append('missing_script_pad:'+pad)
        step_paths=[]
        for step in sorted(reference['steps']):
            source_step=steps.get(step.casefold())
            if source_step: step_paths.append('step/'+source_step.name)
            else: problem.append('missing_script_step:'+step)
        dra=dra_by_stem.get(name)
        if not dra:problem.append('missing_dra')
        if name in conflict_stems:problem.append('same_name_different_geometry')
        if not reference['scripts']:problem.append('generation_script_missing')
        links={'Footprint_DRA':'footprints/'+dra.name if dra and name not in conflict_stems else '',
               'Footprint_PSM':'footprints/'+psm.name if name not in conflict_stems else '',
               'Padstack_Paths':';'.join(pad_paths), 'STEP_Path':step_paths[0] if len(step_paths)==1 else ''}
        fp_links[name]=links
        part.update(Part_ID=part_id,Category=family(psm.stem),Description='个人封装 '+psm.stem,
                    PCB_Footprint=psm.stem if name not in conflict_stems else '',Revision='R01',Status='draft',
                    License_Notes='User-provided Footprint Expert outputs; no public redistribution license asserted',
                    Notes=('PAD and STEP references from generation script; native mapping and geometry unverified; '+ ';'.join(problem)).rstrip('; '),**links)
        generated.append(part)
        fp_report.append({'Part_ID':part_id,'PCB_Footprint':psm.stem,'DRA':links['Footprint_DRA'],'PSM':links['Footprint_PSM'],
                          'Padstack_Paths':links['Padstack_Paths'],'STEP_Path':links['STEP_Path'],
                          'Scripts':';'.join(p.relative_to(fpx).as_posix() for p in reference['scripts']),
                          'Issues':';'.join(problem)})
        issues.extend({'Item':part_id,'Issue':p} for p in problem)
    active_psms={p.stem.casefold():p for p in (root/'footprints').glob('*.psm')}
    active_psms.update({k:p for k,p in psm_by_stem.items() if k not in conflict_stems})
    active_dras={p.stem.casefold():p for p in (root/'footprints').glob('*.dra')}
    active_dras.update({k:p for k,p in dra_by_stem.items() if k not in conflict_stems})
    for index,(name,raw) in enumerate(sorted(streams.items()),1):
        tokens=ascii_tokens(raw)
        candidates=sorted({t.casefold() for t in tokens if t.casefold() in active_psms})
        matched=candidates[0] if len(candidates)==1 and candidates[0] not in conflict_stems else None
        part={f:'' for f in FIELDS};part_id=f'SYM-{index:04d}'
        part.update(Part_ID=part_id,Category=family(name),Description='个人原理图符号 '+name,
                    Symbol_Library='capture/'+olb.name,Symbol_Name=name,Revision='R01',Status='draft',
                    License_Notes='User-created library; no public redistribution license asserted',
                    Notes='OLB CFB package name confirmed; footprint candidate from embedded ASCII token; property semantics and pin mapping unverified')
        if matched:
            part['PCB_Footprint']=active_psms[matched].stem
            part['Footprint_PSM']='footprints/'+active_psms[matched].name
            if matched in active_dras:part['Footprint_DRA']='footprints/'+active_dras[matched].name
            for field in ['Padstack_Paths','STEP_Path']:part[field]=fp_links.get(matched,{}).get(field,'')
            # Carry known personal declarations for pre-existing footprints.
            declarations=json.loads((root/'metadata/footprint-overrides.json').read_text())
            if matched in declarations and not part['Padstack_Paths']:
                part['Padstack_Paths']=';'.join(declarations[matched].get('Padstack_Paths',[]))
        problem='same_name_footprint_conflict' if any(c in conflict_stems for c in candidates) else '' if matched else 'footprint_reference_unresolved'
        if problem:issues.append({'Item':part_id,'Issue':problem})
        symbol_report.append({'Part_ID':part_id,'Symbol_Name':name,'Matched_Footprint':part['PCB_Footprint'],
                              'Match_Evidence':'unique embedded name token' if matched else '',
                              'Issues':problem,'Stream_Strings':json.dumps(tokens,ensure_ascii=False)})
        generated.append(part)
    if {r['Part_ID'] for r in current}.intersection(r['Part_ID'] for r in generated):raise ValueError('Generated ID collision')
    for src,dest in plan:
        dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():shutil.copyfile(src,dest)
    csv_write(root/'parts.csv',FIELDS,current+generated)
    csv_write(previous,FIELDS,generated)
    csv_write(root/'reports/personal-models.csv',list(manifest[0]),manifest)
    csv_write(root/'reports/personal-footprints.csv',list(fp_report[0]),fp_report)
    csv_write(root/'reports/personal-symbols.csv',list(symbol_report[0]),symbol_report)
    csv_write(root/'reports/personal-issues.csv',['Item','Issue'],issues)
    csv_write(root/'reports/conflicts.csv',['Name','Existing','Alternative','Resolution'],conflicts)
    all_parts = current + generated
    inventory = []
    for folder in ['footprints', 'padstacks', 'capture', 'step']:
        for path in sorted((root / folder).iterdir()):
            if path.is_file() and path.suffix.lower() != '.md':
                inventory.append({'File':path.relative_to(root).as_posix(), 'Type':path.suffix.lower(),
                                  'Bytes':path.stat().st_size, 'SHA256':sha(path)})
    csv_write(root/'reports/library-models.csv',['File','Type','Bytes','SHA256'],inventory)
    complete_dras = {p.stem.casefold(): p for p in (root/'footprints').iterdir() if p.suffix.lower()=='.dra'}
    footprints = []
    for path in sorted((root/'footprints').iterdir()):
        if path.suffix.lower() != '.psm': continue
        dra = complete_dras.get(path.stem.casefold())
        footprints.append({'PCB_Footprint':path.stem,
                           'DRA':dra.relative_to(root).as_posix() if dra else '',
                           'PSM':path.relative_to(root).as_posix(),
                           'Status':'draft' if dra else 'draft_missing_dra',
                           'Part_IDs':';'.join(r['Part_ID'] for r in all_parts if r['PCB_Footprint'].casefold()==path.stem.casefold())})
    csv_write(root/'reports/library-footprints.csv',['PCB_Footprint','DRA','PSM','Status','Part_IDs'],footprints)
    totals = {'active_files':len(inventory), 'file_types':dict(Counter(r['Type'] for r in inventory)),
              'active_footprints':len(footprints), 'catalog_rows':len(all_parts)}
    (root/'metadata/library-summary.json').write_text(json.dumps(totals,indent=2)+'\n',encoding='utf-8')
    summary={'input_olb_sha256':sha(olb),'personal_symbols':len(streams),'fpx_psm':len(psm_by_stem),
             'fpx_dra':len(dra_by_stem),'fpx_pad':len(pads),'3d_models':len(steps),
             'active_added_psm':len(psm_by_stem)-len(conflict_stems),'conflicting_footprints':sorted(conflict_stems),
             'symbol_candidates_matched':sum(bool(r['Matched_Footprint']) for r in symbol_report),
             'catalog_rows':len(current)+len(generated),'generated_rows':len(generated),
             'geometry_modified':False,'OLB_modified':False,'issues':dict(Counter(r['Issue'] for r in issues))}
    (root/'metadata/personal-import.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
