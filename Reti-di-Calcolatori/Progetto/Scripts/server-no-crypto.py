# Importazione dei moduli
import socket                 # Modulo per la comunicazione di rete
from settings import config   # Modulo per importare le configurazioni

# Creazione del socket TCP del server in IPv4
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Imposta l'indirizzo IP e la porta sulla quale il server deve rimanere in ascolto
server.bind((config.SERVER_HOST, config.SERVER_PORT))
# Imposta il server in modalita' ascolto (5 e' il numero massimo di Client in attesa)
server.listen(5)

print(f"[SERVER] In ascolto su {config.SERVER_HOST}:{config.SERVER_PORT}")

# Il server resta sempre attivo e in ascolto
while True:
    # Il server si ferma in attesa finche' il SO non fornisce la
    # prossima connessione disponibile dalla coda (tramite ordine FIFO) 
    conn, addr = server.accept()

    ip, porta = addr
    print(f"[SERVER] Connessione da {ip}:{porta}\n")

    # Ciclo infinito dove il server resta attivo e continua a ricevere messaggi
    while True:
        try:
            # Ricezione dei dati
            data = conn.recv(config.BUFFER_SIZE)

            # Viene controllato se il client ha chiuso la connessione
            if not data:
                break

            # Conversione dei byte ricevuti in stringa
            msg = data.decode()
            print(f"[CLIENT] Messaggio ricevuto: {msg}")

            # Il server invia al client una risposta di conferma (ACK) codificata in byte
            conn.send(msg.encode())

        except ConnectionResetError:
            print("\n[SERVER] Connessione interrotta forzatamente")
            break

    # Viene chiusa la connessione con il client
    conn.close()