# Importazione dei moduli
import socket                   # Modulo per la comunicazione di rete
from settings import config     # Modulo per importare le configurazioni
from crypto import (            # Modulo per importare le funzioni di cifratura e decifratura
    genera_chiavi_RSA,          # Funzione che genera la coppia di chiavi RSA  
    esporta_chiave_pubblica,    # Funzione che esporta la chiave pubblica RSA
    decifra_RSA,                # Funzione che decifra tramite RSA
    decifra_AES,                # Funzione che decifra tramite AES
    cifra_AES                   # Funzione che cifra tramite AES
)

# Creazione del socket TCP del server in IPv4
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Imposta l'indirizzo IP e la porta sulla quale il server deve rimanere in ascolto
server.bind((config.SERVER_HOST, config.SERVER_PORT))
# Imposta il server in modalita' ascolto (5 e' il numero massimo di Client in attesa)
server.listen(5)

# Viene generata la coppia di chiavi RSA
chiave_privata, chiave_pubblica = genera_chiavi_RSA()

print(f"[SERVER] In ascolto su {config.SERVER_HOST}:{config.SERVER_PORT}")

# Il server resta sempre attivo e in ascolto
while True:
    # Attesa connessione client
    conn, addr = server.accept()
    ip, porta = addr
    print(f"[SERVER] Connessione da {ip}:{porta}")

    try:
        # Viene inviata la chiave pubblica RSA al client
        conn.send(b"RSA-PUB:" + esporta_chiave_pubblica(chiave_pubblica))

        # Viene ricevuta la chiave AES cifrata da parte del client
        chiave_aes_cifrata = conn.recv(config.BUFFER_SIZE)
        # Decifratura della chiave AES ricevuta
        chiave_aes = decifra_RSA(chiave_aes_cifrata, chiave_privata)

        print("[SERVER] Chiave AES ricevuta e decifrata")
        print("[SERVER] Inizio comunicazione protetta\n")

        # Ciclo che mantiene attiva la sessione con il client
        while True:
            data = conn.recv(config.BUFFER_SIZE)

            if not data:
                break

            # Il messaggio ricevuto viene decifrato tramite AES
            msg = decifra_AES(data, chiave_aes)
            print(f"[CLIENT] Messaggio ricevuto: {msg}")

            # La risposta ACK viene cifrata e poi mandata al client
            risposta = cifra_AES(msg, chiave_aes)
            conn.send(risposta)

    # Gestione dell'errore nel caso in cui la connessione con il client venga interrotta
    except ConnectionResetError:
        print("\n[SERVER] Connessione interrotta forzatamente")

    finally:
        conn.close()
        print("\n[SERVER] Connessione chiusa")