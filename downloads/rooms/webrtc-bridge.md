# WebRTC, SIP over WebSocket, and a hosted bridge

- Wikipedia describes WebRTC as browser and mobile APIs for real-time audio and video without a plugin.
- The W3C WebRTC recommendation is the browser API. RFC 8825 is the IETF overview of the protocol suite those browsers use.
- RFC 8829, JSEP, lets a JavaScript application control the signaling plane through RTCPeerConnection. It discusses how that relates to existing signaling protocols.
- RFC 7118 carries SIP over a WebSocket so a web application can use SIP as the signaling.
- The FreeSWITCH manual opened here says SignalWire runs that engine as a hosted platform with REST APIs. That is one bridge from open telephony to a cloud API. It is not a catalog of every CPaaS.

A browser does not register to CUCM just because both can carry voice. WebRTC media and SIP dialogs meet at a gateway, a PBX that speaks both, or a service that translates them. ICE, which the Wikipedia article names, is how the browser finds a path. It is not a CUCM partition. JSEP is how the page drives offer and answer. SIP over WebSocket is one way to keep SIP as the signaling instead of inventing a new call model. A communications API that places a call for you is a further hop. This lab opened one statement of that idea, in the FreeSWITCH manual's note on SignalWire. It did not open a vendor matrix, so the matrix stays on a confirm row with no link.

A web page establishes a PeerConnection to a gateway. The gateway sends a SIP INVITE to CUCM. CUCM rings a desk phone. If you capture only on CUCM you will see SIP and miss the browser's ICE candidates. If you capture only in the browser you will not see the CUCM route pattern. Save both sides.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Wikipedia. [WebRTC (Wikipedia)](https://en.wikipedia.org/wiki/WebRTC). last checked 2026-10
- WebRTC. [W3C WebRTC recommendation](https://www.w3.org/TR/webrtc/). last checked 2026-10
- RFC. [RFC 8825, WebRTC protocol overview](https://www.rfc-editor.org/rfc/rfc8825). last checked 2026-10
- RFC. [RFC 8829, JavaScript session establishment](https://www.rfc-editor.org/rfc/rfc8829). last checked 2026-10
- RFC. [RFC 7118, SIP over WebSocket](https://www.rfc-editor.org/rfc/rfc7118). last checked 2026-10
- FreeSWITCH. [FreeSWITCH users manual](https://developer.signalwire.com/freeswitch/). last checked 2026-10
- WebRTC. CPaaS vendor matrix. confirm. No vendor matrix was opened. The FreeSWITCH manual notes one hosted platform. Confirm any other vendor on that vendor's own page. last checked 2026-10

Room or sheet file: ../../rooms/sources/webrtc-bridge/sources.json
