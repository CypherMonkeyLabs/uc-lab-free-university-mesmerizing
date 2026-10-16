# Route patterns, lists, and groups

- A route pattern matches digits.
- A route list holds route groups in order.
- A route group holds gateways or trunks.
- Distribution inside the group is its own setting.
- A pattern pointed at a gateway skips the list.

When the PSTN call fails over, you are usually looking at the route list order and whether the first member sent a release cause that CUCM is willing to hunt on. Not every failure hunts.

Pattern 9.! sends national calls to a route list. Group 1 is the primary SIP trunk. Group 2 is the backup. A 503 from the first trunk can hunt. A fast busy from a downstream reason may not. Read the cause.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Cisco. [Cisco Unified Communications Manager product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html). last checked 2026-10
- Cisco. [System Configuration Guide for CUCM, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html). last checked 2026-10
- Cisco. [Cisco Collaboration Preferred Architectures](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/uc_system/design/guides/PAdocs.html). last checked 2026-10
- Cisco. [Preferred Architecture for Cisco Collaboration 15, design overview (PDF)](https://www.cisco.com/c/dam/en/us/td/docs/solutions/PA/overview/15x/clbpa15x.pdf). last checked 2026-10
- Protocol and ports. [CUCM 15 TCP and UDP port usage](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html). last checked 2026-10
- Protocol and ports. [IANA SIP parameters](https://www.iana.org/assignments/sip-parameters/sip-parameters.xhtml). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Voice over IP (Wikipedia)](https://en.wikipedia.org/wiki/Voice_over_IP). last checked 2026-10
- Wikipedia. [CUCM (Wikipedia disambiguation)](https://en.wikipedia.org/wiki/CUCM). last checked 2026-10
- Cisco. Collaboration 12 SRND book. confirm. The historical Collaboration 12 SRND path opened as a product listing, not the design book. Use the Preferred Architecture index, which was opened. last checked 2026-10
- Wikipedia. English Wikipedia article for Cisco Unified Communications Manager. confirm. That title returned HTTP 404. The CUCM disambiguation page is the Wikipedia page that opened. last checked 2026-10

Room or sheet file: ../../rooms/sources/route-patterns/sources.json
