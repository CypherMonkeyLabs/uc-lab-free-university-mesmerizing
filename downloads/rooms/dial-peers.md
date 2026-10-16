# Dial peers

- A dial peer matches an incoming or outgoing call.
- Inbound SIP matching checks URI headers before called number on current Cisco IOS guidance.
- Outbound hunt prefers the longest match, then preference.
- Preference is not the same as a CUCM route list.
- A peer with no session target does not send a call.

Engineers memorize one match order and apply it to every release. Cisco's SIP matching article is the source for the release you run. The teaching order used here is URI, then called number, then calling number for inbound SIP, and longest match then preference for outbound. Confirm that article before you change a production peer.

Two outbound peers match the same number. Preference 1 points at a dead carrier. The call waits on that peer until the timeout, then tries preference 2. Users call it slow dial tone to the PSTN.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Cisco. [Understand IOS and IOS XE call routing](https://www.cisco.com/c/en/us/support/docs/voice/ip-telephony-voice-over-ip-voip/211306-In-Depth-Explanation-of-Cisco-IOS-and-IO.html). last checked 2026-10
- Cisco. [CUBE configuration guide, dial peers (IOS XE 17.6 onwards)](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/voice/cube/ios-xe/config/ios-xe-book/m_cube-dp.html). last checked 2026-10
- RFC. [RFC 4733, RTP telephony events](https://www.rfc-editor.org/rfc/rfc4733). last checked 2026-10
- Cisco. [Cisco Unified Border Element product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-border-element/series.html). last checked 2026-10
- Protocol and ports. [IANA SIP parameters](https://www.iana.org/assignments/sip-parameters/sip-parameters.xhtml). last checked 2026-10
- Protocol and ports. [IANA service names and port numbers](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Session Initiation Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Session_Initiation_Protocol). last checked 2026-10
- Wikipedia. [Voice over IP (Wikipedia)](https://en.wikipedia.org/wiki/Voice_over_IP). last checked 2026-10
- Wikipedia. English Wikipedia article for Cisco Unified Border Element. confirm. That title returned HTTP 404. last checked 2026-10

Room or sheet file: ../../rooms/sources/dial-peers/sources.json
