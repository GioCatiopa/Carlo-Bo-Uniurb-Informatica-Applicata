# Importazione dei moduli
import socket                   # Modulo per la comunicazione di rete
from settings import config     # Modulo per importare le configurazioni
from crypto import (            # Modulo per importare le funzioni di cifratura e decifratura
    importa_chiave_pubblica,    # Funzione che importa la chiave pubblica RSA
    genera_chiave_AES,          # Funzione che genera la chiave AES
    cifra_RSA,                  # Funzione che cifra con la chiave pubblica RSA
    cifra_AES,                  # Funzione che cifra con la chiave AES
    decifra_AES                 # Funzione che decifra con la chiave AES
)

# Creazione del socket TCP del client in IPv4
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Imposta l'indirizzo IP e la porta sulla quale il client deve inviare i messaggi
client.connect((config.MITM_HOST, config.MITM_PORT))

# Imposta il timeout in attesa di riscontro da parte del server
client.settimeout(15)

print(f"[CLIENT] Connesso a {config.MITM_HOST}")
print("[CLIENT] In attesa della chiave pubblica RSA")

# Fase di handshake crittografico (bloccante):
# Il client attende la ricezione della chiave pubblica RSA dal server
# prima di generare e inviare la chiave simmetrica AES
while True:
    try:
        data = client.recv(config.BUFFER_SIZE)

        # Se il server chiude la connessione
        if not data:
            print("[CLIENT] Connessione interrotta prima di stabilire la comunicazione protetta")
            client.close()
            exit()

        # Controllo ricezione chiave pubblica RSA
        if data.startswith(b"RSA-PUB:"):
            chiave_pubblica_rsa_bytes = data.replace(b"RSA-PUB:", b"")

            chiave_pubblica_rsa = importa_chiave_pubblica(chiave_pubblica_rsa_bytes)

            print("[CLIENT] Chiave RSA ricevuta")

            # Generazione chiave AES
            chiave_aes = genera_chiave_AES()

            # Invio AES cifrata con RSA
            chiave_aes_cifrata = cifra_RSA(chiave_aes, chiave_pubblica_rsa)
            client.send(chiave_aes_cifrata)

            print("[CLIENT] Comunicazione protetta stabilita")
            break
    except socket.timeout:
        print("\n[CLIENT] Timeout raggiunto: Handshake non completato!")
        client.close()
        exit()

print("[CLIENT] Digita 'exit' per terminare la connessione\n")

while True:
    try:
        # Richiesta input all'utente
        msg = input("[CLIENT] Messaggio > ")

        # Viene controllato se e' stato digitato il comando di uscita
        if msg.lower() == "exit":
            print("\n[CLIENT] Chiusura connessione in corso")
            break

        # Invio del messaggio cifrato AES
        client.send(cifra_AES(msg, chiave_aes))

    
        # Attesa risposta con timeout
        risposta = client.recv(config.BUFFER_SIZE)
        msgACK = decifra_AES(risposta, chiave_aes)
        print(f"[SERVER] ACK di risposta: {msgACK}")

    except socket.timeout:
        print("\n[CLIENT] Timeout raggiunto: nessuna ACK ricevuta")
        continue

    except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
        print("\n[CLIENT] Connessione interrotta da parte del server")
        break

# Viene chiuso il socket del client
client.close()