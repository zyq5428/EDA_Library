"""Read OLB CFB package streams as evidence, not decoded CAD property semantics."""

import re
import struct


def package_streams(path):
    blob = path.read_bytes()
    if blob[:8] != bytes.fromhex("d0cf11e0a1b11ae1"):
        raise ValueError("OLB is not a CFB compound file")
    size = 1 << struct.unpack_from("<H", blob, 30)[0]
    mini_size = 1 << struct.unpack_from("<H", blob, 32)[0]
    def sector(i):
        data = blob[(i+1)*size:(i+2)*size]
        if len(data) != size: raise ValueError("Truncated CFB sector")
        return data
    ids = list(struct.unpack_from("<109I", blob, 76))
    difat, count = struct.unpack_from("<II", blob, 68)
    seen = set()
    for _ in range(count):
        if difat in seen: raise ValueError("CFB DIFAT cycle")
        seen.add(difat)
        values = struct.unpack("<" + "I"*(size//4), sector(difat))
        ids.extend(values[:-1]); difat = values[-1]
    fat = []
    for i in ids:
        if i < 0xFFFFFFFA: fat.extend(struct.unpack("<" + "I"*(size//4), sector(i)))
    def chain(i, table):
        result, seen = [], set()
        while i < 0xFFFFFFFA:
            if i in seen or i >= len(table): raise ValueError("Invalid CFB chain")
            seen.add(i);result.append(i);i=table[i]
        return result
    directory = b"".join(sector(i) for i in chain(struct.unpack_from("<I", blob, 48)[0],fat))
    entries = []
    for pos in range(0,len(directory),128):
        n = struct.unpack_from("<H",directory,pos+64)[0]
        if n > 64 or n % 2: raise ValueError("Invalid CFB directory name")
        name = directory[pos:pos+max(0,n-2)].decode("utf-16le") if n else ""
        entries.append((name,directory[pos+66],*struct.unpack_from("<III",directory,pos+68),
                        struct.unpack_from("<I",directory,pos+116)[0],struct.unpack_from("<Q",directory,pos+120)[0]))
    root = entries[0]
    mini = b"".join(sector(i) for i in chain(root[5],fat))[:root[6]]
    mini_fat_data = b"".join(sector(i) for i in chain(struct.unpack_from("<I",blob,60)[0],fat))
    mini_fat = list(struct.unpack("<"+"I"*(len(mini_fat_data)//4),mini_fat_data))
    parent = next(e for e in entries if e[0]=="Packages" and e[1]==1)
    visited = set()
    def walk(i):
        if i >= 0xFFFFFFFA: return []
        if i in visited or i >= len(entries): raise ValueError("Invalid CFB sibling tree")
        visited.add(i);e=entries[i]
        return walk(e[2])+([e] if e[1]==2 and e[0]!="$Types$" else [])+walk(e[3])
    result = {}
    cutoff = struct.unpack_from("<I",blob,56)[0]
    for e in walk(parent[4]):
        raw = (b"".join(mini[i*mini_size:(i+1)*mini_size] for i in chain(e[5],mini_fat))
               if e[6] < cutoff else b"".join(sector(i) for i in chain(e[5],fat)))[:e[6]]
        if len(raw)!=e[6]: raise ValueError("Truncated CFB stream")
        result[e[0]]=raw
    return result


def ascii_tokens(raw):
    return [v.decode("ascii") for v in re.findall(rb"[ -~]{4,}",raw)]
