from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

# Funzione che genera una coppia di chiavi RSA (pubblica e privata)
def genera_chiavi_RSA():
    chiave = RSA.generate(2048)

    chiave_privata = chiave
    chiave_pubblica = chiave.publickey()

    return chiave_privata, chiave_pubblica

# Funzione che esporta la chiave pubblica in formato trasmissibile
def esporta_chiave_pubblica(chiave_pubblica):
    return chiave_pubblica.export_key()

# Funzione che importa una chiave pubblica ricevuta dal server
def importa_chiave_pubblica(bytes_chiave):
    return RSA.import_key(bytes_chiave)

# Funzione che cifra dei dati usando la chiave pubblica RSA
def cifra_RSA(dati, chiave_pubblica):
    cifrario = PKCS1_OAEP.new(chiave_pubblica)
    return cifrario.encrypt(dati)

# Funzione che decifra dei dati usando la chiave privata RSA
def decifra_RSA(dati_cifrati, chiave_privata):
    cifrario = PKCS1_OAEP.new(chiave_privata)
    return cifrario.decrypt(dati_cifrati)

# Funzione che genera una chiave AES casuale (256 bit)
def genera_chiave_AES():
    return get_random_bytes(32)

# Funzione che cifra un messaggio con AES (modalità CBC, ovvero cifratura a blocchi)
def cifra_AES(messaggio, chiave):
    cifrario = AES.new(chiave, AES.MODE_CBC)

    testo_cifrato = cifrario.encrypt(
        pad(messaggio.encode(), AES.block_size)
    )

    # Unisce IV + testo cifrato e lo codifica in base64
    return base64.b64encode(cifrario.iv + testo_cifrato)

# Funzione che decifra un messaggio cifrato con AES
def decifra_AES(messaggio_cifrato, chiave):
    dati = base64.b64decode(messaggio_cifrato)

    iv = dati[:16]
    testo_cifrato = dati[16:]

    cifrario = AES.new(chiave, AES.MODE_CBC, iv)

    testo = unpad(
        cifrario.decrypt(testo_cifrato),
        AES.block_size
    )

    return testo.decode()