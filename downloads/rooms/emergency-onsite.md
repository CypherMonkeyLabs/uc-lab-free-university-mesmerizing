# On-site alert, callback, and what this lab will not decide

- The Release 15 administration guide contents include on-site alerts, off-premises users, and a national E911 service provider. Those are different chapters.
- PSAP callback is a call into your network on the ELIN. The CUCM chapter says translation patterns exist so Emergency Responder can intercept that call.
- A successful outbound 911 test does not prove the callback path.
- Wikipedia's Enhanced 911 article separates the caller's number (ANI) from the location database (ALI) on the traditional landline path. An ELIN is how many enterprise designs present a callback number.
- Laws, carriers, and remote-worker designs outside the pages opened here stay on a confirm row.

Treat notification, location, and callback as three tests. Kari's Law notification, on the FCC page, is a message to people at the site. The ELIN callback is a call from the PSAP. On-site alert in Emergency Responder is the product feature listed in the Release 15 guide. They can all be present and still describe different audiences. Off-premises users and a national service provider are named in that guide's contents. This lab does not restate their limits. Dedicated Instance, Webex Calling, and a branch SRST phone are different places for the same human emergency. Test the path the phone will actually use.

You place a test call in a window the carrier agreed to. The PSAP, or your test desk, sees an ELIN. You then call that ELIN back. If the call rings a hunt pilot instead of the phone that placed the test, the translation pattern or the Emergency Responder mapping is the next object, not the codec.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Cisco. [Cisco Emergency Responder Administration Guide, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cer/15/english/administration/guide/cer0_b_cisco-emergency-responder-administration-guide-15.html). last checked 2026-10
- Cisco. [Configure Cisco Unified Communications Manager, Emergency Responder 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cer/15/english/administration/guide/cer0_b_cisco-emergency-responder-administration-guide-15/cer0_b_cisco-emergency-responder-administration-guide-1401_chapter_011.html). last checked 2026-10
- FCC. [FCC, Kari's Law and RAY BAUM'S Act for multi-line telephone systems](https://www.fcc.gov/mlts-911-requirements). last checked 2026-10
- Wikipedia. [Enhanced 911 (Wikipedia)](https://en.wikipedia.org/wiki/Enhanced_9-1-1). last checked 2026-10
- Law. Emergency-calling rule outside the FCC MLTS page. confirm. No statute outside that FCC page was opened. Confirm the rule where the site operates. last checked 2026-10

Room or sheet file: ../../rooms/sources/emergency-onsite/sources.json
