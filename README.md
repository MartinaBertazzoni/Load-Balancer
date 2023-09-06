# Sistema di Bilanciamento del Carico per Server di Calcolo
***
Questo repository contiene un'implementazione in Python di un sistema client-server intermediato da un sistema di load balacing. Il load balancer sfrutta l'algoritmo di bilanciamento del carico Round Robin, che assegna in maniera sequenziale le richieste ai server ad esso collegati che risultano attivi. 

## Introduzione
Questo programma implementa un sistema client-server intermediato da un server di load balacing utilizzano Python. Per fare ciò utilizza tre classi: client, loadBalancer e server. Il client effettua delle richieste al load balancer, il quale le invia ai server sfruttando l'algoritmo di bilanciamento del carico Round Robin. Questo algoritmo assegna le richieste in maniera sequenziale ai server ad esso collegati e che risultano attivi nella sessione. Infine, il load balancer riceve le risposte dai server e le reindirizza al client.

## Descrizione dell'architettura
L'architettura prevede l'utilizzo di un client, un load balancer e tre server. Il `client` richiede in input un comando; se viene digitato il comando di creazione di richieste randomiche, e viene successivamente inserito il numero di richieste da effettuare, queste vengono scelte randomicamente all'interno di un set di operazioni pre-fissate e inviate al load balancer. Il `loadbalancer` invia le richieste ai server che risultano essere attivi; per verificare l'attività o l'inattività dei server effettua precedentemente un controllo di connessione con i server ad esso collegati. Le richieste vengono assegnate utilizzando l'algoritmo di bilanciamento del carico Round Robin: il load balancer invia richieste ai server in maniera sequenziale. In seguito, i `server` effettuano il calcolo richiesto e inviano la risposta al load balancer, che la inoltra al client. 

Il sistema permette quindi una gestione dinamica dei server: il load balancer tiene traccia dei server attivi e inattivi in ogni sessione, per inviare le richieste solo a quelli connessi. Con la stessa logica, il sistema appare altamente tollerante ai guasti, in quanto la disconnessione improvvisa di un server non causa interruzioni nell'invio delle richieste a quelli funzionanti.  

Il load balancer tiene inoltre traccia delle attività di ogni sessione; in particolare, registra sul file loadbalancer.log le connessioni e le richieste effettuate. 

## Funzionamento
Abbiamo 6 file: `client.py`, `loadBalancer.py`, `server1.py`, `server2.py`, `server3.py` e `loadbalancer.log`. 

### Client:
Il file `client.py` contiene la classe `client` con tutti i metodi per consentire la comunicazione delle richieste e delle rispettive risposte con il load balancer.
#### Connessione al load balancer:
Con la funzione `connessione_al_loadbalancer` si ha la connessione del client al load balancer tramite una socket TCP. Nello specifico, viene impostato l'indirizzo IP del load balancer (`loadBalancer_ip`) e la porta su cui il load balancer è in ascolto (`loadBalancer_port`) per creare una nuova istanza di socket TCP/IP per il client (`socket.socket(socket.AF_INET, socket.SOCK_STREAM)`) e il client utilizza il metodo `connect` per stabilire una connessione con il load balancer specificando l'indirizzo IP e la porta del load balancer come argomenti.
Se la connessione ha successo, viene stampato un messaggio di conferma e la funzione restituisce la socket del client connesso al load balancer.
In caso di errore durante la connessione, viene stampato un messaggio di errore e il programma viene chiuso.

La socket del client connesso verrà utilizzata per inviare i comandi al load balancer e ricevere le risposte.

#### Creazione del comando random:
La funzione `crea_comando_random` utilizza la funzione `random.choice()` del modulo random di Python per selezionare casualmente uno dei quattro comandi della lista `comandi_possibili`: "somma," "sottrazione," "moltiplicazione," o "divisione".

Il comando selezionato casualmente è memorizzato nella variabile `comando_casuale` e può essere successivamente inviato al load balancer per l'elaborazione del server disponibile.

#### Avvio del client:
La funzione `avvio client` avvia e chiude tre thread:                                                
##### 1) Interfaccia: prende in imput  i comandi che devono essere eseguiti.
Con il metodo  `interfaccia_client` viene avviata un'interfaccia utente che permette agli utenti di inserire comandi manualmente o , digitando "random", generare comandi casuali (`crea_comando_random()`) e, in tal caso, comunicare il numero di richieste randomiche che devono essere create. Digitando "exit" sull'interfaccia, si ha la chiusura della connessione con il server.
Questi comandi vengono aggiunti alla lista di comandi da eseguire `self.comandi`.

##### 2) Invio dei comandi al load balancer.
 La funzione `invia_richieste_al_loadbalancer` controlla se la lista `self.comandi` contiene comandi da inviare: Se la lista è vuota, continua a scorrere il thread senza inviare nulla.
Se ci sono comandi nella lista, estrae il primo comando e lo assegna alla variabile `comando`.

Se il comando è "exit", imposta la flag `self.chiusura` su True per segnalare che il client sta chiudendo la connessione, invia il comando "exit" al load balancer tramite la connessione socket, incrementa il contatore `self.counter_richieste` per tener traccia delle richieste inviate e stampa un messaggio di chiusura della connessione con il server.

Se il comando non è "exit", invia il comando al load balancer tramite la connessione socket e incrementa il contatore `self.counter_richieste` per tener traccia delle richieste inviate.

Dopo l'invio del comando, la funzione continua ad attendere nuovi comandi da inviare. 
La funzione continua ad eseguire questo ciclo fino a quando il client non decide di chiudere la connessione.

##### 3) Ricezione delle risposte dai server:
La funzione `ricezione_risposta` verifica due condizioni: 
 
Se `self.counter_richieste`, che indica il numero di richieste inviate, è inferiore o uguale a zero, tutte le richieste sono state elaborate e il client può chiudere la connessione con il server interrompendo il loop.

Se la flag `self.chiusura` è impostata su True, il client sta richiedendo la chiusura della connessione e il loop si interrompe anche in questo caso.

### Loadbalancer:

Se nessuna delle due condizioni è verificata, il client rimane in attesa di ricevere una risposta dal server tramite la connessione socket.
La risposta ricevuta dal server viene quindi stampata e il numero di richieste rimanenti viene decrementato di uno.

Quando si verificano le condizioni di uscita, la connessione con il server viene chiusa.

### Loadbalancer:
Affichè il load balancer sia in ascolto per connessioni in arrivo dai client, è stata impostata la porta `self.port` ed è stato specificato l'indirizzo IP `self.ip`(127.0.0.1 per l'ascolto locale).

#### Avvio del loadbalancer:

#### Connessione: accettare e gestire le connessioni in entrata dai client.
La funzione `connessione_client` controlla il flag `shutdown_event`, oggetto `multiprocessing.Event` utilizzato per segnalare la chiusura del load balancer. Il loadbalancer accetta continuamente le connessioni dei client finché il flag di chiusura non è impostato.

E' stato impostato un timeout sulla socket del load balancer utilizzando `settimeout(1)` affinchè il loadbalancer aspetti al massimo un secondo per accettare una connessione prima di continuare l'esecuzione.

Quindi, finchè il flug non viene impostato, il loadbalancer accetta le connessioni in entrata dal client: la funzione `accept` sulla socket del load balancer attende finché un client si connette e quindi restituisce la nuova socket, `client_socket`, specifica per quel client in base al suo indirizzo IP `client_ip`.
Se una connessione viene accettata entro il timeout di 1 secondo, il client viene aggiunto alla lista `self.clients` che tiene traccia dei client connessi e viene stampato un messaggio sulla console per segnalare la connessione accettata, mostrando l'indirizzo IP e la porta del client.
