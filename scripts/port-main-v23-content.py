#!/usr/bin/env python3
"""One-time port of the v23 single-file shell content (main, PR #6) into the modular data.

Adds 11 call walkthroughs to curriculum/walks.js and wires them to sections in the
manifest, and adds 8 fault drills to the SIP drill bank. Idempotent. Run after
split-curriculum.py if you regenerate the curriculum.
"""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CUR = ROOT / "campus/assets/curriculum"
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "scripts/data/v23-extra-scenarios.json"
sc = {s["id"]: s for s in json.loads(SRC.read_text())}
PORT = {
 "conference": ["prod-cucm"], "cti-rp": ["prod-ucce"], "callback": ["prod-ucce", "prod-wxcc"],
 "park": ["prod-cucm"], "shared": ["prod-cucm"], "vm": ["prod-unity"], "early": ["prod-cube"],
 "fax": ["prod-cube"], "pickup": ["prod-cucm"], "snr": ["prod-cucm"], "failover": ["prod-cube"],
}
KIND = {"sip": "req", "rtp": "media"}
def js_json(v): return json.dumps(v, ensure_ascii=False, separators=(",", ":"))
wt = (CUR / "walks.js").read_text()
walks = json.JSONDecoder().raw_decode(wt[wt.index("UC.walks(") + 9:])[0]
have = {w["id"] for w in walks}
for key in PORT:
    s = sc[key]; wid = "walk-v23-" + key
    if wid in have: continue
    idx = {n["id"]: i for i, n in enumerate(s["nodes"])}
    walks.append({"id": wid, "title": s["title"], "why": s["why"], "cite": "UC Lab v23 call-flow set",
      "layout": "walk", "actors": [n["label"] for n in s["nodes"]], "chart": "setup-waterfall", "icon": "route",
      "keys": [["Walkthrough", s["title"]], ["Steps", str(len(s["steps"]))], ["Offline", "No media files"], ["LICC", "Leg, id, counter, capture"]],
      "header": "invite", "audio": False,
      "steps": [{"f": idx[t["f"]], "t": idx[t["t"]], "label": t["label"], "kind": KIND[t["kind"]], "cap": t["note"]} for t in s["steps"]],
      "walkthrough": True})
(CUR / "walks.js").write_text("UC.walks(" + js_json(walks) + ");\n")
mt = (CUR / "manifest.js").read_text()
i = mt.index("{"); m, end = json.JSONDecoder().raw_decode(mt[i:])
for key, secs in PORT.items():
    for sec in m["sections"]:
        if sec["id"] in secs and "walk-v23-" + key not in sec["walks"]:
            sec["walks"].append("walk-v23-" + key)
total_walks = len(walks)
# recompute flows = section flows + walks
base = 1186 - 26  # section flows in the checked-in build (walks.js held 26 definitions)
m["stats"]["flows"] = base + total_walks
m["stats"]["walkthroughs"] = total_walks + 1  # plus the campus home scene
(CUR / "manifest.js").write_text(mt[:i] + js_json(m) + mt[i + end:])
print("walks", total_walks, "flows", m["stats"]["flows"])

# ---- fault drills into the SIP and dial plan drill bank ----
import html as _h
FAULTS = json.loads((ROOT / "scripts/data/v23-faults.json").read_text())
p = CUR / "sections/drill-sip-dialplan-licc.js"
txt = p.read_text()
if "V23 FAULT DRILLS" not in txt:
    i = txt.index("UC.pack(") + 8
    sec, end = json.JSONDecoder().raw_decode(txt[i:])
    add = '<h3>V23 FAULT DRILLS</h3><p>Eight symptom-to-first-proof drills carried over from the v23 shell.</p>'
    for n, f in enumerate(FAULTS, 1):
        right = next(c[0] for c in f["choices"] if c[1])
        wrong = "; ".join(c[0] for c in f["choices"] if not c[1])
        add += ('<details class="q"><summary>F%02d · %s</summary><p><b>Best next move:</b> %s</p>'
                '<p class="why"><b>Why:</b> %s</p><p><b>Tempting but wrong:</b> %s</p></details>') % (
                n, _h.escape(f["title"]), _h.escape(right), _h.escape(f["why"]), _h.escape(wrong))
    body = sec["body"]
    k = body.rindex("</section>")
    sec["body"] = body[:k] + add + body[k:]
    sub = txt[i + end:]
    p.write_text(txt[:i] + json.dumps(sec, ensure_ascii=False, separators=(",", ":")) + sub)
    mt = (CUR / "manifest.js").read_text()
    j = mt.index("{"); m, e2 = json.JSONDecoder().raw_decode(mt[j:])
    m["stats"]["details"] += 8; m["stats"]["selfChecks"] += 8
    for s in m["sections"]:
        if s["id"] == "drill-sip-dialplan-licc": s["cards"] += 8
    (CUR / "manifest.js").write_text(mt[:j] + js_json(m) + mt[j + e2:])
    print("faults added")

# ---- v23 term cards, situation questions, and boss exam into the mastery card library ----
sys.path.insert(0, str(ROOT / "scripts"))
p = CUR / "sections/mastery-cards.js"
txt = p.read_text()
if "V23 TERM CARDS" not in txt:
    from uc_facts import FACTS, BOSS
    from quiz_scenarios import QUIZ_SCENARIOS
    e = _h.escape
    out = ['<div class="card teal"><h2>V23 TERM CARDS</h2><p>%d terms, %d situations, and a %d-question cross-track exam carried over from the v23 shell. Answer before you open.</p>' % (len(FACTS), len(QUIZ_SCENARIOS), len(BOSS))]
    tracks = []
    for f in FACTS:
        if f["track"] not in tracks: tracks.append(f["track"])
    for tr in tracks:
        out.append("<h3>Terms · %s</h3>" % e(tr))
        for f in FACTS:
            if f["track"] == tr:
                out.append('<details class="q"><summary>%s</summary><p>%s</p><p class="why"><b>Why it matters:</b> %s</p></details>' % (e(f["term"]), e(f["def"]), e(f["why"])))
    out.append("<h3>Situations</h3>")
    for s in QUIZ_SCENARIOS:
        out.append('<details class="q"><summary>%s · %s</summary><p><b>Best answer:</b> %s</p><p class="why"><b>Why:</b> %s</p></details>' % (e(s["track"]), e(s["q"]), e(s["correct"]), e(s["why"])))
    out.append("<h3>Cross-track exam</h3>")
    for b in BOSS:
        out.append('<details class="q"><summary>%s</summary><p><b>Best answer:</b> %s</p><p class="why"><b>Why:</b> %s</p></details>' % (e(b["q"]), e(b["choices"][b["answer"]]), e(b["why"])))
    out.append("</div>")
    add = "".join(out)
    i = txt.index("UC.pack(") + 8
    sec, end = json.JSONDecoder().raw_decode(txt[i:])
    sec["body"] += add
    p.write_text(txt[:i] + json.dumps(sec, ensure_ascii=False, separators=(",", ":")) + txt[i + end:])
    n = len(FACTS) + len(QUIZ_SCENARIOS) + len(BOSS)
    mt = (CUR / "manifest.js").read_text()
    j = mt.index("{"); m, e2 = json.JSONDecoder().raw_decode(mt[j:])
    m["stats"]["details"] += n; m["stats"]["selfChecks"] += n
    for s in m["sections"]:
        if s["id"] == "mastery-cards": s["cards"] += n
    (CUR / "manifest.js").write_text(mt[:j] + js_json(m) + mt[j + e2:])
    print("term cards added", n)
