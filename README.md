<h1 align=center> Astrid <img width=32 height=32 style="vertical-align:middle" src="docs/astrid_pixelart.png"></img> </h1>
<p align=center><i>Source Code to impROVise's ROV, Astrid</i>

---

## Usage
> [!IMPORTANT]
> We use a Raspberry Pi 4 for both the the client and the server. From our testing, this will not run on Windows. (Tested on Windows 11)

Create a Python Virtual Environment:
```
python -m venv .venv
```

Activate the virtual environment:
```
source .venv/bin/activate
```

Install dependencies to virtual environment:
```
python -m pip install -r requirements.txt
```

### Running:
```
python main.py --client --ip <IP = 127.0.0.1> --port <PORT = 8080>
```

```
python main.py --server --ip <IP = 127.0.0.1> --port <PORT = 8080> [OPTIONAL: --simulated]
```

> [!TIP]
> - Use `--client` for the code that runs on the computer on the poolside.
> - Use `--server` for the code that runs on the ROV.
> - Use `--simulated` on the server to test the software without the actual hardware attached.

---

# Hardware
We use a Raspberry Pi 4 onboard our ROV for flight control. The Hardware I2C Addresses are defined in [consts.py](src/consts.py), as well as some other physical quantities such as motor throttles and servo angles. We use a ethernet cable along our tether for digital communications. The poolside client computer is also a Raspberry Pi.


---
# To-Do List
_A certified impROVise classic activity_

## Common
- [x] Create Netcode Framework
    - [x] Error Handling (yay...)
    - [x] S2C Camera Stream Protocol
    - [x] C2S Control Protocol

## Client (Poolside)
- [x] Create Window Manager
    - [x] Maintain Aspect Ratio
- [x] Create Gamepad Manager

## Server (ROV)
- [x] Write Camera Handler
- [x] Write Hardware Handler
    - [x] Actually handle key inputs

---
# Licensing
We use an MIT License. (Please see [LICENSE](LICENSE) text!) Please feel free to use this code to learn!