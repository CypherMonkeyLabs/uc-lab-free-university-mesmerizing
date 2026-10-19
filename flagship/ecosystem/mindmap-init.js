
(function () {
  var data = {"content": "UC Lab", "children": [{"content": "Signaling", "children": [{"content": "REGISTER", "children": []}, {"content": "INVITE", "children": []}, {"content": "SDP", "children": []}]}, {"content": "Edge", "children": [{"content": "CUBE", "children": []}, {"content": "MRA", "children": []}, {"content": "SRTP", "children": []}]}, {"content": "Cloud", "children": [{"content": "Webex Calling", "children": []}, {"content": "Teams Phone", "children": []}]}, {"content": "Around the agent", "children": [{"content": "WFM", "children": []}, {"content": "Recording", "children": []}, {"content": "CRM", "children": []}]}]};
  var root = (document.body && document.body.getAttribute('data-root')) || '';
  function load(src) {
    return new Promise(function (resolve, reject) {
      var script = document.createElement('script');
      script.src = src;
      script.onload = resolve;
      script.onerror = reject;
      document.body.appendChild(script);
    });
  }
  function start() {
    var host = document.querySelector('#mind');
    if (!host) return;
    var run = function () {
      load(root + 'assets/vendor/d3.min.js').then(function () {
        return load(root + 'assets/vendor/markmap-view.js');
      }).then(function () {
        if (window.markmap) markmap.Markmap.create('#mind', {}, data);
      }).catch(function () {});
    };
    if ('IntersectionObserver' in window) {
      var watch = new IntersectionObserver(function (entries) {
        if (!entries.some(function (entry) { return entry.isIntersecting; })) return;
        watch.disconnect();
        run();
      }, { rootMargin: '120px' });
      watch.observe(host);
    } else run();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
