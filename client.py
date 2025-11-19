import socket
import threading
import keyboard
import pyautogui
import mss
import cv2
import numpy as np
from ultralytics import YOLO

SERVER_IP = '192.168.1.102'
PORT = 5005
TRIGGER_KEY = 'page up'

try:
    model = YOLO('best.pt') 
except:
    print("Внимание: Файл модели 'best.pt' не найден.")
    model = None

def run_ai_logic():
    """Функция поиска кнопки и клика"""
    print(">>> ЗАПУСК НЕЙРОСЕТИ...")
    
    with mss.mss() as sct:
        # Делаем скриншот всего экрана
        monitor = sct.monitors[1]
        screen_img = np.array(sct.grab(monitor))
        
        # Конвертация цвета для OpenCV/YOLO (из BGRA в BGR)
        frame = cv2.cvtColor(screen_img, cv2.COLOR_BGRA2BGR)

        if model:
            # Поиск объектов
            results = model(frame)
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Если уверенность > 50%
                    if box.conf[0] > 0.5:
                        # Получаем координаты (x1, y1, x2, y2)
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Вычисляем центр кнопки
                        center_x = int((x1 + x2) / 2)
                        center_y = int((y1 + y2) / 2)
                        
                        print(f"Кнопка найдена: {center_x}, {center_y}. Кликаю!")
                        
                        # Двигаем мышь и кликаем
                        pyautogui.moveTo(center_x, center_y, duration=0.5)
                        pyautogui.click()
                        return # Завершаем после первого клика
        else:
            print("Модель не загружена, действие пропущено.")

def listen_server(sock):
    """Слушает команды от сервера"""
    while True:
        try:
            data = sock.recv(1024)
            if data == b'TRIGGER_AI':
                # Запускаем ИИ в отдельном потоке, чтобы не блокировать сеть
                ai_thread = threading.Thread(target=run_ai_logic)
                ai_thread.start()
        except:
            print("Связь с сервером потеряна")
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, PORT))
        print(f"Подключено к серверу {SERVER_IP}")
    except Exception as e:
        print(f"Не удалось подключиться: {e}")
        return

    # Запускаем прослушивание сервера в отдельном потоке
    server_listener = threading.Thread(target=listen_server, args=(client,), daemon=True)
    server_listener.start()

    print(f"Нажмите {TRIGGER_KEY}, чтобы отправить сигнал...")
    
    # Слушаем клавиатуру (основной поток)
    while True:
        keyboard.wait(TRIGGER_KEY)
        print("Кнопка нажата! Отправка сигнала...")
        try:
            client.send(b'ACTION')
            # Небольшая задержка, чтобы не спамить сигналом при удержании
            pyautogui.sleep(0.5) 
        except:
            print("Ошибка отправки")
            break

if __name__ == "__main__":
    main()

