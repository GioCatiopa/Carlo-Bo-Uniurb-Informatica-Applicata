# Importazione dei moduli
import socket                 # Modulo per la comunicazione di rete
from settings import config   # Modulo per importare le configurazioni

# Creazione del socket TCP del client in IPv4
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Imposta l'indirizzo IP e la porta sulla quale il client deve inviare i messaggi
client.connect((config.MITM_HOST, config.MITM_PORT))

# Imposta il timeout in attesa di riscontro da parte del server
client.settimeout(15)

print(f"[CLIENT] Connesso a {config.MITM_HOST}")
print("[CLIENT] Digita 'exit' per terminare la connessione\n")

# Ciclo infinito dove il client resta attivo e continua a inviare messaggi al server
while True:
    # Il client rimane in attesa della risposta ACK da parte del server
    try:
        # Richiesta input all'utente
        msg = input("[CLIENT] Messaggio > ")

        # Viene controllato se e' stato digitato il comando di uscita
        if msg.lower() == "exit":
            # Se e' stato digitato il comando di uscita allora si esce dal ciclo
            print("\n[CLIENT] Chiusura connessione in corso")
            break

        # Invio del messaggio
        client.send(msg.encode())

    
        # Attesa risposta con timeout
        risposta = client.recv(config.BUFFER_SIZE)
        msgACK = risposta.decode()
        print(f"[SERVER] ACK di risposta: {msgACK}")

    except socket.timeout:
        print("\n[CLIENT] Timeout raggiunto: nessuna ACK ricevuta")
        continue

    except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
        print("\n[CLIENT] Connessione interrotta da parte del server")
        break

# Viene chiuso il socket del client
client.close()

