import network
import time
import ujson
from machine import Pin
from mfrc522 import MFRC522
from umqtt.simple import MQTTClient

# --- 1. NETWORK SETUP ---
SSID, PASSWORD = "Benax-POP8A", "$emi0pen"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("[DEBUG] Connecting to WiFi", end="")
while not wlan.isconnected():
    print(".", end="")
    time.sleep(0.5)
print("\n[DEBUG] WiFi Connected! IP:", wlan.ifconfig()[0])

# --- 2. CONFIG & TOPICS ---
TEAM_ID = "team_nexus_20266" 
MQTT_BROKER = "157.173.101.159"

TOPIC_TOPUP = "rfid/{}/card/topup".format(TEAM_ID)
TOPIC_STATUS = "rfid/{}/card/status".format(TEAM_ID)

# NEW: Dictionary to store balances in memory (Map where Key = UID, Value = Balance)
card_balances = {}

# Hardware setup (sck, mosi, miso, rst, cs)
print("[DEBUG] Initializing MFRC522 Reader...")
rdr = MFRC522(sck=14, mosi=13, miso=12, rst=4, cs=5)

# --- 3. MQTT CALLBACK ---
def on_message(topic, msg):
    global card_balances
    try:
        data = ujson.loads(msg)
        target_uid = data.get('uid', "").strip().lower()
        amount = int(data.get('amount', 0))
        
        if target_uid:
            # If the card isn't in our memory yet, initialize it
            if target_uid not in card_balances:
                card_balances[target_uid] = 0
                
            # Add top-up amount to the in-memory balance
            card_balances[target_uid] += amount
            
            print("\n[DEBUG] In-Memory Top-up Processed:")
            print("        UID:", target_uid)
            print("        New Balance:", card_balances[target_uid])
    except Exception as e:
        print("[DEBUG] MQTT Parse Error:", e)

print("[DEBUG] Connecting to MQTT Broker: {}".format(MQTT_BROKER))
client = MQTTClient(TEAM_ID, MQTT_BROKER)
client.set_callback(on_message)
client.connect()
client.subscribe(TOPIC_TOPUP)
print("[DEBUG] Subscribed to:", TOPIC_TOPUP)

print("\n--- SYSTEM LIVE: Place card on reader ---")

# --- 4. MAIN LOOP ---
while True:
    try:
        client.check_msg()
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            if stat == rdr.OK:
                # Format UID and make it lowercase to ensure it matches MQTT payloads perfectly
                current_uid_str = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                current_uid_str = current_uid_str.lower()
                
                print("\n[DEBUG] Card Detected:", current_uid_str)
                
                # Check if card exists in our memory map; if not, set balance to 0
                if current_uid_str not in card_balances:
                    card_balances[current_uid_str] = 0
                    print("[DEBUG] New card registered in memory with balance 0")
                
                # Retrieve the balance from memory
                current_balance = card_balances[current_uid_str]
                print("[DEBUG] Current In-Memory Balance:", current_balance)
                
                # SEND STATUS to Dashboard
                payload = ujson.dumps({"uid": current_uid_str, "balance": current_balance, "team": TEAM_ID})
                client.publish(TOPIC_STATUS, payload)
                print("[DEBUG] Sent UID & Status to Dashboard.")
                
                # WAIT FOR REMOVAL (Prevents polling spam)
                print("[DEBUG] Please remove card...")
                while True:
                    (stat, _) = rdr.request(rdr.REQIDL)
                    if stat != rdr.OK:
                        break
                    time.sleep(0.1)
                print("[DEBUG] Card removed. Ready for next scan.")
                
    except Exception as e:
        print("\n[DEBUG] Global Loop Error:", e)
        time.sleep(1)
    
    time.sleep(0.1)