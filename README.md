# 🦊 Fox Treasure Hunt 3D

**A fully interactive 3D treasure-hunting adventure** built with **Python, PyOpenGL, and Pygame** – featuring a lovable cartoon fox, dynamic animations, and real-time **Bluetooth joystick control**.

---

## 🎮 Screenshots

| **Intro Screen**                                                                                                                            | **Back View (Default)**                                                                                                                  | **Front View (Press F)**                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| <img width="1528" height="1098" alt="Intro-screen" src="https://github.com/user-attachments/assets/479c6179-6d8e-4bda-8c0d-7cbc71630eaa" /> | <img width="1521" height="1094" alt="back-View" src="https://github.com/user-attachments/assets/2c900f74-0832-4d40-92b5-0c0ab8fe1081" /> | <img width="1527" height="1084" alt="image" src="https://github.com/user-attachments/assets/06a37e26-a696-4d98-9a2e-20d98e979ee5" /> |

> *The fox celebrates with sparkles and a victory spin when treasure is found!*

---

## ✨ Features

* **Cute 3D Fox with Full Animation**

  * Walking, jumping, waving, dancing
  * **Celebratory Victory Dance** when treasure is found — spinning, bouncing, golden sparkles, tail frenzy
* **Rich OpenGL 3D World**

  * Procedurally generated forest, colorful village, and unique landmarks
  * 6 hidden treasures with glowing treasure indicators
* **Gameplay Loop**

  * Each treasure has poetic hints and a 2-minute timer
  * Win by finding all treasures, lose if time runs out
* **Dual Control Schemes**

  * Bluetooth Joystick (HC-05/HC-06) – auto-detect & connect
  * Keyboard fallback (WASD + Arrows, Space, F, etc.)
* **Camera Toggle**

  * Press `F` to switch between **Front** and **Back View**
* **Polished UI**

  * Timer, score, hints, distance feedback
  * Animated Intro, Win, and Lose screens

---

## 🕹 Controls

| Action            | Keyboard          | Bluetooth Command              |
| ----------------- | ----------------- | ------------------------------ |
| Move Forward      | `↑` / `W`         | `forward`                      |
| Move Backward     | `↓` / `S`         | `backward`                     |
| Strafe Left       | `←` / `A`         | `left`                         |
| Strafe Right      | `→` / `D`         | `right`                        |
| Jump              | `Space`           | `jump`                         |
| Wave              | `W`               | `wave`                         |
| Dance             | `D`               | `dance`                        |
| Rotate Left/Right | `Q` / `E`         | `rotate_left` / `rotate_right` |
| Toggle View       | `F`               | –                              |
| Start / Replay    | `Enter` / `Space` | –                              |

---

## ⚙ Requirements

```txt
Python 3.7+
pygame
PyOpenGL
pyserial
```

---

## 🔧 Bluetooth Connection Example

```
ESC: Quit  
============================================================
Available Serial Ports:
============================================================
  [0] COM5 - Standard Serial over Bluetooth link (COM5)
      ^ Bluetooth device detected!
  [1] COM4 - Standard Serial over Bluetooth link (COM4)
      ^ Bluetooth device detected!
  [2] COM13 - Standard Serial over Bluetooth link (COM13)
      ^ Bluetooth device detected!
  [3] COM14 - Standard Serial over Bluetooth link (COM14)
      ^ Bluetooth device detected!

Connecting to COM14 at 38400 baud... ✓ Bluetooth connection established!
Listening for joystick commands... ✓ Bluetooth joystick control active!
============================================================
Robot window is ready! Move your joystick or use keyboard.
============================================================
```

---

## 🧭 Gameplay Overview

* 6 treasures hidden in a detailed world
* Each treasure has a poetic hint and a 2-minute limit
* Score increases with speed
* Win by collecting all treasures before time runs out

---

## 🛠 Installation

```bash
pip install pygame PyOpenGL pyserial
python main.py
```

If your Bluetooth module (HC-05/HC-06) is paired, the system will auto-detect it at startup.

---

## 🧪 Troubleshooting

* **Device not found:** Ensure your module is paired and visible in Device Manager.
* **Connection failed:** Close other programs using the same COM port.
* **No response:** Check that joystick sends readable commands (`forward`, `left`, etc.).

---

## 🏆 Credits

Built with ❤️ using **Python**, **Pygame**, and **PyOpenGL**.
