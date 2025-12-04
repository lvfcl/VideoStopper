import sys
import subprocess
import os
import time

def install_libs():
    required = {
        'keyboard': 'keyboard',
        'pyautogui': 'pyautogui',
        'mss': 'mss',
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'ultralytics': 'ultralytics'
    }
    
    installed = False
    
    print(">>> Checking libraries...")
    for lib_import, lib_install in required.items():
        try:
            __import__(lib_import)
        except ImportError:
            print(f"!!! Library '{lib_import}' not found. Installing...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "--user", lib_install
                ])
                installed = True
            except subprocess.CalledProcessError as e:
                print(f"ERROR installing {lib_install}. Check internet or proxy.")
                input("Press Enter to exit...")
                sys.exit(1)

    if installed:
        print(">>> All libraries installed. Restarting script...")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        print(">>> All libraries present.")

install_libs()


import socket
import threading
import keyboard
import pyautogui
import mss
import cv2
import numpy as np
from ultralytics import YOLO

SERVER_IP = "0.tcp.eu.ngrok.io"
PORT = 13050
TRIGGER_KEY = 'page up'

try:
    model = YOLO('best.pt') 
except:
    print("Warning: Model file 'best.pt' not found.")
    model = None


def run_ai_logic():
    print(">>> STARTING NEURAL NETWORK...")
    
    try:
        screen_width, screen_height = pyautogui.size()
        
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        pyautogui.moveTo(center_x, center_y, duration=0.1)
        print(f"Cursor moved to center: ({center_x}, {center_y})")
        
        pyautogui.sleep(0.5) 
        
    except Exception as e:
        print(f"Error moving cursor: {e}")
        return

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screen_img = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(screen_img, cv2.COLOR_BGRA2BGR)

        cv2.imwrite("debug_frame.jpg", frame)

        if not model:
            print("Model not loaded")
            return

        try:
            results = model(frame, imgsz=640, conf=0.02)
        except Exception as e:
            print(f"Error running model: {e}")
            return

        if len(results) == 0:
            print("YOLO returned no results")
            return

        try:
            annotated = results[0].plot()
            cv2.imwrite("debug_yolo.jpg", annotated)
            print("debug_yolo.jpg saved")
        except Exception as e:
            print(f"Error drawing results: {e}")

        for result in results:
            for box in result.boxes:
                if box.conf[0] > 0.01:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)

                    print(f"Object detected: {center_x}, {center_y}")
                    pyautogui.moveTo(center_x, center_y, duration=0.5)
                    pyautogui.click()
                    return


def listen_server(sock, stop_event): 
    while not stop_event.is_set():
        try:
            data = sock.recv(1024)
            if not data:
                print("Server closed connection.")
                stop_event.set()
                break
                
            if data == b'TRIGGER_AI':
                threading.Thread(target=run_ai_logic, daemon=True).start()
                
        except socket.error:
            print("Connection error (recv).")
            stop_event.set()
            break
        except Exception as e:
            print(f"Error in listener: {e}")
            stop_event.set()
            break

def main():
    while True:
        client = None
        stop_event = threading.Event()
        
        try:
            print(f"Connecting to {SERVER_IP}:{PORT}...")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(5)
            client.connect((SERVER_IP, PORT))
            client.settimeout(None)
            
            print(f">>> CONNECTED! Press {TRIGGER_KEY} for action.")
            
            server_listener = threading.Thread(target=listen_server, args=(client, stop_event), daemon=True)
            server_listener.start()

            while not stop_event.is_set():
                if keyboard.is_pressed(TRIGGER_KEY):
                    print("Button pressed! Sending signal...")
                    try:
                        client.send(b'ACTION')
                        time.sleep(0.5) 
                    except socket.error:
                        print("Error sending data.")
                        stop_event.set()
                        break
                
                time.sleep(0.05)

        except Exception as e:
            print(f"Failed to connect: {e}")
        
        finally:
            if client:
                client.close()
            
            if not stop_event.is_set():
                stop_event.set()
            
            print("Retrying connection in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()