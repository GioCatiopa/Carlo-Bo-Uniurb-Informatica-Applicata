# Importazione dei moduli
import socket                 # Modulo per la comunicazione di rete
import threading              # Modulo che permette l’esecuzione parallela di più flussi di comunicazione
from settings import config   # Modulo per importare le configurazioni
import time                   # Modulo per la gestione del tempo

# Funzione che inoltra i dati tra due socket
def inoltra_dati(mittente, destinatario, direzioneComunicazione):
    # Il MitM rimane attivo fino a quando la connessione tra client/server viene chiusa 
    while True:
        try:
            # Il MitM prende i dati in arrivo dal client
            data = mittente.recv(config.BUFFER_SIZE)

            # Viene controllato se la connessione e' stata chiusa
            if not data:
                # Se la connessione e' stata chiusa allora si esce dal ciclo
                break

            msg = ""

            try:
                if direzioneComunicazione == "C→S":
                    msg = "[CLIENT] Messaggio: "

                elif direzioneComunicazione == "S→C":
                    msg = "[SERVER] ACK di risposta: "

                testo = msg + data.decode()

                print(f"[MitM {direzioneComunicazione}] {testo}")

            except:
                print(f"[MitM {direzioneComunicazione}] <BIN DATA>")

            # Simulazione della latenza di rete dovuta da un'intercettazione
            time.sleep(1)

            # Viene inviato il messaggio al server
            destinatario.send(data)

        except Exception as e:
            print(f"[MitM ERROR {direzioneComunicazione}] {e}")
            break

    # Vengono chiusi i socket delle connessioni
    mittente.close()
    destinatario.close()

# Gestisce una singola connessione client e crea il canale verso il server
def gestisci_client(client_socket):
    # Creazione del socket TCP verso il server in IPv4
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Imposta l'indirizzo IP e la porta sulla quale il MitM deve inviare i messaggi
    server_socket.connect((config.SERVER_HOST, config.SERVER_PORT))

    print(f"[MitM] Connessione stabilita con server {config.SERVER_HOST}:{config.SERVER_PORT}\n")

    # Creazione thread per inoltrare i dati dal client al server
    t1 = threading.Thread(
        target=inoltra_dati,
        args=(client_socket, server_socket, "C→S")
    )

    # Creazione thread per inoltrare i dati dal server al client
    t2 = threading.Thread(
        target=inoltra_dati,
        args=(server_socket, client_socket, "S→C")
    )

    # Avvio dei thread
    t1.start()
    t2.start()


# Funzione principale del MitM: si comporta come un server e gestisce le connessioni dei client
def main():
    # Creazione del socket del MitM
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Associazione del MitM a un indirizzo e porta specifici
    proxy.bind((config.MITM_HOST, config.MITM_PORT))
    # Viene messo in ascolto di connessioni in ingresso (come il server)
    proxy.listen(5)

    print(f"[MitM] In ascolto su {config.MITM_HOST}:{config.MITM_PORT}")

    # Ciclo infinito in cui il MitM rimane attivo in attesa di client
    while True:
        # Rimane in attesa di una connessione da parte del client
        client_socket, addr = proxy.accept()
        ip, porta = addr
        print(f"[MitM] Client connesso da {ip}:{porta}")

        # Avvia un thread per gestire quella singola connessione
        threading.Thread(
            target=gestisci_client,
            args=(client_socket,)
        ).start()


if __name__ == "__main__":
    main()