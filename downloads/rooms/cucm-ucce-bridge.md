# The CUCM bridge into UCCE

- Agents are CUCM endpoints.
- The peripheral gateway watches those endpoints.
- A label must be a number CUCM can route.
- CTI controls the desktop. The SIP call is still a call.
- Device targets and extensions drift apart when people rename lines.

The bridge fails in ordinary ways: the script returns a label that is not a directory number, the phone is in a partition the CTI route point cannot reach, or the agent is not associated with the application user. None of those are a mystery queue.

ICM returns label 4501. CUCM has 4501 in a partition the trunk CSS cannot see. The call dies after a successful script. Fix the CSS or the label, and say which one you changed.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Cisco. [Cisco Unified Contact Center Enterprise product support](https://www.cisco.com/c/en/us/support/customer-collaboration/unified-contact-center-enterprise/series.html). last checked 2026-10
- Cisco. [System Configuration Guide for CUCM, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html). last checked 2026-10
- Protocol and ports. [CUCM 15 TCP and UDP port usage](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Voice over IP (Wikipedia)](https://en.wikipedia.org/wiki/Voice_over_IP). last checked 2026-10

Room or sheet file: ../../rooms/sources/cucm-ucce-bridge/sources.json
