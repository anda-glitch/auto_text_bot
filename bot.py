import subprocess
import time
import json
import os
import sys
import threading

# Thread function to silently consume (and optionally print) node's stdout
# to prevent OS pipe buffer from filling up and hanging the process
def consume_stdout(stdout_pipe, ready_event):
    for line in iter(stdout_pipe.readline, ''):
        if not line:
            break
        # Print everything so the user sees the QR code and any errors
        print(line, end='', flush=True)
        
        # When Node broadcasts it's ready, trigger the event
        if 'READY_SIGNAL_WHATSAPP' in line:
            ready_event.set()

def main():
    print("==========================================")
    print("🐍 WELCOME TO THE PYTHON WHATSAPP BOT 🤖")
    print("==========================================")
    
    print("Do you want to send messages to a Person or a Group?")
    target_type = input("Enter '1' for Person, '2' for Group: ").strip()
    
    if target_type == '1':
        target = input("Enter target phone number with country code (e.g. 14155552671): ").strip()
        if not target.isdigit():
            print("Invalid number. Please only use digits.")
            sys.exit(1)
        action = "send"
        target_label = "number"
    elif target_type == '2':
        target = input("Enter the EXACT name of the WhatsApp Group: ").strip()
        action = "send_group"
        target_label = "group"
    else:
        print("Invalid choice.")
        sys.exit(1)

    print("\nStarting the WhatsApp Bridge in the background...")
    bridge_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa_bridge.js')

    if not os.path.exists(bridge_path):
        print(f"Error: Could not find node script at {bridge_path}")
        sys.exit(1)

    print("\nA QR code will be generated momentarily. Please scan it via WhatsApp 'Linked Devices'.")
    print("Once connected, it will say 'READY_SIGNAL_WHATSAPP'.\n")

    process = subprocess.Popen(
        ['node', bridge_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    ready_event = threading.Event()
    
    # Start background thread to consume stdout
    consumer_thread = threading.Thread(target=consume_stdout, args=(process.stdout, ready_event), daemon=True)
    consumer_thread.start()

    print("Waiting for QR Code...")

    # Wait for the node script to connect to WhatsApp max 5 minutes (user needs time to scan)
    connected = ready_event.wait(timeout=300)
    
    if not connected:
        print("\nTimed out waiting for WhatsApp connection or bridge crashed.")
        process.terminate()
        sys.exit(1)
        
    print("\n✅ WHATSAPP IS CONNECTED! Starting the 1-minute scheduling loop.\n")
    
    message_count = 0
    try:
        while True:
            # Send message payload
            payload = {
                "action": action,
                "target": target,
                "message": "hi"
            }
            json_str = json.dumps(payload)
            
            process.stdin.write(json_str + "\n")
            process.stdin.flush()
            
            message_count += 1
            print(f"[Python] Loop #{message_count}: Sent 'hi' to {target_label} '{target}'.")

            # 1 minute sleep
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n\nBot interrupted by user. Closing WhatsApp bridge...")
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
        print("Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
