import socket
import threading

HOST = '0.0.0.0'
PORT = 5005

clients = []

def handle_client(client_socket, addr):
    print(f"[+] Новое подключение: {addr}")
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            
            print(f"Получен сигнал от {addr}. Рассылка...")
            
            # Отправляем сигнал всем, кроме отправителя
            for c in clients:
                if c != client_socket:
                    try:
                        c.send(b'TRIGGER_AI')
                    except:
                        clients.remove(c)
        except:
            break
    
    print(f"[-] Отключение: {addr}")
    clients.remove(client_socket)
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Сервер запущен на {HOST}:{PORT}")

    while True:
        client_sock, addr = server.accept()
        clients.append(client_sock)
        thread = threading.Thread(target=handle_client, args=(client_sock, addr))
        thread.start()

if __name__ == "__main__":
    start_server()

