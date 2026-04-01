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
            
        # Detect group listing data
        if line.startswith('LIST_GROUPS_DATA:'):
            try:
                data_str = line.split('LIST_GROUPS_DATA:')[1].strip()
                groups = json.loads(data_str)
                print("\n" + "="*60)
                print(f"{'GROUP NAME':<30} | {'GROUP ID (Copy this!)'}")
                print("-" * 60)
                for g in groups:
                    name = g['name'] or "Unknown Name"
                    gid = g['id']
                    # Truncate long names for the table
                    display_name = (name[:27] + '..') if len(name) > 27 else name
                    print(f"{display_name:<30} | {gid}")
                print("="*60 + "\n")
            except Exception as e:
                print(f"\n[Error] Failed to parse group list: {e}\n")
            continue

        # Print all other stdout (QR codes, ready signals, etc)
        print(line, end='', flush=True)
        
        # When Node broadcasts it's ready, trigger the event
        if 'READY_SIGNAL_WHATSAPP' in line:
            ready_event.set()

def main():
    print("==========================================")
    print("🐍 WELCOME TO THE PYTHON WHATSAPP BOT 🤖")
    print("==========================================")
    
    bridge_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa_bridge.js')

    if not os.path.exists(bridge_path):
        print(f"Error: Could not find node script at {bridge_path}")
        sys.exit(1)

    print("\nStarting the WhatsApp Bridge...")
    print("A QR code will be generated momentarily. Please scan it via WhatsApp 'Linked Devices'.")
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

    # Wait for the node script to connect to WhatsApp max 5 minutes
    connected = ready_event.wait(timeout=300)
    
    if not connected:
        print("\nTimed out waiting for WhatsApp connection or bridge crashed.")
        process.terminate()
        sys.exit(1)
        
    print("\n✅ WHATSAPP IS CONNECTED!")

    # --- TARGET SELECTION LOOP ---
    while True:
        print("\n--- SELECT TARGET ---")
        print("1. Person (Number)")
        print("2. Name of group")
        print("3. Group ID")
        print("4. List all Groups (to find IDs)")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            target = input("Enter target phone number with country code (e.g. 61412345678): ").strip()
            if not target.isdigit():
                print("Invalid number. Please only use digits.")
                continue
            action = "send"
            target_label = "number"
            break
        elif choice == '2':
            target = input("Enter the EXACT name of the WhatsApp Group: ").strip()
            action = "send_group"
            target_label = "group"
            break
        elif choice == '3':
            target = input("Enter the Group ID (e.g. 120363xxx@g.us): ").strip()
            action = "send_group_id"
            target_label = "group ID"
            break
        elif choice == '4':
            print("\nFetching group list...")
            payload = {"action": "list_groups"}
            process.stdin.write(json.dumps(payload) + "\n")
            process.stdin.flush()
            time.sleep(3) # Give the background thread time to fetch and print
            continue
        else:
            print("Invalid choice, please try again.")

    print(f"\n🚀 Starting the 1-minute scheduling loop for '{target}'.\n")
    
    message_count = 0
    try:
        while True:
            # Send message payload
            payload = {
                "action": action,
                "target": target,
                "message": "."
            }
            json_str = json.dumps(payload)
            
            process.stdin.write(json_str + "\n")
            process.stdin.flush()
            
            message_count += 1
            print(f"[Python] Loop #{message_count}: Sent '.' to {target_label} '{target}'.")

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
