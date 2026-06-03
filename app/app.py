from flask import Flask, jsonify, request, render_template_string
import subprocess

app = Flask(__name__)

# -------------------------
# Helper function
# -------------------------
def run(cmd):
    return subprocess.getoutput(cmd)

# -------------------------
# UI PAGE
# -------------------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Orange Pi WiFi Manager</title>
<style>
body {
    font-family: Arial;
    background: #0f172a;
    color: white;
    margin: 0;
    padding: 20px;
}
.container { max-width: 900px; margin: auto; }

.card {
    background: #1e293b;
    padding: 15px;
    margin: 10px 0;
    border-radius: 10px;
}

button {
    padding: 8px 12px;
    margin: 5px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

input {
    padding: 8px;
    margin: 5px;
    border-radius: 6px;
    border: none;
}

.green { background: #22c55e; color: white; }
.red { background: #ef4444; color: white; }
.blue { background: #3b82f6; color: white; }

pre { background: #0b1220; padding: 10px; border-radius: 8px; }
</style>
</head>
<body>
<div class="container">

<h1>📶 Orange Pi WiFi Manager</h1>

<div class="card">
<h2>Devices</h2>
<button onclick="loadDevices()">Refresh</button>
<pre id="devices"></pre>
</div>

<div class="card">
<h2>WiFi Networks</h2>
<button onclick="loadNetworks()">Scan</button>
<pre id="networks"></pre>
</div>

<div class="card">
<h2>Connect WiFi</h2>
<input id="ssid" placeholder="SSID">
<input id="pass" placeholder="Password">
<input id="iface" placeholder="Device (e.g. wlan0)">
<button class="green" onclick="connectWifi()">Connect</button>
</div>

<div class="card">
<h2>Disconnect WiFi</h2>
<input id="diface" placeholder="Device">
<button class="red" onclick="disconnectWifi()">Disconnect</button>
</div>

<div class="card">
<h2>Hotspot</h2>
<input id="hiface" placeholder="Device (e.g. wlan1)">
<input id="hsid" placeholder="Hotspot Name">
<input id="hpass" placeholder="Password">
<button class="blue" onclick="startHotspot()">Enable</button>
<button class="red" onclick="stopHotspot()">Disable</button>
</div>

<div class="card">
<h2>Hotspot Clients</h2>
<input id="ciface" placeholder="Hotspot interface (e.g. wlan1)">
<button onclick="loadClients()">Show Clients</button>
<pre id="clients"></pre>
</div>

</div>

<script>

async function loadDevices() {
    let r = await fetch('/devices');
    document.getElementById('devices').innerText = await r.text();
}

async function loadNetworks() {
    let r = await fetch('/networks');
    document.getElementById('networks').innerText = await r.text();
}

async function connectWifi() {
    let ssid = document.getElementById('ssid').value;
    let pass = document.getElementById('pass').value;
    let iface = document.getElementById('iface').value;

    await fetch(`/connect?ssid=${ssid}&pass=${pass}&iface=${iface}`);
    alert("Connecting...");
}

async function disconnectWifi() {
    let iface = document.getElementById('diface').value;
    await fetch(`/disconnect?iface=${iface}`);
    alert("Disconnected");
}

async function startHotspot() {
    let iface = document.getElementById('hiface').value;
    let ssid = document.getElementById('hsid').value;
    let pass = document.getElementById('hpass').value;

    await fetch(`/hotspot/start?iface=${iface}&ssid=${ssid}&pass=${pass}`);
    alert("Hotspot started");
}

async function stopHotspot() {
    await fetch(`/hotspot/stop`);
    alert("Hotspot stopped");
}

async function loadClients() {
    let iface = document.getElementById('ciface').value;
    let r = await fetch(`/hotspot/clients?iface=${iface}`);
    document.getElementById('clients').innerText = await r.text();
}

</script>

</body>
</html>
"""

# -------------------------
# ROUTES
# -------------------------

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/devices")
def devices():
    return run("nmcli device status")

@app.route("/networks")
def networks():
    return run("nmcli device wifi list")

@app.route("/connect")
def connect():
    ssid = request.args.get("ssid")
    password = request.args.get("pass")
    iface = request.args.get("iface")
    return run(f'nmcli device wifi connect "{ssid}" password "{password}" ifname {iface}')

@app.route("/disconnect")
def disconnect():
    iface = request.args.get("iface")
    return run(f"nmcli device disconnect {iface}")

@app.route("/hotspot/start")
def hotspot_start():
    iface = request.args.get("iface")
    ssid = request.args.get("ssid")
    password = request.args.get("pass")
    return run(f'nmcli device wifi hotspot ifname {iface} ssid "{ssid}" password "{password}"')

@app.route("/hotspot/stop")
def hotspot_stop():
    return run("nmcli connection down Hotspot")

@app.route("/hotspot/clients")
def hotspot_clients():
    iface = request.args.get("iface")
    # shows connected clients for AP mode
    return run(f"iw dev {iface} station dump")

# -------------------------
# RUN SERVER
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)