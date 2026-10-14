# Remix the campus

Fork it. Change it. Share it. The license is MIT, and the educational notice in `NOTICE.md` still applies: vendor trademarks and official docs stay with their owners.

Keep two properties intact when you re-engineer the campus:

1. **It opens from disk.** System fonts only. No CDN. Scripts and stylesheets are relative. The HTML may link `assets/…`, `sw.js`, and `manifest.webmanifest`. Do not add `https://` script or font links. `file://` loads a lesson by injecting its module. The service worker runs only on http.
2. **A section is a module.** Do not put `window.SECTIONS` back into the HTML. The checker rejects that, and it rejects an HTML shell over 250,000 bytes.

`python3 scripts/check-campus.py` is the gate. It checks every section module, the counts below, the zip, CDN tags, and personal-hub links.

## File structure

```text
campus/uc-lab-free-university.html          shell
campus/sw.js                                http cache
campus/manifest.webmanifest
campus/assets/app.css                       theme
campus/assets/app.js                        router
campus/assets/telephony.js                  dialpad and tones
campus/assets/tools.js                      ladder, Erlang, SDP
campus/assets/topology.js                   3D fabric (loads Three.js)
campus/assets/vendor/three.module.min.js    vendored Three.js r170
campus/assets/curriculum/manifest.js        index: titles, journeys, counts
campus/assets/curriculum/sections/<id>.js   one lesson
campus/assets/curriculum/walks.js           long scenes
campus/assets/visual-*.js                   studio player
releases/uc-lab-free-university.html.zip
downloads/*.pptx                            62-slide briefing
docs/                                       learner and remix guides
scripts/check-campus.py                     integrity gate
scripts/rebuild-campus-zip.py              zip builder
scripts/scrub-pptx-metadata.py              deck metadata cleaner
```

| Layer | Where it is | What a remix changes |
|-------|-------------|----------------------|
| Theme | `campus/assets/app.css`, `html[data-theme=…]` | Colors. Keep `--cc-bg`, `--cc-surface`, `--cc-accent-1` … `--cc-accent-4` so a future hub can theme the campus. |
| Shell | `uc-lab-free-university.html` and `app.js` | Chrome, routes, one `h1` |
| Catalog | `curriculum/manifest.js` | Titles, groups, journeys. No lesson bodies. |
| Lesson | `curriculum/sections/<id>.js` | That lesson's HTML and its flows |

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

1. Add `campus/assets/curriculum/sections/<id>.js`. The file is one statement: `UC.pack({...section}, [...flows]);` with JSON text. Escape `</` inside HTML as `<\/`.
2. Add the matching object to the `sections` array in `curriculum/manifest.js` (`id`, `num`, `group`, `title`, `sub`, `journey`, `track`, `flow`, `blurb`, `cards`). Bump `stats.sections` and the journey count.
3. Set `window.STATS.sections` in the HTML shell to the new length.
4. If the home lesson states the count, update that body too. The home body must keep `data-v21` and the words `Study sequence`.
5. Run `python3 scripts/check-campus.py`. The checker currently expects the published counts (580 sections, 1,186 flows, and the card totals). A new section means updating those expected totals in `scripts/check-campus.py` in the same change.
6. Rebuild the zip. Open `#/lesson/your-id` and the legacy hash `#your-id`.

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

Edit the `body` string inside `campus/assets/curriculum/sections/<id>.js`. The Teams Phone PSTN checklist lives in the `ms-teams-phone-pstn` module and must keep the text `V20 FIELD CHECKLIST`.

### Retheme the whole campus

Public themes are `light` (default), `dark`, `contrast`, and `signal`. **Settings** stores `uc_lab_settings_v21` and keeps `uc_theme` in step with the theme. Older names (`warm`, `paper` → light; `night`, `aurora`, `cobalt`, `forest`, `sunset` → dark) are mapped in the boot script in the HTML. Do not put the old seven-theme gallery back as the default.

Change `:root` and the `html[data-theme=…]` blocks in `campus/assets/app.css`. Keep the `--cc-*` tokens. The studio still reads `--bg`, `--card`, `--ink`, and `--muted`, which alias those tokens.

## Add a theme

Pick a short lowercase name, such as `tide`.

1. Add `html[data-theme="tide"]` in `campus/assets/app.css`, setting the `--cc-*` tokens and the studio aliases.
2. Add a radio `<input type="radio" name="theme" value="tide">` in the Settings dialog, and add `tide` to `THEMES` in `campus/assets/settings.js`.
3. Allow `tide` in the boot script next to `dark`, `contrast`, `signal`, and `light`.

Reload. The choice should survive a refresh.

## Regenerate the zip

The zip contains `uc-lab-free-university.html`, `sw.js`, `manifest.webmanifest`, and `assets/`. Members must match the files on disk.

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
Read docs/REMIX.md. Add one section module under campus/assets/curriculum/sections/.
Register it in curriculum/manifest.js. Do not embed window.SECTIONS in the HTML.
Keep zero CDN: relative assets only, system fonts only.
Update the expected counts in scripts/check-campus.py if the totals change.
Run python3 scripts/check-campus.py and python3 scripts/rebuild-campus-zip.py.
```

**Cursor.** Open this repo as the workspace. Point the agent at `docs/REMIX.md` and `scripts/check-campus.py`. Ask for a diff that touches the new module, the manifest entry, and the zip. Reject a diff that pastes the curriculum back into the HTML.

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
