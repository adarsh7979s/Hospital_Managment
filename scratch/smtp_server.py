import socket
import threading

def handle_client(client_socket):
    try:
        client_socket.sendall(b"220 localhost ESMTP MockServer\r\n")
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            cmd = data.decode(errors='replace').strip()
            print(f"[SMTP CLIENT] {cmd}")
            
            if cmd.upper().startswith("HELO") or cmd.upper().startswith("EHLO"):
                client_socket.sendall(b"250-localhost Hello\r\n250-SIZE 250000\r\n250-8BITMIME\r\n250 HELP\r\n")
            elif cmd.upper().startswith("MAIL FROM:"):
                client_socket.sendall(b"250 OK\r\n")
            elif cmd.upper().startswith("RCPT TO:"):
                client_socket.sendall(b"250 OK\r\n")
            elif cmd.upper().startswith("DATA"):
                client_socket.sendall(b"354 Start input; end with <CR><LF>.<CR><LF>\r\n")
                
                mail_data = b""
                while True:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    mail_data += chunk
                    if b"\r\n.\r\n" in mail_data or mail_data.endswith(b"\r\n.\r\n") or mail_data.endswith(b"\n.\n"):
                        break
                
                print("\n" + "="*40)
                print("[SMTP SERVER] RECEIVED MAIL CONTENT:")
                print("="*40)
                print(mail_data.decode(errors='replace').strip())
                print("="*40 + "\n")
                
                client_socket.sendall(b"250 OK: queued as 12345\r\n")
            elif cmd.upper().startswith("QUIT"):
                client_socket.sendall(b"221 Bye\r\n")
                break
            else:
                client_socket.sendall(b"250 OK\r\n")
    except Exception as e:
        print(f"SMTP Client handler error: {e}")
    finally:
        client_socket.close()

def run_smtp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 1025))
    server.listen(5)
    print("Mock SMTP Server listening on 127.0.0.1:1025...")
    while True:
        try:
            client, addr = server.accept()
            print(f"Accepted SMTP connection from {addr}")
            threading.Thread(target=handle_client, args=(client,), daemon=True).start()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"SMTP Accept error: {e}")

if __name__ == "__main__":
    run_smtp_server()
