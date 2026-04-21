<h1 align=center> 

Astrid 
<img width=32 height=32 style="vertical-align:middle" src="docs/astrid_pixelart.png"></img>
</h1>
<p align=center><i>Source Code to impROVise's ROV, Astrid</i>
<br><br><br>
<img height=50 style="vertical-align:middle" src="docs/improvise.png"></img>

---

## Usage
> [!IMPORTANT]
> We use a Raspberry Pi 4 for both the the Poolside and the ROV.

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
python main.py --poolside --target-ip <TARGET_IP = 127.0.0.1> --target-port <PORT = 8081> --port <PORT = 8080>
```

```
python main.py --rov --target-ip <TARGET_IP = 127.0.0.1> --target-port <TARGET_PORT = 8080> --port <PORT = 8081> [OPTIONAL: --simulated] 
```

> [!IMPORTANT]
> `target-ip` on either end is the IP which data will be sent to. In other words, use the poolside ip for `rov`, and the ROV ip for `poolside`.
> `target-port` is the port in which to send to, on `target-ip`.
> `port` is the port on which to listen on, on this device.

> [!TIP]
> - Use `--poolside` for the code that runs on the computer on the poolside.
> - Use `--rov` for the code that runs on the ROV.
> - Use `--simulated` on the rov to test the software without the actual hardware attached.

---

# Hardware
We use a Raspberry Pi 4 onboard our ROV for flight control. This Pi 4 is connected to a I2C PCA9685 board to control our motors and servos. The addresses for this board are defined in [consts.py](src/consts.py), as well as some other physical quantities such as motor throttles and servo angles. We use Ethernet cable for our tether, and the poolside computer is a Raspberry Pi 4.


---
# Licensing
We use an MIT License. (Please see [LICENSE](LICENSE) text!) Please feel free to use this code to learn!


---
<footer align=center> 
    <i>made in scotland with love</i>
    <br>
    <img height=20 style="vertical-align:middle" src="docs/scotland.png"></img>
</footer>