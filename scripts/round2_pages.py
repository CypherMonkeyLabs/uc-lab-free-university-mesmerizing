"""Round-2 guide, play, and cheat-code pages for the flagship lab."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/CypherMonkeyLabs/uc-lab-free-university-mesmerizing"
PORT_DOC = "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html"
SYS = "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html"
BLOG = "https://blogs.cisco.com/learning/the-future-of-collaboration-is-here"
FCC = "https://www.fcc.gov/mlts-911-requirements"
RFC3261 = "https://www.rfc-editor.org/rfc/rfc3261"


def cheat_foot() -> str:
    return f"""
<footer class="cheat-print">
<p><a href="https://cyphermonkeylabs.com">cyphermonkeylabs.com</a>
· <a href="https://linktr.ee/cyphermonkey">linktr.ee/cyphermonkey</a>
· <a href="{REPO}">GitHub repo · rate, comment, help</a></p>
<p>Independent educational project, not affiliated with vendors. Trademarks belong to their owners. MIT code, CC BY-NC-SA content.</p>
</footer>
"""


def build_round2(write_page, sources, bank: dict) -> None:
    write_guide(write_page, sources, bank)
    write_play(write_page, sources, bank)
    slugs = write_cheats(write_page, sources, bank)
    manifest = {
        "sheets": slugs,
        "json": ["flashcards-cited.json", "flashcards-idea-pool.json"],
        "bundle": "../uc-lab-flagship.zip",
    }
    (ROOT / "flagship" / "cheats" / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    cited = [
        {"id": card.get("id"), "topic": card.get("topic"), "q": card.get("q"), "a": card.get("a"), "cite": card.get("cite")}
        for card in bank["pr2Cards"]
    ]
    pool = [
        {"term": card.get("term"), "def": card.get("def"), "track": card.get("track")}
        for card in bank["cards"]
    ]
    folder = ROOT / "flagship" / "cheats"
    (folder / "flashcards-cited.json").write_text(json.dumps({"deck": "cited-study-cards", "count": len(cited), "cards": cited}, indent=2), encoding="utf-8")
    (folder / "flashcards-idea-pool.json").write_text(json.dumps({"deck": "idea-pool", "count": len(pool), "cards": pool}), encoding="utf-8")


def write_guide(write_page, sources, bank: dict) -> None:
    cards = """
<div class="atlas">
<a class="card" href="architecture.html"><h2>Architecture</h2><p>Identity, signaling, media, policy, observe.</p></a>
<a class="card" href="deployment.html"><h2>Deployment</h2><p>Publisher, time, DNS, certificates, backups.</p></a>
<a class="card" href="configure.html"><h2>Configuration</h2><p>Lab-safe walkthroughs. Not a change window.</p></a>
<a class="card" href="migration.html"><h2>Migration</h2><p>Checklist and a cutover you can roll back.</p></a>
<a class="card" href="playbooks.html"><h2>Playbooks</h2><p>One hypothesis, one change, one capture.</p></a>
<a class="card" href="firewall.html"><h2>Firewall matrix</h2><p>Who talks to whom, from the CUCM 15 port chapter.</p></a>
<a class="card" href="pstn.html"><h2>PSTN choices</h2><p>Trunk, Calling Plan, local gateway, Operator Connect, Direct Routing.</p></a>
<a class="card" href="security.html"><h2>Security</h2><p>Toll fraud, TLS, SRTP, and what this lab will not decide.</p></a>
<a class="card" href="../licensing.html"><h2>Licensing</h2><p>Smart Licensing, Webex subscriptions, Teams Phone.</p></a>
<a class="card" href="../certifications.html"><h2>Certifications</h2><p>The February 2026 Cisco exam names.</p></a>
<a class="card" href="interview.html"><h2>Interview</h2><p>Questions from the bank, and a career path with no invented salaries.</p></a>
<a class="card" href="whats-new.html"><h2>What's new</h2><p>2026 items that are cited, and rows marked unverified.</p></a>
</div>
"""
    write_page("guide/index.html", "Guide", f"<p class='kicker'>Gap audit</p><h1>From fundamentals to the job</h1><p class='lede'>Every block below is a page in this lab. The deep campus still holds the long library.</p>{cards}", "Architecture through interview prep.")

    write_page("guide/architecture.html", "Architecture", f"""
<p class="kicker">Planes</p>
<h1>Architecture</h1>
<p class="lede">Read a call in five planes. Jumping from a symptom to a restart skips the plane that actually failed.</p>
<figure class="ladder"><svg viewBox="0 0 920 220" role="img" aria-label="Five planes from identity to observe">
<rect width="920" height="220" rx="16" fill="#fffdf8"/>
<g font-family="Georgia, serif" font-size="16" text-anchor="middle">
<rect x="20" y="70" width="150" height="70" rx="12" fill="#fff6e4" stroke="#a9782c"/><text x="95" y="110">Identity</text>
<rect x="200" y="70" width="150" height="70" rx="12" fill="#e7f6f2" stroke="#0f6e62"/><text x="275" y="110">Signaling</text>
<rect x="380" y="70" width="150" height="70" rx="12" fill="#eceefe" stroke="#4c3d8f"/><text x="455" y="110">Media</text>
<rect x="560" y="70" width="150" height="70" rx="12" fill="#fde8e3" stroke="#9f3048"/><text x="635" y="110">Policy</text>
<rect x="740" y="70" width="150" height="70" rx="12" fill="#fff" stroke="#1c1915"/><text x="815" y="110">Observe</text>
</g>
</svg></figure>
<ul>
<li><strong>Identity.</strong> Directory number, user, device, certificate, and the PSTN number the far side will see.</li>
<li><strong>Signaling.</strong> SIP, SCCP, or the cloud call control that owns the invite. Port 5060 or 5061 is this plane.</li>
<li><strong>Media.</strong> RTP or SRTP between the addresses in SDP. A proxy can be perfect and still not see audio.</li>
<li><strong>Policy.</strong> CSS and partitions, dial-peers, Teams voice routes, Webex location PSTN choice, emergency, recording.</li>
<li><strong>Observe.</strong> CDR, CUIC call type, CQD, Control Hub, the ladder, the packet capture.</li>
</ul>
<p>On-premises call control in this lab is Unified CM plus CUBE or another SBC. Cloud call control is Webex Calling or Teams Phone. Contact center sits on top of a number: UCCE on a dialed number and call type, Webex Contact Center on an entry point and a flow.</p>
{sources([("RFC 3261", RFC3261), ("CUCM 15 system configuration", SYS), ("Webex Calling help", "https://help.webex.com/"), ("Direct Routing plan", "https://learn.microsoft.com/en-us/microsoftteams/direct-routing-plan")])}
""", "Five-plane architecture for voice and contact center.")

    write_page("guide/deployment.html", "Deployment", f"""
<p class="kicker">Before the first phone</p>
<h1>Deployment</h1>
<p class="lede">The port chapter is also a deployment checklist. These are the rows that decide whether the cluster comes up.</p>
<ol>
<li><strong>Publisher first.</strong> The first node you install is the publisher. Subscribers install against it. Port 22/TCP has to stay open and unthrottled during that install.</li>
<li><strong>Time.</strong> CUCM uses NTP on 123/UDP. Certificates and CDRs lie when clocks disagree.</li>
<li><strong>Names.</strong> Phones resolve the cluster. Inside, _cisco-uds._tcp. Outside, for Mobile and Remote Access, _collab-edge._tls. A public answer for cisco-uds is the wrong record.</li>
<li><strong>Certificates.</strong> TLS on 5061 and HTTPS on 443 and 8443 fail closed when the name does not match. CAPF for phone certificates listens on 3804/TCP.</li>
<li><strong>Backups.</strong> DRS sends backups to SFTP on 22/TCP. A cluster without a tested restore is a design, not a deployment.</li>
<li><strong>Do not run DHCP on CUCM.</strong> The port chapter says Cisco does not recommend the CUCM DHCP server or DHCP client. Give the nodes static addresses.</li>
<li><strong>Phones get files</strong> on TFTP 69/UDP and HTTP 6970/TCP. SCCP is 2000/TCP. SIP is 5060 and 5061.</li>
</ol>
<div class="callout sand"><p>SRST is the branch router keeping phones registered when the WAN to CUCM is down. Failback is its own problem: the WAN can return while phones stay on the router. Treat that as a registration symptom, not a dial-plan symptom.</p></div>
{sources([("CUCM 15 port usage", PORT_DOC), ("CUCM 15 system configuration", SYS)])}
""", "Deployment checks taken from the CUCM 15 port chapter.")

    write_page("guide/configure.html", "Configuration walkthroughs", f"""
<p class="kicker">Lab-safe</p>
<h1>Configuration walkthroughs</h1>
<p class="lede">Each walkthrough is an order of checks. It is not a screen-by-screen copy of an admin guide, and it does not log in anywhere.</p>
<h2>1. Class of service</h2>
<ol>
<li>Name the calling search space on the line, then the one on the device. The line CSS is searched first.</li>
<li>List partitions. Put the emergency partition before any partition that contains 9.@.</li>
<li>Dial 911 in the CSS lab on the labs page. Confirm the emergency pattern wins.</li>
<li>Only then add a national pattern.</li>
</ol>
<h2>2. CUBE dial-peers</h2>
<ol>
<li>Decide the inbound match. If nothing matches, the leg is dial-peer 0.</li>
<li>Decide the outbound match: longest destination-pattern, then lowest preference.</li>
<li>Write down whether each leg is early offer or delayed offer.</li>
<li>Place one test call and read both SDPs before you add a second carrier.</li>
</ol>
<h2>3. Webex Calling PSTN</h2>
<ol>
<li>Name the model: Calling Plan, or a local gateway for that location.</li>
<li>If it is Calling Plan, stop looking for a CUBE on the path.</li>
<li>If it is a local gateway, confirm the location points at the gateway you are tracing.</li>
</ol>
<h2>4. Teams Direct Routing</h2>
<ol>
<li>Confirm the user is Direct Routing, not Calling Plan or Operator Connect.</li>
<li>Get OPTIONS answered before you debug an INVITE.</li>
<li>Then place one call and keep the SBC's carrier leg in the same capture.</li>
</ol>
{sources([("CUCM 15 system configuration", SYS), ("Webex Calling help", "https://help.webex.com/"), ("Direct Routing plan", "https://learn.microsoft.com/en-us/microsoftteams/direct-routing-plan")])}
""", "Ordered configuration checks for CSS, CUBE, Webex, and Teams.")

    write_page("guide/migration.html", "Migration and cutover", f"""
<p class="kicker">Dual run</p>
<h1>Migration checklist</h1>
<p class="lede">Move a number only when identity, emergency location, and recording have a landing zone. The ladder for a CUCM-to-Webex dual run is on the flow page. This is the checklist around it.</p>
<div class="table-scroll"><table>
<thead><tr><th>Phase</th><th>Check</th><th>Rollback</th></tr></thead>
<tbody>
<tr><td>Discover</td><td>Who owns the number today, which gateway, which recording profile, which emergency location.</td><td>Nothing has moved. Write the owner down.</td></tr>
<tr><td>Normalize</td><td>+E.164 on both systems so the same digits mean the same destination.</td><td>Keep the old habit in a translation you can remove.</td></tr>
<tr><td>Canary</td><td>One user. Inbound, outbound, hold, transfer, voicemail, and emergency callback to the right site.</td><td>Send the number back to the original system the same day.</td></tr>
<tr><td>Cut</td><td>A named cohort, a window, and one person who can stop the window.</td><td>The trigger is a failed canary proof, not a feeling.</td></tr>
<tr><td>Evidence</td><td>A ladder, a CDR or cloud record, and the emergency test you are allowed to run.</td><td>If evidence is missing, you are not done, even if users are quiet.</td></tr>
</tbody></table></div>
<h2>From platforms other than CUCM</h2>
<p>The same five rows apply to a PBX, another UC cloud, or a contact-center number. What changes is the object name: a Webex location, a Teams voice routing policy, a UCCE dialed number, a Webex Contact Center entry point. Do not reuse a CUCM CSS screenshot as if it were the other product's screen.</p>
<p>Florida Crystals, in Microsoft's public story, decommissioned on-premises PBX lines after Teams Phone. That is an outcome on their page, not a template you can copy without the discovery rows above.</p>
{sources([("Webex Calling help", "https://help.webex.com/"), ("Florida Crystals story", "https://www.microsoft.com/en/customers/story/1804528563383903958-florida-crystals-corporation-microsoft-teams-phone-manufacturing-en-united-states"), ("FCC MLTS", FCC)])}
""", "Migration checklist with rollback for each phase.")

    write_page("guide/playbooks.html", "Troubleshooting playbooks", f"""
<p class="kicker">One change</p>
<h1>Playbooks</h1>
<p class="lede">Twenty-nine branching cases are in the case lab. These four are the trees you can print.</p>
<h2>No registration</h2>
<ol>
<li>Is the phone reaching TFTP or the cloud identity host? Desk phones and remote Jabber are different DNS names.</li>
<li>Is there a 401 and then a second REGISTER, or only the first?</li>
<li>Certificates and time before you rebuild the device.</li>
</ol>
<h2>Reorder on an outside number</h2>
<ol>
<li>Does an inside call work? If yes, the phone is registered.</li>
<li>Does the CSS contain a matching pattern? A miss never reaches CUBE.</li>
<li>If CUBE sees no INVITE, the call died in call control. An empty debug is the evidence.</li>
</ol>
<h2>One-way audio</h2>
<ol>
<li>200 OK on both signaling legs.</li>
<li>SDP on the answer that the next hop needed.</li>
<li>RTP both ways after ACK.</li>
<li>Only then DSCP and the jitter buffer.</li>
</ol>
<h2>Agent reserved, phone silent</h2>
<ol>
<li>The script selected an agent. The queue is not empty.</li>
<li>The device that should ring is a different object from the desktop state.</li>
<li>Capture the ring leg. Do not restart the router because the desktop changed color.</li>
</ol>
<p><a href="../cases.html">Open the 29 cases</a></p>
{sources([("RFC 3261", RFC3261), ("UCCE", "https://www.cisco.com/c/en/us/support/customer-collaboration/unified-contact-center-enterprise/series.html")])}
""", "Four troubleshooting trees for registration, reorder, one-way audio, and a silent agent phone.")

    write_page("guide/firewall.html", "Firewall matrix", f"""
<p class="kicker">CUCM 15</p>
<h1>Firewall matrix</h1>
<p class="lede">Direction is from the session originator toward the listener, as the port chapter draws it. Administrators can change numbers. Cisco does not recommend that. Open the chapter for the release you run.</p>
<div class="table-scroll"><table>
<thead><tr><th>From</th><th>To</th><th>Port</th><th>Why it is open</th></tr></thead>
<tbody>
<tr><td>Phone</td><td>CUCM</td><td>69/UDP then ephemeral</td><td>TFTP</td></tr>
<tr><td>Phone</td><td>CUCM</td><td>6970/TCP</td><td>HTTP configuration and firmware</td></tr>
<tr><td>Phone</td><td>CUCM</td><td>5060 TCP/UDP, 5061/TCP</td><td>SIP and SIP TLS</td></tr>
<tr><td>Phone</td><td>CUCM</td><td>2000/TCP, 2443/TCP</td><td>SCCP and secure SCCP</td></tr>
<tr><td>Phone</td><td>CUCM</td><td>3804/TCP</td><td>CAPF</td></tr>
<tr><td>Gateway</td><td>CUCM</td><td>2427/UDP</td><td>MGCP</td></tr>
<tr><td>Gateway</td><td>CUCM</td><td>1720/TCP</td><td>H.225</td></tr>
<tr><td>Phone or gateway</td><td>Phone or gateway</td><td>16384–32767/UDP</td><td>RTP and SRTP. CUCM's own range in the chapter is 24576–32767.</td></tr>
<tr><td>CUCM</td><td>LDAP</td><td>389, 636, 3268, 3269/TCP</td><td>Directory</td></tr>
<tr><td>Application</td><td>CUCM</td><td>2748/TCP, 2749/TCP</td><td>CTI and CTI over TLS</td></tr>
<tr><td>Application</td><td>CUCM</td><td>8443/TCP</td><td>AXL / SOAP</td></tr>
<tr><td>Gateway</td><td>CUCM</td><td>8090/TCP</td><td>Gateway recording HTTP</td></tr>
<tr><td>CUCM</td><td>CSSM</td><td>443/HTTPS</td><td>Smart Licensing usage</td></tr>
<tr><td>CUCM</td><td>NTP</td><td>123/UDP</td><td>Time</td></tr>
<tr><td>Browser</td><td>CUCM</td><td>443, 8443/TCP</td><td>Administration</td></tr>
</tbody></table></div>
<p>Ephemeral ports on the node are 32768–61000 and the chapter says they need to stay open for phones to remain registered. Multicast music-on-hold uses the ports you configure. They are not in this matrix on purpose.</p>
{sources([("CUCM 15 port usage", PORT_DOC)])}
""", "Firewall-style matrix from the CUCM 15 port chapter.")

    write_page("guide/pstn.html", "PSTN and bring your own carrier", f"""
<p class="kicker">Who owns the trunk</p>
<h1>PSTN, SIP trunking, and bring-your-own carrier</h1>
<p class="lede">"Bring your own carrier" means the PSTN contract stays with you and an SBC you operate sits between that carrier and the call control. It is not a single product.</p>
<div class="table-scroll"><table>
<thead><tr><th>Call control</th><th>PSTN choices</th><th>Where you look when it fails</th></tr></thead>
<tbody>
<tr><td>Unified CM</td><td>SIP trunk to CUBE or another SBC, MGCP or H.323 gateway, or a trunk to another cluster</td><td>CSS, route list, then both dial-peers</td></tr>
<tr><td>Webex Calling</td><td>Cisco Calling Plan, or a local gateway you manage for that location</td><td>The location's PSTN model first. Calling Plan has no local gateway.</td></tr>
<tr><td>Teams Phone</td><td>Microsoft Calling Plan, Operator Connect, or Direct Routing through a certified SBC</td><td>The user's connectivity type. OPTIONS only if an SBC is on the path.</td></tr>
<tr><td>Contact center</td><td>The same PSTN as the PBX, or the cloud's own numbers, or a certified SBC into Teams (the Connect model)</td><td>Entry point or dialed number, then the carrier leg</td></tr>
</tbody></table></div>
<p>A SIP trunk is still RFC 3261 plus the trunk's own profile: early or delayed offer, transport, and which numbers are accepted. Two carriers at the same preference will split calls. OPTIONS can busy one of them out.</p>
<p>The Logicalis marketplace listing describes Teams Calling with Webex Contact Center through Direct Routing and CUBE. That is a published partner pattern, not a measurement and not the only legal design. Microsoft's contact-center article is the model list: Connect, Extend, and Unify.</p>
{sources([("RFC 3261", RFC3261), ("Direct Routing plan", "https://learn.microsoft.com/en-us/microsoftteams/direct-routing-plan"), ("Teams contact center", "https://learn.microsoft.com/en-us/microsoftteams/teams-contact-center"), ("Webex Calling help", "https://help.webex.com/")])}
""", "PSTN options for CUCM, Webex Calling, Teams Phone, and contact center.")

    write_page("guide/security.html", "Security and compliance", f"""
<p class="kicker">Fence the dial plan</p>
<h1>Security and compliance</h1>
<ul>
<li><strong>Toll fraud.</strong> Auto-registration that can reach the PSTN, or a short translation that grows into an international pattern, is a class-of-service hole. Close the CSS. Do not start by rebooting.</li>
<li><strong>TLS is not SRTP.</strong> 5061 protects signaling. SRTP, RFC 3711, protects audio. Require both only on hops that can answer both.</li>
<li><strong>Recording.</strong> Gateway recording HTTP is 8090/TCP in the port chapter. SIPREC is RFC 7866. Whether you may record, and what you must tell the caller, is local law. This page is not legal advice.</li>
<li><strong>Emergency.</strong> Kari's Law and RAY BAUM'S Act are United States MLTS duties. Other countries have their own rules. A lab ladder is not your filing.</li>
<li><strong>Identity.</strong> LDAP on 389, 636, 3268, or 3269. Certificates from CAPF on 3804. A public DNS name for an internal service is a publish decision, not a convenience.</li>
<li><strong>This repository.</strong> No customer captures, no live credentials, no dial plans from a real company. Examples use documentation addresses already allowed in the campus checker.</li>
</ul>
{sources([("RFC 3711", "https://www.rfc-editor.org/rfc/rfc3711"), ("RFC 7866", "https://www.rfc-editor.org/rfc/rfc7866"), ("CUCM 15 port usage", PORT_DOC), ("FCC MLTS", FCC)])}
""", "Toll fraud, TLS versus SRTP, recording, and the limits of this lab.")

    samples = []
    seen = set()
    for question in bank["questions"]:
        track = question.get("track") or "General"
        if track in seen:
            continue
        seen.add(track)
        samples.append(question)
        if len(samples) == 6:
            break
    items = []
    for question in samples:
        choices = "".join(f"<li>{choice}</li>" for choice in question.get("choices") or [])
        answer = (question.get("choices") or [""])[question.get("answer") or 0]
        q_track = html.escape(str(question.get("track") or "General"))
        items.append(
            f"<article class='paper'><h2>{html.escape(str(question.get('q') or ''))}</h2><p class='muted'>{q_track}</p><ul>{choices}</ul>"
            f"<p><strong>Reason in the bank:</strong> {html.escape(str(answer))}</p></article>"
        )
    write_page("guide/interview.html", "Interview and career", f"""
<p class="kicker">Show the leg</p>
<h1 data-i18n="pageCareers">Interview prep and career path</h1>
<p class="lede">Six questions from the idea-pool bank, one track each. The scored quiz has the other {len(bank['questions']) - 6}. Open a stop on the timeline. This lab does not publish wages.</p>
<ol class="timeline">
<li><button type="button" aria-expanded="true">01 · Voice and SIP</button><div class="time-body"><p>Draw registration and a basic call. A 200 OK is not audio.</p></div></li>
<li><button type="button" aria-expanded="false">02 · Call control and the SBC</button><div class="time-body" hidden><p>CSS miss, dial-peer 0, or a carrier timeout. Name which leg.</p></div></li>
<li><button type="button" aria-expanded="false">03 · Cloud PSTN</button><div class="time-body" hidden><p>Calling Plan, local gateway, Operator Connect, Direct Routing. Do not mix their traces.</p></div></li>
<li><button type="button" aria-expanded="false">04 · Around the agent</button><div class="time-body" hidden><p>Call type or entry point, then recording, WFM, CRM, and a handoff.</p></div></li>
<li><button type="button" aria-expanded="false">05 · Proof you can show</button><div class="time-body" hidden><p>Cisco's February 2026 set is one public map: CLCOR, then a concentration. It is not the only way to be hired. The certifications page has the exam names.</p></div></li>
</ol>
{''.join(items)}
<h2>A path, not a salary table</h2>
<p>This lab does not publish wages. Hiring pages move, and a number here would be a guess. The work itself has a readable order:</p>
<ol>
<li><strong>Voice and SIP.</strong> You can draw registration and a basic call, and you can say why a 200 OK is not audio.</li>
<li><strong>Call control and the SBC.</strong> You can explain a CSS miss versus dial-peer 0 versus a carrier timeout.</li>
<li><strong>Cloud PSTN.</strong> You can name Calling Plan, local gateway, Operator Connect, and Direct Routing without mixing their traces.</li>
<li><strong>Contact center and the systems around it.</strong> Call type or entry point, then recording, WFM, CRM, and a virtual agent that can hand off.</li>
</ol>
<p>Cisco's February 2026 certification set is one public map of that work: CLCOR, then a concentration. It is not the only way to be hired. The certifications page has the exam names and the blog link.</p>
{sources([("Cisco learning blog", BLOG), ("350-801 CLCOR", "https://www.cisco.com/site/us/en/learn/training-certifications/exams/clcor.html")])}
""", "Interview questions from the bank and a career sequence without invented wages.")

    write_page("guide/whats-new.html", "What's new", f"""
<p class="kicker">As of October 2026</p>
<h1>What's new, and what this page will not pretend</h1>
<div class="table-scroll"><table>
<thead><tr><th>Item</th><th>Status</th><th>Source</th></tr></thead>
<tbody>
<tr><td>CCNP Collaboration v2.0 testing starts 3 February 2026. v1.2 testing ended 2 February 2026. The blog describes a 50/50 cloud and on-premises split.</td><td>Verified against Cisco's learning blog</td><td><a href="{BLOG}">Cisco learning blog</a></td></tr>
<tr><td>350-801 CLCOR remains the 120-minute core. 300-815 CLACC v2.0 is the on-premises call-control concentration. 300-820 is published there as CLHCT, hybrid and cloud. 300-830 CLCCE is introduced as the cloud customer-experience concentration.</td><td>Verified against that blog and the CLCOR and CLACC pages linked from the certifications page</td><td><a href="{BLOG}">Blog</a></td></tr>
<tr><td>The CUCM Release 15 system configuration book's revision history includes a February 5, 2026 note about NSE-based fax or passthrough for secure SIP lines.</td><td>Verified against the public book text retrieved for this lab</td><td><a href="{SYS}">System configuration guide</a></td></tr>
<tr><td>Port numbers in the firewall matrix match the Release 15 port chapter retrieved for this lab, including 8090 for gateway recording and 443 for Smart Licensing to CSSM.</td><td>Verified against that chapter</td><td><a href="{PORT_DOC}">Port chapter</a></td></tr>
<tr><td>Webex Calling commercial SKU names and prices for October 2026.</td><td>Unverified here. Read Control Hub help before you quote a SKU.</td><td><a href="https://help.webex.com/">Webex help</a></td></tr>
<tr><td>The current Microsoft collaboration exam code.</td><td>Unverified here. The certifications page refuses to freeze a code this build did not re-check.</td><td><a href="https://learn.microsoft.com/en-us/microsoftteams/teams-phone-landing-page">Teams Phone</a></td></tr>
<tr><td>Any "2026 feature" that is not in the rows above.</td><td>Unverified. Do not treat this lab as a product roadmap.</td><td>None</td></tr>
</tbody></table></div>
{sources([("Cisco learning blog", BLOG), ("CUCM 15 system configuration", SYS), ("CUCM 15 port usage", PORT_DOC)])}
""", "Cited 2026 changes, with unverified rows marked.")

    write_page("ecosystem/wfm.html", "Workforce management", f"""
<p class="kicker">Sister system</p>
<h1>Workforce management, forecasting, and scheduling</h1>
<p class="lede">WFM forecasts how many people you need and then builds schedules. It does not route the call. The contact center still owns the queue.</p>
<h2>What you configure</h2>
<ul>
<li>The same agent identifier in the ACD and in the WFM feed.</li>
<li>Interval length, usually 15 or 30 minutes, in the contact center's timezone.</li>
<li>Average handle time, shrinkage, and the queue or skill the forecast is for.</li>
<li>A schedule that can be wrong if the forecast interval does not match the ACD export.</li>
</ul>
<h2>Teaching load calculator</h2>
<p>Offered load in erlangs is calls per hour times average handle time in seconds, divided by 3600. Erlang B below is the iterative form. Erlang C is reported only as a teaching probability of waiting. It is not NICE, Verint, Calabrio, Genesys, or Webex Workforce Optimization.</p>
<form id="erlangForm" class="paper">
<label class="field">Calls per hour <input id="erlangCalls" type="number" value="120" min="1"></label>
<label class="field">Handle time seconds <input id="erlangAht" type="number" value="180" min="1"></label>
<label class="field">Agents <input id="erlangAgents" type="number" value="8" min="1"></label>
<p id="erlangOut"></p>
</form>
<h2>Troubleshooting</h2>
<ul>
<li>Adherence stuck after logout: the logout event never arrived.</li>
<li>A missing interval stays missing unless the product documents a backfill.</li>
<li>A renumbered skill looks like a new queue, so yesterday's forecast no longer matches.</li>
</ul>
{sources([("Webex help", "https://help.webex.com/"), ("UCCE", "https://www.cisco.com/c/en/us/support/customer-collaboration/unified-contact-center-enterprise/series.html")])}
""", "Workforce forecasting, a teaching Erlang calculator, and schedule failure modes.")

    write_page("ecosystem/crm.html", "CRM and APIs", f"""
<p class="kicker">Sister system</p>
<h1>CRM and API integrations</h1>
<p class="lede">A screen pop needs a number the CRM can match, and an API needs an id you can say out loud in a ticket.</p>
<h2>Screen pop</h2>
<ul>
<li>Pick one key: +E.164, national digits, or an internal customer id. Write it down.</li>
<li>Webex Contact Center, a Finesse gadget, and a Teams contact-center model each pop from their own event.</li>
<li>A miss is often formatting. A wrong record is often two customers on one main number.</li>
</ul>
<h2>APIs you can name without inventing a payload</h2>
<ul>
<li><strong>AXL / SOAP on CUCM</strong> listens on 8443/TCP in the port chapter. It reads and writes the database for provisioning applications. The WSDL for your version is the contract, not this page.</li>
<li><strong>Webex</strong> publishes APIs at the Webex developer site. Calling and contact center objects are different. Do not reuse an admin click as if it were a REST field.</li>
<li><strong>Microsoft Graph</strong> has a communications overview for Teams workloads. Direct Routing health is still an SBC problem when the user is on Direct Routing.</li>
</ul>
<p>Future hooks, not features this lab turns on: a stable interaction id on the CTI or webhook event, SIPREC on the SBC, and +E.164 at every boundary. They are named on the bridges page.</p>
{sources([("CUCM 15 port usage", PORT_DOC), ("Webex for developers", "https://developer.webex.com/"), ("Microsoft Graph communications", "https://learn.microsoft.com/en-us/graph/api/resources/communications-api-overview"), ("Teams contact center", "https://learn.microsoft.com/en-us/microsoftteams/teams-contact-center")])}
""", "CRM screen pop and the APIs an engineer can name without a guessed payload.")


def write_play(write_page, sources, bank: dict) -> None:
    write_page("play/index.html", "Play", """
<p class="kicker">Practice</p>
<h1 data-i18n="pagePlay">Play</h1>
<p class="lede">Scores stay in this browser. Nothing is sent to a server. Break a hop in the sim, then open a full game.</p>
<section class="sim glass" id="labSim">
<h2>Break a hop</h2>
<div class="sim-board" id="simBoard">
<span data-node="register">Phone</span><i data-link="register"></i>
<span data-node="css">CUCM</span><i data-link="css"></i>
<span data-node="pstn">SBC</span><i data-link="pstn"></i>
<span data-node="pstn-end">PSTN</span>
<span data-node="webex">Webex</span>
<span data-node="teams">Teams</span>
<span data-node="ucce">UCCE</span>
</div>
<p id="simOut">Choose a hop. The note is the teaching read from this lab, not a live trace.</p>
<div class="sim-path">
<button type="button" data-hop="register">Phone → CUCM</button>
<button type="button" data-hop="css">CUCM → SBC</button>
<button type="button" data-hop="pstn">SBC → PSTN</button>
<button type="button" data-hop="webex">Webex location</button>
<button type="button" data-hop="teams">Teams PSTN</button>
<button type="button" data-hop="ucce">UCCE</button>
</div>
</section>
<div class="atlas">
<a class="card" href="ports-game.html"><h2>Ports game</h2><p>Eight rounds. Six correct earns a badge.</p></a>
<a class="card" href="map.html"><h2>Flow map</h2><p>Click the nodes. Three opens earn a badge.</p></a>
<a class="card" href="sandbox.html"><h2>Build a ladder</h2><p>Phone, CUCM, CUBE, PSTN. Three messages earn a badge.</p></a>
<a class="card" href="daily.html"><h2>Daily challenge</h2><p>One bank question, stable for the UTC date.</p></a>
<a class="card" href="badges.html"><h2>Badges</h2><p>Ten badges. The joystick code is one of them.</p></a>
</div>
<canvas id="shareCanvas" class="share-card" width="640" height="360" aria-label="Shareable result card"></canvas>
<div class="actions"><button type="button" class="btn" id="shareBtn" data-title="UC Lab play" data-line="Teaching result. Links home at cyphermonkeylabs.com">Download result card</button></div>
<p class="muted">An old joystick code still works on any page of this lab.</p>
""", "Ports game, flow map, sandbox, daily challenge, and badges.")

    deck = [
        {"ask": "SIP signaling for a phone or a gateway", "port": "5060 TCP/UDP", "decoys": ["5061 TCP", "2000 TCP", "443 TCP"], "why": "5060 is SIP. 5061 is SIP over TLS. Both are in the CUCM 15 port chapter."},
        {"ask": "SIP over TLS", "port": "5061 TCP", "decoys": ["5060 UDP", "8443 TCP", "22 TCP"], "why": "5061/TCP is secure SIP in the phone and gateway tables."},
        {"ask": "SCCP from a phone", "port": "2000 TCP", "decoys": ["2443 TCP", "69 UDP", "1720 TCP"], "why": "2000/TCP is SCCP. 2443/TCP is secure SCCP."},
        {"ask": "TFTP so a phone can download its file list", "port": "69 UDP", "decoys": ["6970 TCP", "123 UDP", "514 UDP"], "why": "69/UDP is TFTP. 6970/TCP is the HTTP download that follows."},
        {"ask": "CAPF, locally significant certificates", "port": "3804 TCP", "decoys": ["2444 TCP", "22 TCP", "443 TCP"], "why": "3804/TCP is the CAPF listening port in the phone table."},
        {"ask": "CTI from an application", "port": "2748 TCP", "decoys": ["2749 TCP", "8443 TCP", "5060 TCP"], "why": "2748/TCP is CTI. 2749/TCP is CTI over TLS."},
        {"ask": "AXL / SOAP provisioning", "port": "8443 TCP", "decoys": ["443 TCP", "8080 TCP", "6970 TCP"], "why": "The application table lists 8443/TCP for AXL / SOAP."},
        {"ask": "Gateway recording HTTP", "port": "8090 TCP", "decoys": ["5060 TCP", "16384 UDP", "2427 UDP"], "why": "8090 is the gateway recording HTTP port in the intracluster table."},
        {"ask": "Smart Licensing toward CSSM", "port": "443 HTTPS", "decoys": ["8443 TCP", "22 TCP", "123 UDP"], "why": "Table 10 in the port chapter is 443/HTTPS from the Smart Licensing service to CSSM."},
        {"ask": "RTP and SRTP between phones and gateways", "port": "16384-32767 UDP", "decoys": ["5060 UDP", "24576 only", "32768-61000 TCP"], "why": "The chapter gives 16384-32767 for devices, and notes CUCM itself uses 24576-32767."},
        {"ask": "MGCP gateway control", "port": "2427 UDP", "decoys": ["2428 TCP", "2000 TCP", "1720 TCP"], "why": "2427/UDP is MGCP control. 2428/TCP is MGCP backhaul."},
        {"ask": "NTP", "port": "123 UDP", "decoys": ["53 TCP", "161 UDP", "22 TCP"], "why": "123/UDP is NTP from CUCM to the time server."},
    ]
    write_page("play/ports-game.html", "Ports game", f"""
<p class="kicker">Mastery game</p>
<h1>Ports and protocols</h1>
<p class="lede">Pick the port. The reason cites the CUCM 15 chapter, not a high score from a vendor.</p>
<script type="application/json" id="portDeck">{json.dumps(deck)}</script>
<div id="portsGame" class="paper"></div>
<p><a href="../guide/firewall.html">Open the firewall matrix</a> · <a href="../ports.html">Open the filterable table</a></p>
{sources([("CUCM 15 port usage", PORT_DOC)])}
""", "A ports and protocols quiz game.")

    nodes = [
        ("Phone", "SIP or SCCP toward CUCM. Media comes later.", "../flows/registration.html"),
        ("CUCM", "Call control, CSS, and the trunk.", "../flows/dial-plan.html"),
        ("CUBE", "Two dial-peers. Two SDPs.", "../flows/cube.html"),
        ("PSTN", "The carrier leg. OPTIONS can busy it out.", "../flows/pstn.html"),
        ("Webex", "Calling Plan or a local gateway. Not both on one location.", "../flows/webex-lgw.html"),
        ("Teams", "Calling Plan, Operator Connect, or Direct Routing.", "../flows/teams-dr.html"),
        ("UCCE", "Dialed number, call type, script, agent.", "../flows/ucce.html"),
        ("WFM", "Forecast and schedule. Not the route.", "../ecosystem/wfm.html"),
        ("Recorder", "Forked audio. A score is not the file.", "../ecosystem/recording.html"),
        ("Emergency", "Location and callback. A connected wrong site is a failure.", "../flows/e911.html"),
    ]
    buttons = "".join(
        f"<button type='button' class='choice' data-map='{name}' data-blurb='{blurb}' data-href='{href}'>{name}</button>"
        for name, blurb, href in nodes
    )
    write_page("play/map.html", "Flow map", f"""
<p class="kicker">Explorer</p>
<h1>Network and flow map</h1>
<p class="lede">Open three nodes. The detail pane is the job of that box, with a link into the lab.</p>
<div class="map-layout">
<div class="paper">{buttons}</div>
<aside id="mapDetail" class="paper"><p>Choose a node.</p></aside>
</div>
""", "Clickable flow map of the lab.")

    write_page("play/sandbox.html", "Call-flow sandbox", """
<p class="kicker">Your ladder</p>
<h1>Build a call flow</h1>
<p class="lede">Four actors. Add a message. This does not generate a packet. It teaches you to name the hop.</p>
<div class="sandbox-row">
<label>From <select id="sbFrom"><option>Phone</option><option>CUCM</option><option>CUBE</option><option>PSTN</option></select></label>
<label>To <select id="sbTo"><option>CUCM</option><option>Phone</option><option>CUBE</option><option>PSTN</option></select></label>
<label>Label <input id="sbLabel" value="INVITE" maxlength="24" aria-label="Message label"></label>
<button type="button" class="btn" id="sbAdd">Add message</button>
</div>
<p id="sbBoard" class="muted"></p>
<div id="sbSvg" class="ladder"></div>
""", "Sandbox for assembling a four-actor ladder.")

    write_page("play/daily.html", "Daily challenge", f"""
<p class="kicker">One question</p>
<h1>Daily challenge</h1>
<p class="lede">The index is the UTC date modulo the size of the bank, so the question is stable for that UTC day and changes the next day. It is one of the {len(bank["questions"])} questions in the idea-pool bank, not a new invention.</p>
<div id="dailyHost" class="paper"><p>Loading the bank.</p></div>
<canvas id="shareCanvas" class="share-card" width="640" height="360" aria-label="Daily result card"></canvas>
<div class="actions"><button type="button" class="btn" id="shareBtn" data-title="Daily challenge" data-line="One question from the idea-pool bank.">Download result card</button></div>
""", "One UTC-stable question from the quiz bank.")

    write_page("play/badges.html", "Badges", """
<p class="kicker">This browser</p>
<h1>Badges</h1>
<p class="lede">Earned badges are a timestamp in local storage. Clearing site data clears them. They are not certificates.</p>
<div id="badgeList" class="atlas"></div>
""", "Local achievement badges for the flagship lab.")


def write_cheats(write_page, sources, bank: dict) -> list[str]:
    sheets = [
        ("ports", "Ports and protocols", f"""
<h1>Ports cheat sheet</h1>
<p>CUCM 15 port chapter. Confirm the release before you open a firewall.</p>
<ul>
<li>5060 SIP · 5061 SIP TLS · 2000 SCCP · 2443 secure SCCP</li>
<li>69 TFTP · 6970 HTTP files · 3804 CAPF</li>
<li>2427 MGCP · 1720 H.225 · 2748 CTI · 2749 CTI TLS · 8443 AXL</li>
<li>16384–32767 RTP on devices · CUCM uses 24576–32767</li>
<li>8090 gateway recording · 443 Smart Licensing to CSSM · 123 NTP · 22 SFTP</li>
</ul>
"""),
        ("firewall", "Firewall matrix", """
<h1>Firewall cheat sheet</h1>
<ul>
<li>Phone to CUCM: 69/UDP, 6970/TCP, 5060, 5061, 2000 or 2443, 3804</li>
<li>Gateway to CUCM: 2427/UDP or 1720/TCP, plus RTP</li>
<li>RTP between media hosts: UDP 16384–32767 unless you have changed it</li>
<li>Apps to CUCM: 2748/2749 CTI, 8443 AXL</li>
<li>CUCM to the world: 123 NTP, 389/636/3268/3269 LDAP, 443 CSSM, 22 backup</li>
<li>Keep ephemeral 32768–61000 open on the node or phones drop</li>
</ul>
"""),
        ("call-flows", "Call flows", """
<h1>Call-flow cheat sheet</h1>
<ol>
<li>REGISTER, 401, REGISTER, 200. No media.</li>
<li>INVITE, 100 from each hop, 180, 200, ACK. RTP can skip the proxy.</li>
<li>Hold is a re-INVITE with sendonly or inactive, then the matching answer.</li>
<li>Blind REFER gets 202. 202 is not answer. Read NOTIFY.</li>
<li>Early media is 183 with SDP, not a confirmed dialog.</li>
</ol>
"""),
        ("config", "Configuration checklist", """
<h1>Config checklist</h1>
<ol>
<li>Line CSS before device CSS.</li>
<li>Emergency partition before any 9.@ partition.</li>
<li>Inbound dial-peer named. Dial-peer 0 means you missed.</li>
<li>Early offer or delayed offer written down per leg.</li>
<li>Webex location PSTN model named before the trace.</li>
<li>Teams connectivity type named before the SBC trace.</li>
</ol>
"""),
        ("troubleshoot", "Troubleshooting tree", """
<h1>Troubleshooting tree</h1>
<ol>
<li>Registered? If no, DNS, TFTP or edge, 401, time, certificate.</li>
<li>Inside calls work and outside reorder? CSS, then route list, then an empty CUBE trace.</li>
<li>Connected and one-way? SDP on both answers, then RTP both ways, then QoS.</li>
<li>Reserved and silent? The desktop state is not the ring. Capture the phone leg.</li>
</ol>
"""),
        ("glossary", "Glossary", """
<h1>Glossary cheat sheet</h1>
<ul>
<li>CSS — ordered partitions. Line, then device.</li>
<li>Dial-peer 0 — no inbound peer matched.</li>
<li>Early offer — SDP in INVITE. Delayed offer — SDP in the 200.</li>
<li>B2BUA — two legs. Read both.</li>
<li>ELIN — callback identity for the site that called emergency services.</li>
<li>Call type — UCCE report bucket selected by the dialed number.</li>
<li>EF 46 — voice RTP mark. Still needs a priority queue.</li>
</ul>
"""),
        ("pstn", "PSTN options", """
<h1>PSTN cheat sheet</h1>
<ul>
<li>CUCM: SIP trunk, MGCP, H.323, or ICT. CUBE is a B2BUA in front of a carrier you keep.</li>
<li>Webex Calling: Calling Plan, or local gateway. Not both for one location.</li>
<li>Teams: Calling Plan, Operator Connect, or Direct Routing.</li>
<li>Bring your own carrier: your contract, your SBC, their call control.</li>
</ul>
"""),
        ("e911", "Emergency", """
<h1>Emergency cheat sheet</h1>
<ul>
<li>Direct 911. A required prefix fails Kari's Law in the United States.</li>
<li>On-site notification is a second duty.</li>
<li>Callback must reach the site that dialed, not a headquarters receptionist.</li>
<li>Webex and Teams locations are not a CUCM ELIN. Name the product before you test.</li>
</ul>
"""),
        ("qos", "QoS", """
<h1>QoS cheat sheet</h1>
<ul>
<li>Voice RTP is commonly EF, DSCP 46. Confirm the service parameter.</li>
<li>Cisco designs often mark signaling CS3. RFC 4594 assigns signaling to CS5.</li>
<li>A mark without a priority queue is a label.</li>
<li>G.711 at 20 ms is 80 kbit/s at layer 3 and 87.2 kbit/s with an 18-byte Ethernet header.</li>
<li>G.114 planning talk is about one-way delay around 150 ms.</li>
</ul>
"""),
        ("migration", "Cutover", """
<h1>Cutover cheat sheet</h1>
<ol>
<li>Discover owner, gateway, recording, emergency location.</li>
<li>Normalize to +E.164.</li>
<li>Canary one user, including callback.</li>
<li>Write the rollback before the window.</li>
<li>Stop if the canary proof is missing.</li>
</ol>
"""),
        ("security", "Security", """
<h1>Security cheat sheet</h1>
<ul>
<li>PSTN-capable auto-registration is toll fraud waiting.</li>
<li>TLS locks signaling. SRTP locks audio.</li>
<li>8090 is gateway recording HTTP. Consent is not a port.</li>
<li>This lab stores no customer data and places no live call.</li>
</ul>
"""),
        ("wfm-recording", "WFM and recording", """
<h1>WFM and recording cheat sheet</h1>
<ul>
<li>WFM needs the same agent id, the same interval, and the contact-center timezone.</li>
<li>A forecast is not a route. Scheduling does not make the phone ring.</li>
<li>Recording is the audio. Quality management is a score of that audio.</li>
<li>One-way on the recorder is still an SDP problem.</li>
</ul>
"""),
    ]
    cites = {
        "ports": f'<p class="muted">Source: <a href="{PORT_DOC}">CUCM 15 TCP and UDP port usage</a>. This sheet is a note, not that chapter.</p>',
        "firewall": f'<p class="muted">Source: <a href="{PORT_DOC}">CUCM 15 TCP and UDP port usage</a>.</p>',
        "call-flows": f'<p class="muted">Source: <a href="{RFC3261}">RFC 3261</a>. Ladder pages in this lab expand each line.</p>',
        "config": f'<p class="muted">Sources: <a href="{SYS}">CUCM 15 system configuration</a>, <a href="https://help.webex.com/">Webex Calling help</a>, <a href="https://learn.microsoft.com/en-us/microsoftteams/direct-routing-plan">Direct Routing plan</a>.</p>',
        "troubleshoot": f'<p class="muted">Source: <a href="{RFC3261}">RFC 3261</a> for the signaling checks. The 29 cases are the longer trees.</p>',
        "glossary": f'<p class="muted">Terms used in this lab. Port numbers still come from <a href="{PORT_DOC}">the CUCM 15 port chapter</a>.</p>',
        "pstn": '<p class="muted">Sources: <a href="https://help.webex.com/">Webex Calling help</a>, <a href="https://learn.microsoft.com/en-us/microsoftteams/direct-routing-plan">Direct Routing plan</a>, <a href="https://www.rfc-editor.org/rfc/rfc3261">RFC 3261</a>.</p>',
        "e911": f'<p class="muted">Source: <a href="{FCC}">FCC MLTS 911 requirements</a>. Other countries have their own rules.</p>',
        "qos": '<p class="muted">Sources: <a href="https://www.rfc-editor.org/rfc/rfc4594">RFC 4594</a> and the CUCM QoS service parameters for the release you run.</p>',
        "migration": '<p class="muted">A teaching checklist. Florida Crystals is a published outcome, not a template: <a href="https://www.microsoft.com/en/customers/story/1804528563383903958-florida-crystals-corporation-microsoft-teams-phone-manufacturing-en-united-states">Microsoft customer story</a>.</p>',
        "security": f'<p class="muted">Sources: <a href="https://www.rfc-editor.org/rfc/rfc3711">RFC 3711</a>, <a href="https://www.rfc-editor.org/rfc/rfc7866">RFC 7866</a>, <a href="{PORT_DOC}">CUCM 15 port usage</a>.</p>',
        "wfm-recording": '<p class="muted">Teaching notes. Forecast math here is not a vendor workforce product.</p>',
    }
    slugs = []
    for slug, title, body in sheets:
        slugs.append(slug)
        write_page(
            f"cheats/{slug}.html",
            title,
            f"<article class='cheat-sheet'><p class='kicker'>Cheat code</p>{body}{cites[slug]}{cheat_foot()}</article>",
            title,
        )
    rows = []
    for card in bank["pr2Cards"][:12]:
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                html.escape(str(card.get("q") or "")),
                html.escape(str(card.get("a") or "")),
                html.escape(str(card.get("cite") or "")),
            )
        )
    slugs.append("flashcards")
    write_page(
        "cheats/flashcards.html",
        "Printable flashcards",
        f"""<article class="cheat-sheet"><p class="kicker">Cheat code</p><h1>Twelve cited cards</h1>
<p>The JSON files next to this page hold the full cited deck ({len(bank['pr2Cards'])}) and the idea-pool deck ({len(bank['cards'])}). This page is the one-page pass.</p>
<table class="deck"><thead><tr><th>Question</th><th>Answer</th><th>Cite</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
{cheat_foot()}</article>""",
        "Printable cited flashcards.",
    )
    links = "".join(f"<li><a href='{slug}.html'>{slug}</a> · <a href='{slug}.pdf'>PDF</a> · <a href='{slug}.png'>PNG</a></li>" for slug in slugs)
    faces = {
        "ports": "5060 SIP, 5061 TLS, 2000 SCCP, 69 TFTP, 6970 HTTP. From the CUCM 15 port chapter.",
        "firewall": "Phones to CUCM, gateways, applications, then CUCM outward. The matrix is the sheet, not a live ACL.",
        "call-flows": "REGISTER stores a binding. The call is not up until ACK. A 200 OK is not audio.",
        "config": "Line CSS before device CSS. Early offer is SDP in the INVITE. Delayed offer is SDP in the 200.",
        "troubleshoot": "One leg, one identifier, one change, then the capture. Reorder outside is often CSS before CUBE.",
        "glossary": "CSS, partition, dial-peer 0, early offer, B2BUA, ELIN, call type, EF 46.",
        "pstn": "CUCM trunk, Webex Calling Plan or local gateway, Teams Calling Plan or Operator Connect or Direct Routing.",
        "e911": "Direct 911 in the US. Callback must return to the site that dialed. Name the product before the test.",
        "qos": "Voice RTP is commonly EF 46. Cisco signaling designs often use CS3. RFC 4594 assigns signaling CS5.",
        "migration": "Discover, normalize to +E.164, canary including callback, write the rollback, stop if proof is missing.",
        "security": "TLS locks signaling. SRTP locks audio. 8090 is gateway recording HTTP. Consent is not a port.",
        "wfm-recording": "Same agent id, same interval, contact-center timezone. A forecast does not route the call.",
        "flashcards": "Twelve cited cards on the printable page. The JSON files hold the full decks.",
    }
    titles = {slug: title for slug, title, _body in sheets}
    titles["flashcards"] = "Flashcards"
    flips = []
    for slug in slugs:
        flips.append(
            f"<div class='flip glass' tabindex='0' role='button' aria-pressed='false'>"
            f"<span class='flip-face flip-front'><strong>{html.escape(titles.get(slug, slug))}</strong><em>Flip</em></span>"
            f"<span class='flip-face flip-back'><span>{html.escape(faces.get(slug, 'Open the sheet.'))}</span>"
            f"<span class='flip-links'><a href='{slug}.html'>Sheet</a> · <a href='{slug}.pdf'>PDF</a> · <a href='{slug}.png'>PNG</a></span></span></div>"
        )
    write_page("cheats/index.html", "Cheat codes", f"""
<p class="kicker">Downloads</p>
<h1 data-i18n="pageCheats">Cheat codes</h1>
<p class="lede">Flip a card. The back is the short read. The sheet, PDF, and PNG are the one-page files. Vendor books stay at the links on each study page.</p>
<div class="flip-grid">{''.join(flips)}</div>
<h2>Flashcard files</h2>
<ul>
<li><a href="flashcards-cited.json">Cited deck JSON</a> · {len(bank['pr2Cards'])} cards</li>
<li><a href="flashcards-idea-pool.json">Idea-pool deck JSON</a> · {len(bank['cards'])} cards</li>
<li><a href="flashcards.html">Printable twelve</a></li>
</ul>
<h2>Full offline bundle</h2>
<p><a class="btn dl" href="../uc-lab-flagship.zip">Download the flagship zip</a></p>
<p class="muted">Older October study PDFs remain in the download folder: SIP, SDP, dial plan, CUBE, E911, QoS, and migration.</p>
{cheat_foot()}
""", "Downloadable one-page cheat sheets, flashcard files, and the offline zip.")
    return slugs
