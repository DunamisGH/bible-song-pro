# Bible Song Pro LAN display setup

This project includes a lightweight LAN relay so the control panel and display can sync across devices on the same network.

## Run it

Windows:

```bat
py -3 lan_server.py
```

To start the server and configure Tailscale Funnel for internet access, run:

```bat
start_funnel.bat
```

This exposes the web page on Funnel HTTPS port `443` and the WebSocket relay on
port `10000`. In Bible Song Pro's Remote Show settings, use port `443` and relay
port `10000`. The Funnel routes are configured in Tailscale background mode;
stopping this launcher stops the local app server, but leaves the routes configured.
Turn those routes off with `tailscale funnel --https=443 off` and
`tailscale funnel --https=10000 off`.

or:

```bat
py -3 lan_server.py --host 0.0.0.0 --http-port 8000 --relay-port 5511
```

Then open the control panel and display pages on the same machine or another device on the LAN:

- Control panel: http://<your-lan-ip>:8000/Bible%20Song%20Pro%20panel.html
- Display: http://<your-lan-ip>:8000/BSP_display.html

The display page will automatically try to connect to the same host over WebSocket:

- ws://<your-lan-ip>:5511

## Notes

- The relay is intentionally minimal and designed for local network use.
- If you load the display using `localhost`, it will default to `127.0.0.1`, which only works on the same machine.
- To use another device on the LAN, open the page via the server's LAN IP address.
