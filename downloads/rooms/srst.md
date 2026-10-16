# SRST

- SRST is the fallback when phones cannot reach CUCM.
- The router becomes a small call agent for the phones that fail over.
- Dial plan on SRST is a subset you configured, not the full CUCM CSS.
- Fallback is a registration event.
- When CUCM returns, phones re-home. Confirm the timers.

Survivable Remote Site Telephony keeps a branch placing and receiving a planned set of calls during a WAN failure. It is not an automatic copy of every CUCM feature. Hunt pilots, pickup, and presence may not exist in fallback. Test the fallback dial plan on purpose.

WAN down. Phones show a fallback mode and register to the branch router. 911 and local PSTN still match the SRST dial peers. An internal abbreviation that lived only in CUCM fails. That failure is expected if you never built it on SRST.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Cisco. [Cisco Unified SRST product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-survivable-remote-site-telephony/series.html). last checked 2026-10
- Cisco. [Cisco Unified Communications Manager product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html). last checked 2026-10
- Cisco. [System Configuration Guide for CUCM, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html). last checked 2026-10
- Protocol and ports. [CUCM 15 TCP and UDP port usage](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Voice over IP (Wikipedia)](https://en.wikipedia.org/wiki/Voice_over_IP). last checked 2026-10
- Wikipedia. English Wikipedia article for Survivable Remote Site Telephony. confirm. That title returned HTTP 404. last checked 2026-10

Room or sheet file: ../../rooms/sources/srst/sources.json
