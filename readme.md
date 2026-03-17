# Nexus RFID: IoT POS & Management

An **RFID-based POS and Recharge system** using ESP8266, Flask, and a "Live" glassmorphism dashboard. This system stores balances directly on **Mifare Sector 8**, ensuring data portability and real-time security.

## Live Demo
[Access System Here](http://157.173.101.159:9227/)

## System Architecture

### 1. ESP8266 (Edge Controller)
* **Physical Storage:** Reads/Writes 4-byte integer balances directly to the card.
* **Edge Logic:** Uses bit-shifting for high-value balances (up to 4.2B RWF).
* **MQTT:** Handles asynchronous status updates and physical write commands.

### 2. Backend (Flask & SQLite)
* **Persistence:** Logs every transaction in `nexus_pos.db` (SQLite).
* **Bridge:** Synchronizes MQTT hardware data with browsers via WebSockets.
* **API:** Manages checkout deductions and admin refills via HTTP POST.

### 3. Web Dashboard
* **Dual-Mode:** Vibrant Storefront for shopping and a secure Admin Panel.
* **Real-time Checkout:** Triggers a "Waiting for Tap" state for card deductions.
* **Live Feed:** Stream of all card interactions and system diagnostics.

## Communication Flow
* **ESP8266 ↔ MQTT:** Card status and physical write operations.
* **Browser ↔ Flask:** WebSocket (Socket.IO) for live tap and result events.
* **Browser ↔ Flask:** HTTP POST for cart checkouts and administrative refills.
* **Flask ↔ MQTT:** Dispatches balance adjustment commands to hardware.

The new link for PWA
https://monotypic-unfiltrated-teofila.ngrok-free.dev/