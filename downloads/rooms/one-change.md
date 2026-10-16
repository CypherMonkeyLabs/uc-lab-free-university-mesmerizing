# One hypothesis, one change

- Say what you think is broken, in one sentence.
- Change one thing.
- Capture before and after.
- If the symptom does not move, revert.
- A bundle of changes is not a lesson.

Voice tickets get worse when five settings change before the first ladder is saved. The evidence pack is the hypothesis, the time, the calling and called numbers, the SIP ladder or the CUCM trace, and the result. Store it next to the change.

Hypothesis: the trunk CSS cannot see the PSTN partition. Change: add that partition. Result: the same call now leaves CUCM and fails further downstream. You learned something. You did not also restart the cluster.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Cisco. [System Configuration Guide for CUCM, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html). last checked 2026-10
- RFC. [RFC 3261, SIP](https://www.rfc-editor.org/rfc/rfc3261). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Session Initiation Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Session_Initiation_Protocol). last checked 2026-10
- Protocol and ports. [CUCM 15 TCP and UDP port usage](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html). last checked 2026-10

Room or sheet file: ../../assets/data/sources/one-change.json
