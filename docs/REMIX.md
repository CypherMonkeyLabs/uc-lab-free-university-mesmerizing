# Remix the campus

Fork it. Change it. Share it. The license is MIT, and the educational notice in `NOTICE.md` still applies: vendor trademarks and official docs stay with their owners.

Keep two properties intact when you re-engineer the file:

1. **It opens from disk.** System fonts only. No CDN. Scripts and stylesheets must be relative files under `campus/assets/` (the zip places that folder next to the HTML). A `data:` favicon is still allowed. Do not add `https://` script or font links.
2. **A section is data.** `window.SECTIONS` is the curriculum. The shell renders whatever that array contains.

`python3 scripts/check-campus.py` is the gate. It checks the section array, the zip, CDN tags, and personal-hub links.

## File structure

```text
campus/uc-lab-free-university.html     the app and the curriculum
campus/assets/                         visual studio, kept beside the HTML
releases/uc-lab-free-university.html.zip
downloads/*.pptx                       62-slide briefing
docs/                                  learner and remix guides
docs/references/                       public session list
scripts/check-campus.py                integrity gate
scripts/rebuild-campus-zip.py         zip builder
scripts/scrub-pptx-metadata.py         deck metadata cleaner
```

The HTML is one document with four layers:

| Layer | Where it is | What a remix changes |
|-------|-------------|----------------------|
| Theme CSS | `<style>` near the top, `html[data-theme=…]` | Colors |
| Shell | Markup for the bar, menu, options, export | Chrome around the sections |
| Curriculum | `window.SECTIONS = [ … ]` | Lessons |
| Packs | Scripts after the array: resources, swatches, mission control, orientation, section pictures | Behavior that wraps every section |

Do not pretty-print the HTML. `window.SECTIONS` is a single JSON-compatible literal, and a reflow turns a one-line edit into a 15 MB diff.

## How a section is built

Each item has these fields:

| Field | Required | Convention |
|-------|----------|------------|
| `id` | Yes | Unique, stable, lowercase kebab-case. The address-bar hash is this id. |
| `num` | Yes | Display label, a string. Home is `000`. Hubs use `C01` … `C17`. It is not the array index. |
| `group` | Yes | Sidebar group. Reuse one from the section map unless you mean a new chapter. |
| `title` | Yes | Short. One emoji is enough. |
| `sub` | Yes | One line under the title. |
| `body` | Yes | HTML fragment. Quotes are escaped as `\"` and line breaks as `\n`. |
| `kind` | No | `"rich"` on some existing sections. The shell renders a section without it. Omit it on new ones. |

Id prefixes already in the file:

| Prefix | Means |
|--------|--------|
| `prod-` | A product chapter, such as `prod-cucm` or `prod-webex` |
| `found-` | A foundation layer, `found-0` upward |
| `hub-` | A chapter hub that collects a trail |
| `drill-` | A LICC drill bank |
| `qbank`, `glossary`, `resources-index` | Library tools |

Body HTML that already matches the shell: `hero`, `card`, `hook`, `warn`, `tips`, `grid`, `stat`, `eyebrow`, and `table.nice`.

### Add a section

1. Find the end of `window.SECTIONS`, just before `];(function () { "use strict"; var additions`.
2. Insert one object before the closing `]`. Keep the comma valid.
3. Set `window.STATS.sections` to the new length.
4. Set the visible home stat in the `home` section body to the new length. The progress script fills `#st-sec` from `SECTIONS.length` when that element exists. v21 home shows the count as a literal in the Study sequence card.
5. Run `python3 scripts/check-campus.py`.
6. Open `campus/uc-lab-free-university.html#your-id` with the network disabled.

Example shape, shown with real quote characters. Inside the file those quotes are escaped:

```json
{
  "id": "lgw-canary-checklist",
  "num": "C18",
  "group": "Migrations",
  "title": "🐤 LGW canary",
  "sub": "One site, one rollback",
  "body": "<div class=\"card teal\"><h2>Canary</h2><p>Write the LICC line before the change window.</p></div>"
}
```

### Extend a section that already exists

Immediately after the array, an IIFE named `additions` appends HTML onto an existing body, keyed by `id`. Use that when you want a checklist on `prod-webex` and you want the original section left in place. The keys already there (`ms-teams-phone-pstn`, `webex-calling-advanced`, `cucm-webex-calling-cutover`, and others) are the pattern.

### Retheme the whole campus

The public themes are `light` and `dark`. Light is the default (`<html data-theme="light">`). Teal `#0F9B8E` is the primary accent and navy `#0B1220` is the dark background and the light-theme ink. `setAppTheme` sets `data-theme` and stores `uc_theme` in `localStorage`. The header select `#theme` offers only those two.

Older names (`warm`, `night`, `cobalt`, `forest`, `aurora`, `sunset`, `paper`) still have CSS rules that map onto light or dark. They are not in the header select. A remix that wants a third public theme adds it to that select and to the cycle list. Do not put the old seven-theme gallery back as the default.

A full visual remix can stop at CSS variables. Change `:root` and you have a new default. Forks that only recolor should still pass `scripts/check-campus.py`.

## Add a theme

Pick a short lowercase name, such as `tide`. Touch five places. All of them are in `campus/uc-lab-free-university.html`.

1. **CSS.** Next to the other `html[data-theme=…]` rules:

```css
html[data-theme=tide]{
  --bg:#042F2E; --card:#083344; --ink:#ECFEFF; --muted:#99F6E4;
  --amber:#2DD4BF; --gold:#5EEAD4; --peach:#134E4A; --border:#115E59;
  --line:#115E59; --teal:#14B8A6; --blue:#67E8F9; --purple:#A5B4FC; --rose:#FB7185;
}
```

2. **Header select** `#theme`. The swatch gallery is built from these options:

```html
<option value="tide">🌊 Tide</option>
```

3. **Options buttons**, next to Light and Dark:

```html
<button class="setting-btn" onclick="setAppTheme('tide')">🌊 Tide</button>
```

4. **Cycle list**, the array `var themes = ["light", "dark"]`. Append `"tide"`.

5. **Swatch colors**, the `THEME_DOTS` object:

```javascript
tide: ["#042F2E", "#2DD4BF", "#67E8F9"]
```

Reload from disk. Pick Tide from the select and from the swatch row. The choice should survive a refresh.

## Regenerate the zip

The zip is a snapshot of the HTML, with one member named `uc-lab-free-university.html`.

```bash
python3 scripts/rebuild-campus-zip.py
python3 scripts/check-campus.py
```

Commit both the HTML and the zip so a download matches the campus in the same commit.

The README points learners at the files in the repo. The zip in `releases/` is edition v21. An older GitHub Release tagged `v20.2-resources` is a previous cut. Updating that release is a maintainer step outside this script.

## Regenerate the PPTX

There is no slide generator in this repo. The deck is a normal Office Open XML file:

`downloads/Enterprise-Voice-with-Cisco-Technologies-CC-Cloud-Migration.pptx`

1. Edit it in PowerPoint, Keynote, or LibreOffice.
2. Keep it a technical briefing. Synthetic numbers only (documentation ranges such as `203.0.113.0/24` and `198.51.100.0/24` are fine).
3. Save over the same filename, still 62 slides unless you also update the README and the checker.
4. Run:

```bash
python3 scripts/scrub-pptx-metadata.py
python3 scripts/check-campus.py
```

The scrubber sets the creator to **CYPHER0X9**, drops company and application metadata, drops the custom AIGC property and the orphaned provenance part, and rewrites the generator hostname in the `pptd` namespace. Slide text is left alone. Run it again after every save; office apps write identity back into the package.

## Use an AI coding agent

Cursor, or any agent that can edit the repo, is a good way to add a section. The file is large, so the instructions matter more than the model name.

Paste this boundary into the prompt:

```text
Read docs/REMIX.md. Edit campus/uc-lab-free-university.html surgically.
Do not reflow or pretty-print it.
Add one SECTIONS object with a unique kebab-case id.
Escape quotes in the body. Keep zero CDN: no script src, no stylesheet link, system fonts only.
Bump window.STATS.sections and the home stat st-sec if the count changes.
Run python3 scripts/check-campus.py and python3 scripts/rebuild-campus-zip.py.
```

**Cursor.** Open this repo as the workspace. Point the agent at `docs/REMIX.md` and `scripts/check-campus.py`. Ask for a diff that touches the section you named, the STATS line, and the zip. Reject a diff that reformats the HTML.

**Skills.** A project skill is optional. If you add one under `.cursor/skills`, make it point at this file and at the check script. Do not put API tokens, MCP secrets, or customer data in a skill.

**MCP.** Documentation servers are useful for checking a vendor fact before you write it into a section. Copy the official URL and the behavior you verified. Leave workspace secrets, customer names, internal hostnames, and live dial plans out of the HTML. If a connected tool returns a private value, it does not belong in a public campus.

After the agent finishes:

1. `python3 scripts/check-campus.py`
2. Open the new hash in a browser with the network disabled.
3. Read the section once yourself. An agent can invent a port or a product name. You are the editor.

## What to leave out

- Personal hubs, emails, phone numbers, and street addresses
- Employer or client names, real dial plans, and call captures
- Tokens, keys, and internal hostnames
- A CDN dependency "just for the fonts"

Synthetic examples already in the text (`user@contoso.com`, `user@domain.com`, TEST-NET addresses) can stay. They are placeholders.
