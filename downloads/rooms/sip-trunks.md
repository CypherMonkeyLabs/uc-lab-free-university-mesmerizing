# SIP trunks on CUCM

- The trunk, the SIP profile, and the security profile are three objects.
- OPTIONS can mark a trunk out of service.
- Early offer is a setting, not a guess.
- Run on all nodes is a choice with consequences.
- A trunk in service can still route nowhere if the CSS is empty.

CUCM sends OPTIONS when the profile says so. A trunk that looks down may be a failed OPTIONS to an address that does not answer, while calls would have worked, or the reverse. Read the destination address and the profile together.

A new CUBE peer answers calls but CUCM marks the trunk down. The OPTIONS ping target is a different IP than the INVITE target. Fix the target you actually configured, then retest.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- RFC. [RFC 3261, SIP](https://www.rfc-editor.org/rfc/rfc3261). last checked 2026-10
- RFC. [RFC 4028, SIP session timers](https://www.rfc-editor.org/rfc/rfc4028). last checked 2026-10
- Cisco. [Cisco Unified Communications Manager product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html). last checked 2026-10
- Cisco. [System Configuration Guide for CUCM, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html). last checked 2026-10
- Protocol and ports. [CUCM 15 TCP and UDP port usage](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html). last checked 2026-10
- Protocol and ports. [IANA SIP parameters](https://www.iana.org/assignments/sip-parameters/sip-parameters.xhtml). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Session Initiation Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Session_Initiation_Protocol). last checked 2026-10
- Cisco. Collaboration 12 SRND book. confirm. The historical Collaboration 12 SRND path opened as a product listing, not the design book. Use the Preferred Architecture index, which was opened. last checked 2026-10

Room or sheet file: ../../assets/data/sources/sip-trunks.json
