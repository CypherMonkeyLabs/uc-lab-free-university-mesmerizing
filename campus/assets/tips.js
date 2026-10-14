/* Pro tips, interview traps, and a cheat sheet for each study track. */
(function () {
  "use strict";

  function row(term, meaning) {
    return [term, meaning];
  }

  var TRACKS = [
    {
      slug: "start",
      name: "Start here",
      tips: [
        "Say the call leg before the product name. A ladder with no leg is a story.",
        "Write the identifier you will join on before you open a second log.",
        "One change, then the canary. A second change hides which one worked."
      ],
      traps: [
        "Calling a 200 OK proof of audio. Signaling can succeed while RTP is black.",
        "Treating a hostname as the identifier. Call-ID, correlation id, and interaction id are the joins.",
        "Skipping the capture plan because the dashboard is green."
      ],
      sheet: [
        row("Leg", "Which hop failed, named as devices, not as a vendor mood."),
        row("Identifier", "Call-ID, RouterCallKey, interaction id, or the platform's call id."),
        row("Counter", "The metric that must move if the hypothesis is true."),
        row("Capture", "Ladder, packet, CLI, or report interval, with a clock source.")
      ]
    },
    {
      slug: "sip",
      name: "SIP and media",
      tips: [
        "Draw signaling and media as two pictures. They do not have to share a path.",
        "A B2BUA mints a new Call-ID. Join on the header the gateway copies, or on time and numbers.",
        "Name the offer and the answer. Codec failure is an SDP problem wearing a SIP status."
      ],
      traps: [
        "Quoting a single UDP 5060 port for every modern trunk. Many edges are TLS on 5061, or a vendor-specific port.",
        "Assuming PRACK because you saw a 183. Reliable provisional responses are negotiated.",
        "Blaming the codec when the packet was never routed. Look at the IP in the c= line."
      ],
      sheet: [
        row("INVITE", "Starts a dialog when the 200 OK arrives. A provisional response does not."),
        row("Call-ID", "Dialog identity on that hop. It changes across a B2BUA."),
        row("SDP", "Where media wants to go. RFC 3264 is the offer and the answer."),
        row("SRTP", "Encrypted RTP. A locked padlock in a GUI is not the key exchange."),
        row("RFC 4733", "Digits in RTP. SIP INFO digits are a different path.")
      ]
    },
    {
      slug: "cucm-cube",
      name: "CUCM and CUBE",
      tips: [
        "Trace CSS, partition, route pattern, route list, and route group before you open a dial-peer.",
        "On CUBE, bind the signaling and the media to the interface you think you are using.",
        "A SIP trunk security profile that demands TLS will not register to a UDP dial-peer."
      ],
      traps: [
        "Resetting a trunk because one phone is silent. Reset is not a measurement.",
        "Forgetting MTP when the two legs disagree on DTMF or early offer.",
        "Treating Running on the trunk as proof that digit analysis selected it."
      ],
      sheet: [
        row("CSS", "Which partitions this caller may see."),
        row("Route pattern", "The digits CUCM is willing to consume."),
        row("Dial-peer", "CUBE's match. Incoming and outgoing are different peers."),
        row("Bind", "The source address CUBE actually uses."),
        row("MTP", "A media helper. Invoke it on purpose, not as a habit.")
      ]
    },
    {
      slug: "cloud-calling",
      name: "Webex Calling and Teams Phone",
      tips: [
        "Name the PSTN product first: Calling Plan, Local Gateway, Operator Connect, or Direct Routing. The admin screen follows from that choice.",
        "Webex Calling location and Teams voice routing policy are not the same object. Do not reuse a CUCM route-pattern story for both.",
        "Certificate trunks and registration trunks use different ports. Write the port next to the trunk type."
      ],
      traps: [
        "Calling Webex Contact Center a mode of Webex Calling. They are different products.",
        "Looking for a Local Gateway on a Webex Calling Plan location. Calling Plan has no customer gateway.",
        "Assuming media bypass is on because the SBC is certified. Bypass is a policy, and the firewall has to agree.",
        "Pairing an SBC and forgetting the voice route. A healthy OPTIONS ping is not a dial plan."
      ],
      sheet: [
        row("Control Hub", "Webex system of record for users, locations, numbers, and devices."),
        row("Local Gateway", "Customer CUBE. Certificate signaling toward TCP 5062, or a registration trunk on TCP 8934."),
        row("Calling Plan", "Cisco cloud PSTN. No customer Local Gateway on that location."),
        row("Dedicated Instance", "A CUCM-class cloud. Do not run a multi-tenant runbook against it."),
        row("Direct Routing", "Teams to a customer SBC. Pair the FQDN, then the routes."),
        row("Operator Connect", "The carrier is the PSTN join. You do not operate their SBC."),
        row("Voice route", "Teams number pattern plus a PSTN usage that points at an online gateway."),
        row("Media bypass", "Media can skip Microsoft when policy and the network allow it.")
      ]
    },
    {
      slug: "ucce",
      name: "Contact center — UCCE and PCCE",
      tips: [
        "Follow the call into CVP, then the script, then the queue, then the agent. One of those is the leg.",
        "RouterCallKey joins the ICM side. The SIP Call-ID joins the edge. Write both.",
        "PCCE is a packaged topology. Do not invent a random UCCE node and call it the same product."
      ],
      traps: [
        "Treating an agent state change as proof the script queued the call.",
        "Debugging CUIC before the call even reached the queue.",
        "Mixing UCCE skill groups with a CCaaS queue name in the same sentence."
      ],
      sheet: [
        row("Ingress", "Where the carrier or CUBE hands the call to CVP."),
        row("Script", "The routing decision. A script error is not a phone firmware bug."),
        row("Queue", "The wait. Skill group and precision queue are different selectors."),
        row("Finesse", "The agent desktop. State is not the call flow."),
        row("CUIC", "The report. Name the interval and the key.")
      ]
    },
    {
      slug: "ccaas",
      name: "CCaaS and UCaaS platforms",
      tips: [
        "Use the platform's own contact id. Translating it into a SIP Call-ID too early loses the join.",
        "A flow, an IVR, and a queue are three objects. Draw which one ran.",
        "Recording and screen capture are separate consent and storage problems."
      ],
      traps: [
        "Assuming every CCaaS uses SIP end to end. Some legs are proprietary until the PSTN edge.",
        "Copying a Webex Calling dial plan into a contact-center flow.",
        "Declaring the vendor down because one region’s edge is failing over."
      ],
      sheet: [
        row("Contact id", "The platform's join key for that interaction."),
        row("Flow", "The authored logic. Version it."),
        row("Queue", "Who can answer, and the wait target."),
        row("PSTN edge", "Where the contact becomes SIP you can capture."),
        row("Recording", "Who stores it, and which id is on the file.")
      ]
    },
    {
      slug: "e911",
      name: "Emergency calling",
      tips: [
        "Location is configuration plus a test. An untested dispatchable location is a guess.",
        "Write the on-site notification next to the PSAP path. Kari's Law is not a footnote.",
        "Emergency calls do not follow the same outbound permission as a normal national call."
      ],
      traps: [
        "Proving 911 by calling a colleague. Use the provider's test number, such as 933 where that is the published test.",
        "Moving a user to a new location and leaving the emergency address on the old site.",
        "Assuming a soft client inherits the site address of the LAN it happened to join."
      ],
      sheet: [
        row("Dispatchable location", "An address a responder can use, not a building nickname."),
        row("ELIN / ERL", "The callback identity and the zone, in the vocabulary of that design."),
        row("On-site notification", "Who inside the building learns that an emergency call was placed."),
        row("Test call", "A planned call with a record of what the PSAP or test desk saw.")
      ]
    },
    {
      slug: "qos",
      name: "Voice network and QoS",
      tips: [
        "Mark at the trust boundary you control. Re-marking later is a different policy.",
        "Separate delay, jitter, and loss. One MOS number does not say which one moved.",
        "G.711 at 20 ms is 80 kbit/s at layer 3 and 87.2 kbit/s with an 18-byte Ethernet header."
      ],
      traps: [
        "Trusting a phone's DSCP after it crossed an untrusted switch port.",
        "Sizing a WAN class with the codec payload and forgetting the headers.",
        "Using a browser speed test as the voice SLA."
      ],
      sheet: [
        row("EF", "The usual voice class. Confirm the actual marking with a capture."),
        row("150 ms", "ITU-T G.114 one-way planning region, not a measured guarantee."),
        row("Jitter buffer", "Delay you added on purpose to absorb variation."),
        row("MOS", "A model. Say which one. The campus chart is a teaching form of G.107.")
      ]
    },
    {
      slug: "migrations",
      name: "Migrations",
      tips: [
        "A number has a state: old platform, dual-run, or new platform. Write the state before the window.",
        "The rollback owner is a person with a clock, not a paragraph that says revert if needed.",
        "Canary one DID you can call from a network you do not operate."
      ],
      traps: [
        "Porting the number and the route on the same minute with no dual-run.",
        "Declaring cutover done because outbound works. Inbound is a different carrier record.",
        "Forgetting voicemail, recording, and emergency in the feature parity list."
      ],
      sheet: [
        row("Dual-run", "Both platforms can still complete a call for a defined set of numbers."),
        row("Canary", "A number you call after every change."),
        row("FOC", "The carrier's firm order. Your route change is not their database."),
        row("Rollback", "The steps that put the canary back, and who runs them.")
      ]
    },
    {
      slug: "troubleshooting",
      name: "Troubleshooting",
      tips: [
        "Write the falsifier before the fix. If that observation shows up, the hypothesis is dead.",
        "Change one thing. Then call the canary. Then read the counter you named.",
        "A failure path in the player is a hypothesis, not a confession. Prove it on the wire."
      ],
      traps: [
        "Collecting every log and reading none of them.",
        "Restarting a service because the last restart worked once.",
        "Comparing a packet capture in local time with a server log in UTC without saying so."
      ],
      sheet: [
        row("Hypothesis", "One sentence that can be wrong."),
        row("Falsifier", "The observation that kills it."),
        row("Canary", "The call you place after the change."),
        row("Blast radius", "Who else hears the change.")
      ]
    },
    {
      slug: "evidence",
      name: "Evidence habits",
      tips: [
        "Screenshot the filter, not only the result. A future you cannot see the query.",
        "Store the clock source next to the timestamp.",
        "Redact a capture before it leaves the lab. A teaching ladder uses synthetic numbers."
      ],
      traps: [
        "Pasting a production Call-ID into a public note.",
        "Calling a dashboard tile evidence when you cannot reproduce the query.",
        "Keeping a packet capture with real audio payloads in a shared drive."
      ],
      sheet: [
        row("Filter", "The query that produced the row."),
        row("Clock", "Whose time, and the offset."),
        row("Retention", "How long that log actually lives."),
        row("Redaction", "What you removed before sharing.")
      ]
    },
    {
      slug: "design",
      name: "Design notes",
      tips: [
        "Name the failure domain. A design that cannot say what dies together is not finished.",
        "Capacity is the first resource that saturates, in a unit you can measure.",
        "Security includes fraud outbound, not only TLS."
      ],
      traps: [
        "Drawing HA boxes without saying what happens to a call already up.",
        "Copying a port list from memory. Date the vendor document you used.",
        "Hiding recording and emergency on a later slide."
      ],
      sheet: [
        row("Failure domain", "What shares a fate."),
        row("RTO", "How long you claim recovery takes."),
        row("Canary cohort", "Who is in the first wave."),
        row("Fraud control", "Who may dial what, and the alert when they do not.")
      ]
    },
    {
      slug: "practice",
      name: "Practice",
      tips: [
        "Answer before you open the card. The card is the check, not the first reading.",
        "Misses go back into a LICC line: leg, id, counter, capture.",
        "A question bank is paged. Finish the six cards you can see, then ask for the next six."
      ],
      traps: [
        "Recognizing the wording instead of the mechanism.",
        "Skipping the proof line because the letter of the answer matched.",
        "Treating a lab number as a real dial plan you can paste into production."
      ],
      sheet: [
        row("Prompt", "What the question asks, in your words."),
        row("Decision", "The answer you would defend."),
        row("Proof", "The counter or capture that would show you are right."),
        row("Miss", "The card you will teach back tomorrow.")
      ]
    },
    {
      slug: "reference",
      name: "Reference",
      tips: [
        "Open the vendor document that matches the version you run, not the version you remember.",
        "RFC numbers in the campus link to the RFC Editor. Read the section the lesson named.",
        "A glossary expansion is not a design. Put the term back on a call leg."
      ],
      traps: [
        "Citing a forum post over the product guide.",
        "Mixing two release trains in one port list.",
        "Memorizing a default that the deployment overrode."
      ],
      sheet: [
        row("RFC Editor", "The text of the protocol, not a blog summary."),
        row("Series page", "Cisco's index for that product. Pick the release."),
        row("Learn", "Microsoft's Teams Phone and Direct Routing articles."),
        row("Help Center", "Webex Calling administration articles, including the port reference.")
      ]
    }
  ];

  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function find(slug) {
    for (var i = 0; i < TRACKS.length; i += 1) if (TRACKS[i].slug === slug) return TRACKS[i];
    return null;
  }

  function sheet(rows) {
    return '<table class="sheet"><tr><th>Term</th><th>Use it this way</th></tr>' + rows.map(function (pair) {
      return "<tr><td><b>" + esc(pair[0]) + "</b></td><td>" + esc(pair[1]) + "</td></tr>";
    }).join("") + "</table>";
  }

  function list(items) {
    return "<ul>" + items.map(function (item) { return "<li>" + esc(item) + "</li>"; }).join("") + "</ul>";
  }

  function indexHtml() {
    return '<p class="lede">Pro tips, interview traps, and a one-page cheat sheet for each track. The lessons underneath are unchanged.</p><nav class="path-list" aria-label="Tracks">' +
      TRACKS.map(function (track) {
        return '<a href="#/tips/' + track.slug + '"><span>' + esc(track.name) + "</span><small>Sheet</small></a>";
      }).join("") + "</nav>";
  }

  function trackHtml(slug) {
    var track = find(slug);
    if (!track) return "";
    return '<p class="kicker">Tips and tricks</p><p class="lede">' + esc(track.name) + "</p>" +
      '<p><a href="#/tips">All tracks</a></p>' +
      '<div class="card green"><h2>Pro tips</h2>' + list(track.tips) + "</div>" +
      '<div class="card rose"><h2>Interview traps</h2>' + list(track.traps) + "</div>" +
      '<div class="card teal"><h2>Cheat sheet</h2>' + sheet(track.sheet) + "</div>";
  }

  window.UCTips = {
    indexHtml: indexHtml,
    trackHtml: trackHtml,
    known: function (slug) { return !!find(slug); }
  };
})();
