import json
import re
import sys
from pathlib import Path

RAW = Path('cc_raw.txt')
text = RAW.read_text(encoding='utf-8', errors='replace').replace('\r\n', '\n').replace('\f', '\n')
body_start = text.find('\n8 Class FAU: Security audit\n\n8.1 Class description')
assert body_start > 0
body = text[body_start:]

toc_text = text[:text.find('\n1 Scope', 2000)]
toc_pat = re.compile(r'^\s*\d+\.\d+\.\d+\s+([A-Z]{3}_[A-Z]{3}\.\d+)\s+(.+?)\.{3,}', re.M)
toc_components = [(m.group(1), m.group(2).strip()) for m in toc_pat.finditer(toc_text)]
assert len(toc_components) == 156, len(toc_components)
names = dict(toc_components)

clean = []
for line in body.split('\n'):
    s = line.strip().replace('\ufffd', '')
    if re.match(r'^(November 2022\s+)?CC:2022\s+Page \d+ of 297$', s):
        continue
    if re.match(r'^Page \d+ of 297\s+CC:2022\s+November 2022$', s):
        continue
    if re.match(r'^Class [A-Z]{3}: .+$', s):
        continue
    if s == 'Security functional components':
        continue
    clean.append(line.replace('\ufffd', ''))
body = '\n'.join(clean)

positions = []
for cid, title in toc_components:
    pat = re.compile(r'(?m)^(?:\d+(?:\.\d+)+[ \t]+)?' + re.escape(cid) + r'(?:[ \t]+(.+?))?[ \t]*$')
    candidates = []
    for m in pat.finditer(body):
        tail = body[m.end():m.end() + 500]
        if 'Component relationships' in tail[:300] or re.match(r'\s*Hierarchical to:', tail):
            candidates.append(m)
    if not candidates:
        for m in re.finditer(re.escape(cid), body):
            tail = body[m.end():m.end() + 600]
            if 'Component relationships' in tail or 'Hierarchical to:' in tail:
                candidates.append(m)
    assert candidates, cid
    positions.append(candidates[0].start())

class_heads = list(re.finditer(r'(?m)^(\d+) Class ([A-Z]{3}): (.+)$', body))
family_heads = list(re.finditer(r'(?m)^(\d+\.\d+) (.+?) \(([A-Z]{3}_[A-Z]{3})\)$', body))
section_heads = list(re.finditer(r'(?m)^(?:\d+(?:\.\d+)+\s+[A-Z].*|\d+ Class [A-Z]{3}:.*)$', body))


def next_section(pos):
    for m in section_heads:
        if m.start() > pos:
            return m.start()
    return len(body)


def clean_text(s):
    s = re.sub(r'\n[ \t]*\n', '\n\n', s)
    s = re.sub(r'(?<=\w)- (?=\w)', '-', s)
    return s.strip()


def join_lines(s):
    lines = [x.strip() for x in s.split('\n')]
    out = []
    for x in lines:
        if not x:
            continue
        if out and not re.match(r'^([a-z]\)|--|[0-9]+\)|•)', x):
            out[-1] += ' ' + x
        else:
            out.append(x)
    return '\n'.join(out)


def paragraph_blocks(raw):
    raw = clean_text(raw)
    if not raw:
        return []
    raw = re.sub(r'(?m)^\d+ Class [A-Z]{3}: .*$', '', raw)
    chunks = [c.strip() for c in re.split(r'\n\s*\n', raw) if c.strip()]
    blocks = []

    def bracket_balance(s):
        return s.count('[') - s.count(']')

    for chunk in chunks:
        lines = [l.strip() for l in chunk.split('\n') if l.strip()]
        if not lines:
            continue
        lead = []
        items = []
        mode = None
        for line in lines:
            m = re.match(r'^(?:([a-z])\)|(--)|([0-9]+)\)|•)\s*(.*)$', line)
            if m:
                marker = 'ordered' if (m.group(1) or m.group(3)) else 'bullet'
                if mode is None:
                    mode = marker
                if mode == marker:
                    items.append(m.group(4).strip())
                else:
                    items = []
                    mode = 'mixed'
                    lead.append(line)
            elif mode and items:
                items[-1] += ' ' + line
            else:
                lead.append(line)
        if lead:
            text = ' '.join(lead)
            prev = blocks[-1] if blocks else None
            if prev and prev['type'] == 'p' and (
                bracket_balance(prev['text']) > 0
                or prev['text'].endswith((':', ',', ';'))
                or text[:1].islower()
            ):
                prev['text'] += ' ' + text
            else:
                blocks.append({'type': 'p', 'text': text})
        if items:
            if blocks and blocks[-1]['type'] == 'list' and blocks[-1].get('ordered') == (mode == 'ordered'):
                blocks[-1]['items'].extend(items)
            else:
                blocks.append({'type': 'list', 'ordered': mode == 'ordered', 'items': items})
    # merge adjacent same-type lists
    merged = []
    for block in blocks:
        if merged and block['type'] == 'list' and merged[-1]['type'] == 'list' and merged[-1]['ordered'] == block['ordered']:
            merged[-1]['items'].extend(block['items'])
        else:
            merged.append(block)
    return merged


def parse_component(idx, cid, title):
    start = positions[idx]
    ns = next_section(start)
    if idx + 1 < len(positions) and positions[idx + 1] < ns:
        end = positions[idx + 1]
    else:
        end = ns
    sec = body[start:end]
    first_line_end = sec.find('\n')
    sec = sec[first_line_end + 1:] if first_line_end >= 0 else ''
    sec = re.split(r'(?m)^\s*Component rationale.*$', sec)[0]

    hm = re.search(r'(?m)^\s*Hierarchical to:\s*(.*?)(?=^\s*Dependencies:)', sec, re.S)
    dm = re.search(r'(?m)^\s*Dependencies:\s*(.*?)(?=^\s*' + re.escape(cid) + r'\.\d+\s*$)', sec, re.S)
    hierarchical = [x for x in names if x in hm.group(1)] if hm else []
    dependencies = [x for x in names if x in dm.group(1)] if dm else []

    elements = []
    ems = list(re.finditer(r'(?m)^' + re.escape(cid) + r'\.(\d+)\s*$', sec))
    for j, m in enumerate(ems):
        estart = m.end()
        eend = ems[j + 1].start() if j + 1 < len(ems) else len(sec)
        eraw = sec[estart:eend]
        elements.append({'id': cid + '.' + m.group(1), 'blocks': paragraph_blocks(eraw)})
    return hierarchical, dependencies, elements


classes = []
for ci, cm in enumerate(class_heads):
    cstart = cm.start()
    cend = class_heads[ci + 1].start() if ci + 1 < len(class_heads) else len(body)
    cbody = body[cstart:cend]
    cnum, cid, cname = cm.group(1), cm.group(2), cm.group(3).strip()
    cd = re.search(r'(?m)^\d+\.1 Class description\s*\n(.*?)(?=^\d+\.\d+ )', cbody, re.S)
    cdesc = join_lines(cd.group(1)) if cd else ''
    cdesc = re.sub(r'Figure \d+.*?(?=\n[A-Z]|\Z)', '', cdesc, flags=re.S).strip()

    fams = []
    fhs = [m for m in family_heads if cstart <= m.start() < cend]
    for fi, fm in enumerate(fhs):
        fstart = fm.start()
        fend = fhs[fi + 1].start() if fi + 1 < len(fhs) else cend
        fbody = body[fstart:fend]
        fnum, fname, fid = fm.group(1), fm.group(2).strip(), fm.group(3)
        fb = re.search(r'(?m)^\d+\.\d+\.1 Family behaviou?r\s*\n(.*?)(?=^\d+\.\d+\.2 )', fbody, re.S)
        fdesc = join_lines(fb.group(1)) if fb else ''

        mgmt = {}
        audit = {}
        for sm in list(re.finditer(r'(?m)^\d+\.\d+\.\d+ (Management|Audit) of ', fbody)):
            kind = sm.group(1)
            p = sm.end()
            line_end = fbody.find('\n', p)
            ids_text = fbody[p:line_end if line_end >= 0 else len(fbody)]
            p = line_end + 1 if line_end >= 0 else len(fbody)
            # Consume wrapped component lists, including an indented line after a blank.
            while p < len(fbody):
                le = fbody.find('\n', p)
                line = fbody[p:le if le >= 0 else len(fbody)]
                if line.strip() == '':
                    q = p + 1
                    qe = fbody.find('\n', q)
                    nxt = fbody[q:qe if qe >= 0 else len(fbody)]
                    if re.match(r'^[ \t]+[A-Z]{3}_[A-Z]{3}\.\d+', nxt):
                        p = qe + 1 if qe >= 0 else len(fbody)
                        continue
                    break
                if re.match(r'^[ \t]+[A-Z]{3}_[A-Z]{3}\.\d+', line):
                    ids_text += ' ' + line.strip()
                    p = le + 1 if le >= 0 else len(fbody)
                    continue
                break
            while p < len(fbody) and fbody[p] == '\n':
                p += 1
            nm = re.search(r'(?m)^\d+(?:\.\d+){1,2} ', fbody[p:])
            content_end = p + nm.start() if nm else len(fbody)
            scontent = fbody[p:content_end]
            ids = re.findall(r'[A-Z]{3}_[A-Z]{3}\.\d+', ids_text)
            if not ids:
                for suffix in re.findall(r'(?:^|[, ]+)([A-Z]{3}\.\d+)', ids_text):
                    ids.append(fid.split('_')[0] + '_' + suffix)
            items = []
            for line in join_lines(scontent).split('\n'):
                line = re.sub(r'^[a-z]\)\s*', '', line).strip()
                if not line:
                    continue
                if line.startswith('The following actions') or line.startswith('in the PP, PP-Module'):
                    continue
                items.append(line)
            for x in ids:
                if kind == 'Management':
                    mgmt.setdefault(x, []).extend(items)
                else:
                    audit.setdefault(x, []).extend(items)

        level_start = fbody.find('Components leveling and description')
        lvl_m = re.search(r'(?m)^\d+\.\d+\.\d+ (?:Management|Audit) of ', fbody[level_start:])
        level_end = level_start + lvl_m.start() if lvl_m else -1
        intro = fbody[level_start:level_end if level_end > level_start else fend - fstart]

        comps = []
        for idx, (cid2, title2) in enumerate(toc_components):
            if positions[idx] < fstart or positions[idx] >= fend:
                continue
            if not cid2.startswith(fid + '.'):
                continue
            h, d, els = parse_component(idx, cid2, title2)
            desc = ''
            cmatch = re.search(r'(?m)^[^\n]*\b' + re.escape(cid2) + r'\b[^\n]*', intro)
            if cmatch:
                rest = intro[cmatch.end():]
                stops = [len(rest)]
                for marker in [rest.find('\n\n')]:
                    if marker >= 0:
                        stops.append(marker)
                nxt_id = re.search(r'(?m)^[^\n]*\b[A-Z]{3}_[A-Z]{3}\.\d+\b[^\n]*', rest)
                if nxt_id:
                    stops.append(nxt_id.start())
                nxt_sec = re.search(r'(?m)^\d+\.\d+', rest)
                if nxt_sec:
                    stops.append(nxt_sec.start())
                desc = intro[cmatch.start():cmatch.end() + min(stops)]
                desc = ' '.join(x.strip() for x in desc.split('\n') if x.strip())
                if desc.startswith('Figure '):
                    desc = ''
            if not desc and not els:
                sec_start = positions[idx]
                sec_end = next_section(sec_start)
                chunk = body[sec_start:sec_end]
                note = re.search(r'(?m)^(?:The component has been|This component is).*?(?=\n\n|$)', chunk, re.S)
                if note:
                    desc = ' '.join(note.group(0).split())
            comps.append({
                'id': cid2,
                'name': title2,
                'hierarchicalTo': [{'id': x, 'name': names[x]} for x in h],
                'dependencies': [{'id': x, 'name': names[x]} for x in d],
                'management': mgmt.get(cid2, []),
                'audit': audit.get(cid2, []),
                'description': desc,
                'elements': els
            })
        fams.append({'id': fid, 'number': fnum, 'name': fname, 'description': fdesc, 'components': comps})
    classes.append({'id': cid, 'number': int(cnum), 'name': cname, 'description': cdesc, 'families': fams})

nc = sum(len(c['families']) for c in classes)
ncomp = sum(len(f['components']) for c in classes for f in c['families'])
nel = sum(len(x['elements']) for c in classes for f in c['families'] for x in f['components'])
print('classes', len(classes), 'families', nc, 'components', ncomp, 'elements', nel)
for c in classes:
    print(c['id'], len(c['families']), sum(len(f['components']) for f in c['families']), sum(len(x['elements']) for f in c['families'] for x in f['components']))
Path('data/cc_en.json').write_text(json.dumps({'classes': classes}, ensure_ascii=False, indent=2), encoding='utf-8')
