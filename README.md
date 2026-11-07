# MoVe Traversensteuerung – Probe Traverse Control

Closed-loop stepper-motor control for positioning a **Prandtl (pitot-static) probe** inside a wind tunnel, so that the flow field in front of a compressor can be measured on a user-defined grid of points.

The project was built for the *MoVe – Moderne Verdichterauslegung* project workshop at the Chair of Aero Engine Design (Fachgebiet Luftfahrtantriebe), TU Berlin. It has two parts:

| Part | Folder | What it does |
|---|---|---|
| **Desktop GUI** | [`GUI/`](GUI) | PyQt5 app: define or generate a polar measurement grid, connect to the board over a serial port, and drive the probe from point to point with encoder feedback |
| **Firmware** | [`Nema_Disc_Board/`](Nema_Disc_Board) | STM32CubeIDE project for the STM32F072B-Discovery board: parses serial commands, generates STEP/DIR pulses for up to four stepper drivers and reads two quadrature encoders |

---

## System overview

```
┌───────────────┐   USB (virtual COM port)   ┌──────────────────────┐   STEP/DIR   ┌──────────────┐
│  PC – PyQt5   │ ─────── commands ────────▶ │  STM32F072 Discovery │ ───────────▶ │ Stepper      │
│  GUI          │ ◀── callbacks / encoder ── │  (firmware)          │              │ drivers      │
└───────────────┘                            │                      │ ◀─ A/B ───── │ NEMA 17 +    │
                                             └──────────────────────┘   encoder    │ encoders     │
                                                                                   └──────────────┘
```

The probe moves in a **polar coordinate system**:

* **Angular axis (φ)** – probe deflection angle in degrees, default range −30° … +30°
* **Radial axis (r)** – probe radius in cm, default range 60 cm … 100 cm

Each axis is driven by a NEMA 17 stepper motor with an integrated encoder. The GUI converts the target positions into step counts, sends them to the microcontroller, then compares the encoder reading with the expected value. If the error exceeds a tolerance, it sends a correcting move (up to two retries per move).

---

## Features

* **Grid editor** – add single points (angle; radius) with spin boxes, or clear all points
* **Grid generator** – create a serpentine (back-and-forth) grid from start, end and step size for both axes, so the probe never has to return to the start of a row
* **Live polar plot** – embedded Matplotlib plot that shows the planned points and the reachable area (dashed red boundary from `settings.yaml`)
* **Closed-loop moves** – encoder-verified positioning with automatic correction moves
* **Command handshake** – the GUI re-sends motor parameters until the board echoes back the expected step count
* **Homing** – returns both axes to the encoder positions stored with *Init Enc*
* **Manual overwrite** – jog any motor by a given number of steps
* **Configuration dialog** – edit every value in `settings.yaml` from the GUI (dimensions, motor mapping, steps per revolution, speeds, dwell time, baud rate)
* **Firmware end-stop detection** – a move stops early if the encoder stops changing while steps are still being sent (axis at a mechanical limit)
* **Stop by interrupt** – any serial data received while a motor is running stops it immediately

---

## Hardware

| Component | Notes |
|---|---|
| STM32F072B-Discovery (STM32F072RBT6) | Connected to the PC through the **USER USB** port (USB CDC virtual COM port) |
| 2 × NEMA 17 closed-loop stepper with magnetic encoder | 1000 PPR / 4000 CPR encoder (angular axis) |
| Stepper drivers with STEP/DIR inputs | One per motor |
| Optional motors 3 and 4 | Pins are set up in firmware but not yet used by the GUI |

### Pin assignment

| Signal | Pin | Used for |
|---|---|---|
| `STEP` / `DIR` (motor 0) | PB6 / PB7 | Angular motor |
| `STEP2` / `DIR2` (motor 1) | PB4 / PB5 | Radial motor |
| `STEP3` / `DIR3` (motor 2) | PC14 / PC13 | Reserved |
| `STEP4` / `DIR4` (motor 3) | PF0 / PC15 | Reserved |
| `TIM3_CH1` / `TIM3_CH2` | PC6 / PC7 | Angular encoder A/B (counter starts at 32 768) |
| `TIM2_CH1` / `TIM2_CH2` | PA5 / PA1 | Radial encoder A/B (counter starts at 500 000) |

> Check the pin table against `Nema_Disc_Board/Nema_Disc_Board.ioc` before wiring if you change the CubeMX configuration.

---

## Getting started

### 1. Flash the firmware

1. Open **STM32CubeIDE** and choose *File → Import → Existing Projects into Workspace*, then select the `Nema_Disc_Board` folder.
2. Build the project (*Project → Build*).
3. Connect the Discovery board through the **ST-LINK** USB port and run *Nema_Disc_Board Debug* (or flash the `.elf`).
4. Connect the **USER USB** port to the PC. The board appears as a virtual COM port (e.g. `COM5` on Windows, `/dev/ttyACM0` on Linux).

### 2. Install the GUI dependencies

Python 3.9 – 3.12 is known to work.

```bash
pip install PyQt5 pyserial pyyaml numpy matplotlib
```

### 3. Run the GUI

The GUI loads `settings.yaml` and writes `output.txt` with relative paths, so **start it from inside the `GUI` folder**:

```bash
cd GUI
python GUI_Master.py
```

---

## Usage

1. **Connect** – select the board's COM port in the *Board* drop-down and click **Connect**.
2. **Init Enc** – click once, with the probe at its reference position, to store the starting encoder values used for homing.
3. **Define the grid**, either
   * point by point: set *angle* and *radius*, then click **Add point**, or
   * automatically: *Generate Gitter* in the menu bar. Enter radial start/end/step and angular start/end/step.
4. Check the points in the polar plot. They must stay inside the dashed red boundary.
5. Click **Perform**. The probe moves to each point in order. After each move it waits `Delay_time` seconds so the measurement can be taken. The progress bar and the *Current pos* / *Next Point* labels show the progress.
6. Click **Home** to return both axes to the positions stored in step 2.

Other menu entries:

* **Manual Overwrite** – move motors by a given number of steps (−1000 … 1000)
* **Configuration** – edit and save `settings.yaml`. The plot and input limits update right away.

### Grid file format

Grids are plain text files, one point per line: angle in degrees, then radius in cm, separated by a space.

```text
-30.000 60.000
-30.000 70.000
-30.000 80.000
```

`GUI/test.txt` and `GUI/test_gitter.txt` are example grids. The GUI saves the current grid to `GUI/output.txt` every time it changes.

---

## Configuration (`GUI/settings.yaml`)

| Section | Key | Meaning |
|---|---|---|
| `dimensions` | `inner_radius`, `outer_radius` | Radial travel limits (cm) |
| | `min_deflection`, `max_deflection` | Angular travel limits (°) |
| `motor_configuration` | `Angular_mot`, `Radial_mot` | Motor index (0–3) used for each axis |
| | `Steps/rot_Angular`, `Steps/rot_Radial` | Driver steps per motor revolution |
| | `Encoder_Steps/rot_Angular`, `Encoder_Steps/rot_Radial` | Encoder counts per revolution |
| `movement_configuration` | `phi_dir` | Steps per degree on the angular axis |
| | `radial_dir` | Steps per cm on the radial axis |
| | `Angular_mot_speed`, `Radial_mot_speed` | Step rate (Hz), converted into the step period sent to the board |
| | `Delay_time` | Dwell time at each point for measuring (s) |
| `serial_configuration` | `baud` | Serial baud rate |
| `gear_ratios` | `x`, `y`, `z` | Placeholder, not used yet |

---

## Serial protocol

Commands are ASCII strings ending with `\r\n`. The firmware is a small state machine (`REST → EDIT → RUN`). A command letter puts it into `EDIT`, and the number that follows is applied when it receives the carriage return.

| Command | Example | Effect |
|---|---|---|
| `p<µs>` | `p10` | Set the step period (half-cycle delay in µs) |
| `s<n>` | `s2000` | Set the number of steps |
| `d<0\|1>` | `d1` | Set the direction |
| `m<0–3>` | `m1` | Select the motor |
| `c` | `c` | Callback: board replies with the signed step count it has stored (handshake) |
| `e` | `e` | Board replies with both encoder counts (angular, then radial), one per line |
| `r` | `r` | Run the move with the stored parameters |

When a move finishes, the board sends `done` and then the encoder count of the motor that moved. Any data received while a motor is running stops the move.

A typical move from the GUI:

```
p10 → s2000 → d1 → m1 → c   (repeat until the callback matches)
r                            (run)
← done
← <encoder count>
e                            (read both encoders, then check the error and correct if needed)
```

---

## Project structure

```
MoVe-Traversensteurung-main/
├── GUI/
│   ├── GUI_Master.py              # Entry point: main window, motion sequence, closed-loop logic
│   ├── Serial_Com_Dummy.py        # pyserial wrapper (port list, open/close, send/receive)
│   ├── Grid.py                    # Grid data structure (loads point files)
│   ├── file_operations.py         # Loads grid .txt files and settings.yaml
│   ├── transformations.py         # Polar → Cartesian helper
│   ├── mplwidget.py               # Matplotlib canvas embedded in Qt (polar plot + boundary)
│   ├── Configuration*.py          # Settings dialog
│   ├── *Generate_Gitter*.py       # Grid generator dialog
│   ├── Manual_Overwrite*.py       # Manual jog dialog
│   ├── py_files/QT_Project.py     # Main window layout (generated from Qt Designer, then edited)
│   ├── ui_files/*.ui              # Qt Designer sources
│   ├── settings.yaml              # Machine configuration
│   └── output.txt, test*.txt      # Current and example grids
└── Nema_Disc_Board/
    ├── Core/Src/main.c            # Command parser, state machine, stepping and end-stop logic
    ├── USB_DEVICE/App/usbd_cdc_if.c  # USB CDC receive callback (also handles stop-by-interrupt)
    ├── Nema_Disc_Board.ioc        # STM32CubeMX configuration
    └── Drivers/, Middlewares/     # ST HAL, CMSIS and USB device library
```

---

## Known limitations

* **Stop** is not yet connected to a handler, and **Perform** runs in the GUI thread, so the window does not respond during a sequence.
* **Load Gitter** (menu) is not finished. To use a saved grid, copy its points into the point list instead.
* `gear_ratios` and motors 3 and 4 appear in the configuration but are not used in the motion logic yet (they are shown in red in the dialogs).
* **Home** needs **Init Enc** to have been pressed earlier in the same session.
* `GUI/generate_gitter.py` is an old prototype that opens its own window. Use the *Generate Gitter* menu entry instead.

## Possible next steps

* Move the motion sequence into a `QThread` so the GUI stays responsive and **Stop** can work
* Add automatic data logging of probe readings at each grid point
* Add Cartesian grids and use the gear-ratio settings for other traverse designs

---

## Authors

* **James Reynaldo** – TU Berlin
* **Matthias Klose** – TU Berlin

Developed in 2024 – 2025 as part of the MoVe project workshop.

## Acknowledgements

* STM32 HAL, CMSIS and USB device library © STMicroelectronics (see the licence files in `Nema_Disc_Board/Drivers` and `Middlewares`)
* Parts of the GUI are adapted from tutorials by pythonguis.com and Stack Overflow answers. The sources are credited in the code comments.
