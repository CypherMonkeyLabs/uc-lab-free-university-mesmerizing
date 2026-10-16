# Survivability during cutover

- Cloud calling needs a plan for when the cloud path is down.
- A survivability gateway is a Webex Calling feature. Confirm it is on your subscription.
- SRST is the CUCM-era feature. It does not automatically cover Webex apps.
- Emergency calling must be tested on the fallback path.
- Write who can call whom when the WAN is down.

Cutover weekend is the worst time to discover that branch phones have no local PSTN. If the design uses a survivability gateway, test it before you move the numbers. If the design is CUCM with SRST, test SRST. Do not assume one covers the other.

After the site moves to Calling, you pull the WAN. The survivability gateway registers the phones it is responsible for and places a local emergency call. If that call fails, the site is not ready, even if the happy-path cloud call worked.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Webex. [Get started with Webex Calling](https://help.webex.com/en-us/article/8jda92/Webex-Calling). last checked 2026-10
- Webex. [Webex Help Center](https://help.webex.com/). last checked 2026-10
- Webex. [Get started with Local Gateway](https://help.webex.com/en-us/article/t9xctu/Get-started-with-Local-Gateway). last checked 2026-10
- Webex. [Configure Local Gateway on Cisco IOS XE for Webex Calling](https://help.webex.com/en-us/article/jr1i3r/Configure-local-gateway-on-IOS-XE-for-Webex-Calling). last checked 2026-10
- Protocol and ports. [Port reference for Webex Calling](https://help.webex.com/en-us/article/b2exve/Port-Reference-Information-for-Cisco-Webex-Calling). last checked 2026-10
- Cisco. [Cisco Unified Communications Manager product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html). last checked 2026-10
- Cisco. [System Configuration Guide for CUCM, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Voice over IP (Wikipedia)](https://en.wikipedia.org/wiki/Voice_over_IP). last checked 2026-10
- Webex. Webex Calling survivability gateway guide. confirm. A survivability-gateway article was not opened, so this row has no link. The local-gateway guide that did open is listed above. last checked 2026-10
- Cisco. [Cisco Unified SRST product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-survivable-remote-site-telephony/series.html). last checked 2026-10

Room or sheet file: ../../rooms/sources/cutover-survivability/sources.json
