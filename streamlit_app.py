import streamlit as st

# Impress.js CDN (use the latest version or host your own)
impress_js_cdn = "https://cdn.jsdelivr.net/npm/impress.js@1.1.0/js/impress.min.js"

impress_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>impress.js Dynamic Example with Cool Transitions</title>
  <meta name="viewport" content="width=1024" />
  <style>
    body { background: #181d28; color: #fff; font-family: 'Segoe UI', Arial, sans-serif; }
    .step {
      border-radius: 16px;
      box-shadow: 0 0 30px #22336699;
      padding: 60px;
      transition: box-shadow 0.5s cubic-bezier(.18,.89,.32,1.28);
    }
    .dynamic { color: #ff0; font-weight: bold; }
    #dynamic-content {
      font-size: 2em;
      margin-top: 20px;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0% { text-shadow: 0 0 5px #fff700, 0 0 10px #fff700; }
      50% { text-shadow: 0 0 40px #fff700, 0 0 80px #fff700; }
      100% { text-shadow: 0 0 5px #fff700, 0 0 10px #fff700; }
    }
    a { color: #80f8ff; }
  </style>
  <link href="https://cdn.jsdelivr.net/npm/impress.js@1.1.0/css/impress-demo.css" rel="stylesheet" />
</head>
<body>
<div id="impress">
  <div id="title" class="step" data-x="0" data-y="0" data-scale="1" data-rotate-z="0">
    <h1>Welcome to <span class="dynamic">impress.js</span>!</h1>
    <p>Use arrow keys or spacebar to navigate.<br>
      <small>Enjoy the wild transitions!</small>
    </p>
  </div>
  <div class="step" data-x="1500" data-y="0" data-z="1000" data-rotate-x="90" data-rotate-y="30" data-scale="2.5">
    <h2>Dynamic Content Demo</h2>
    <div id="dynamic-content">Loading dynamic data...</div>
  </div>
  <div class="step" data-x="0" data-y="2000" data-z="3000" data-rotate-y="180" data-rotate-x="60" data-scale="3.5">
    <h2>3D Step</h2>
    <p>This slide floats, flips, and zooms in 3D space!</p>
  </div>
  <div class="step" data-x="-1500" data-y="0" data-z="-1200" data-rotate-z="270" data-rotate-x="45" data-scale="2">
    <h2>Edge Browser Compatible</h2>
    <p>Tested and works in Microsoft Edge, Chrome, Firefox, Safari.</p>
    <p><span style="font-size:2em;">🎉</span></p>
  </div>
  <div class="step" data-x="0" data-y="-2000" data-z="0" data-rotate-y="360" data-scale="1">
    <h2>Thank You!</h2>
    <p>impress.js is <a href="https://impress.js.org/" target="_blank">open source</a>.<br>
    <span style="font-size:1.4em;">Happy presenting!</span></p>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/impress.js@1.1.0/js/impress.min.js"></script>
<script>
impress().init();

// Example of dynamic content (fetching random joke from API)
fetch('https://api.chucknorris.io/jokes/random')
  .then(response => response.json())
  .then(data => {
    document.getElementById('dynamic-content').innerText = data.value;
  })
  .catch(() => {
    document.getElementById('dynamic-content').innerText = "Couldn't load joke 😅";
  });
</script>
</body>
</html>
"""

# Render in Streamlit
st.components.v1.html(impress_html, height=800, scrolling=True)
