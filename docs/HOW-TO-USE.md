# How to use UC Lab Free University

The campus is one HTML file. Everything else in the repo helps you download it, brief from it, or study beside it.

**Open it in Chrome, Safari, Edge, or Firefox.** The page boots from the file. Themes, search, and the curriculum stay available with the network off. Links inside a section that point at Cisco, Microsoft, AWS, or another vendor need a network, and the campus still opens when those links cannot.

## Each file, offline and on a phone

| File | Offline | On a phone |
|------|---------|------------|
| `campus/uc-lab-free-university.html` | Double-click, or open the file from the browser. Airplane mode is a fair test: home, search, themes, and a section should still render. | Use the Chrome or Safari **app**. First open can take 10–30 seconds. Then use **☰ Menu**, search, and the theme control. |
| `releases/uc-lab-free-university.html.zip` | Unzip, then open the HTML the same way. The zip is only packaging. | Download in the browser app, unzip in **Files** (iPhone) or Downloads (Android), then open the HTML in Chrome or Safari. |
| `downloads/Enterprise-Voice-with-Cisco-Technologies-CC-Cloud-Migration.pptx` | PowerPoint, Keynote, or LibreOffice, from the local file. 62 slides. | PowerPoint or Keynote mobile, or the Files preview. The HTML is the better phone textbook. The deck is the projected story. |
| `docs/HOW-TO-USE.md`, `docs/FAQ.md`, `docs/REMIX.md`, `docs/SIBLINGS.md` | Any markdown preview, including the GitHub app offline cache or a local editor. | Comfortable to read. They do not replace the campus. |
| `docs/references/uc-contact-center-session-vault-2026-10.md` | The list itself is local. | Read the titles offline. Opening a Cisco Live or YouTube link needs a network, and some sessions need a free vendor account. |
| `docs/assets/preview.png` | Local image. | The picture on the README. |

> [!TIP]
> In-app browsers inside LinkedIn, Instagram, and Telegram often stop on "Loading" for this file. Move the zip into Files and open it from Chrome or Safari.

### A ten-minute first session

1. Open the HTML. Wait until the home page shows **Mission Control** and the October 2026 card.
2. Read **Method** (`#method`) and say LICC without looking: Leg, ID, Counter, Capture.
3. Open **☰ Menu** and pick one product, for example CUCM (`#prod-cucm`).
4. Switch theme once (Warm, Night, or Paper). That confirms the page is running locally.
5. Search for `Local Gateway`. Open one hit. Stop there.

Progress checkmarks stay in this browser. A different browser, or a cleared site store, starts the donut over. Nothing is uploaded.

### Export without installing anything

Use the export button in the campus bar:

- one section as HTML
- the whole app
- Markdown
- progress JSON
- question-bank CSV
- print, then **Save as PDF** in the browser

## 30-day study path

About 45–75 minutes a day. Stay on the day's ids. The hash in the address bar is the section id.

| Day | Open these | Done when you can… |
|-----|------------|--------------------|
| 1 | `home`, `method`, `mindmap`, `naming` | Define LICC and point at a call leg on the home diagram |
| 2 | `found-0` … `found-4` | Separate physical path, numbering, dial plan, and SIP |
| 3 | `found-5` … `found-9` | Explain one-way audio, QoS, and NAT in one paragraph each |
| 4 | `found-10` … `found-15` | Name the proof you would keep for TLS, E911, STIR, recording, and a migration |
| 5 | `prod-cucm`, `hub-cucm` | Trace registration and a basic call on CUCM |
| 6 | `prod-cube`, `hub-cube-sbc`, `hub-sip` | Draw CUBE between a PBX and a SIP trunk |
| 7 | `prod-webex`, `prod-teams` | Contrast Webex Calling Local Gateway with Teams Direct Routing |
| 8 | `prod-expressway`, `hub-expressway` | Say what Expressway does, and what it does not |
| 9 | `prod-unity` | Place voicemail on the call path and name the MWI proof |
| 10 | `prod-ucce`, `hub-icm-ucce`, `hub-pcce` | Contrast UCCE and PCCE in five sentences |
| 11 | `prod-wxcc`, `hub-webex-cc` | Describe a Webex Contact Center call to an agent |
| 12 | `prod-connect`, `hub-amazon-connect` | Follow a contact from entry to queue using ContactId |
| 13 | `prod-genesys`, `prod-zoom`, `prod-nice` | Name one routing idea each platform shares |
| 14 | `hub-e911-redsky`, `hub-qos` | List the evidence you would want after an emergency test call |
| 15 | `hub-migrations` | Write a canary and a rollback for one site |
| 16 | Search `cutover`, open the CUCM → Webex Calling section | Fill the coexistence failure matrix in your own words |
| 17 | `drill-sip-dialplan-licc` | Finish one drill with all four LICC lines |
| 18 | `drill-media-resources-licc` | Explain a silent 200 OK with a capture plan |
| 19 | `drill-edge-cloud-licc` | Compare Local Gateway and Direct Routing failure clues |
| 20 | `drill-cc-e911-qos-licc` | Tie a contact-center symptom to a counter |
| 21 | `resources-index` | Pick two official docs and note what you would re-check before production |
| 22 | `hub-interview` | Answer one prompt out loud in under four minutes |
| 23 | `qbank` | Score a short set, and write the misses as LICC |
| 24 | `hub-sev-troubleshoot` plus one Tricky SEV | Time-box 25 minutes, then compare with the notes |
| 25 | `glossary` | Define ten terms you still hesitate on |
| 26 | Blank page | Teach a CUCM ↔ Local Gateway ↔ Webex call with no notes |
| 27 | Export | Save one hub as Markdown and read it away from the app |
| 28 | Paper theme | Present that hub to a person, or record yourself |
| 29 | Your miss list | Repeat the two weakest days |
| 30 | One page | Write a LICC story from a drill: leg, id, counter, capture |

Miss a day and continue. The path is a sequence, not a streak.

> [!NOTE]
> Foundations still teach CUCM, CUBE, UCCE, and dial plan because dual-run and migration jobs still require them. The October 2026 card on `home` names the current product lines to put on top of that base: Webex Calling, Webex Contact Center, Customer Assist, Teams Phone, and the major CCaaS platforms.

## Interview prep

Use the campus as a speaking gym.

1. Open `hub-interview`. Answer one prompt before you read the notes.
2. Force this order: **path, then product**. "The call hits the SBC, the Call-ID changes, the counter that moved was…" lands better than a feature list.
3. Drill these three out loud until they are boring:
   - CUCM phone to a SIP trunk through CUBE
   - Webex Calling user to the PSTN through a Local Gateway, including a transfer
   - Teams Direct Routing versus Operator Connect, including an emergency call
4. Open `qbank`. Export CSV if you want a paper stack. Misses go back into a LICC line, not into a highlight.
5. Borrow the **62-slide deck** when you want a whiteboard narrative for "tell me about a migration." The slides are a briefing. The section behind them is the study.
6. Close the laptop and teach the answer to a timer. Four minutes. Then one minute on what evidence you would capture.

Bring synthetic numbers only. A real customer story needs permission and still does not belong in a public fork.

## Teach a class

A 90-minute team session:

| Minutes | Do this |
|---------|---------|
| 0–10 | Home page, Paper theme, Mission Control. Agree the room rule: synthetic numbers only. |
| 10–25 | `method`. Everyone writes LICC for a call they already know. |
| 25–55 | One hub. Good first hubs: `hub-sip`, `hub-cube-sbc`, `hub-webex-cc`, `hub-migrations`, `hub-e911-redsky`. |
| 55–75 | Pairs. One person breaks a leg. The other asks for id, counter, and capture. |
| 75–90 | Two teach-backs, two minutes each. Export the hub to PDF for anyone who wants the paper. |

Longer programs: assign one row of the 30-day table per week and use the session vault for an optional official recording. The vault is a reading list of public sessions. It is not a substitute for the vendor's current document.

Classroom setup:

- Project from a laptop. The file does not need a login.
- **Paper** theme is the calm projector look. **Night** is the dim-room look.
- Font scale and density are in the options panel.
- Hand out the zip, not a screenshot. People should leave with the file.
- Keep customer captures and production dial plans off the shared screen and out of the HTML.

## If the page looks stuck

- Give a phone up to a minute on the first open.
- Open the same file on a laptop to confirm the copy is intact.
- Use the full browser app.
- Search for `THE CALL MUST ALWAYS CONNECT` or `LICC`. A hit means the curriculum is in memory.
- Themes must still switch in airplane mode. If they do, you are on the local file.

More short answers: [FAQ](./FAQ.md). Engineering changes: [REMIX](./REMIX.md).
