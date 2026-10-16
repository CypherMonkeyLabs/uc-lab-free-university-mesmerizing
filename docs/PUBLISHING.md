# Publishing

The site is a static folder. `index.html` is the front door. `sw.js` and `manifest.webmanifest` make it installable as a PWA when it is served over http. `scripts/gzip-static.mjs` is the local gzip server used for checks.

Prepared, not built:

- A Chrome extension would wrap this folder as an unpacked extension with a popup that opens `index.html`. No manifest for the Chrome Web Store is in this repository.
- A Capacitor iOS or Android shell would point `webDir` at this folder. No Xcode or Gradle project is generated here.
- An embed widget would be an iframe of `index.html` on a page that allows it. No hosted widget script is deployed.

GitHub Pages can publish the repository root. Do not merge that change from this branch until someone reviews it.
