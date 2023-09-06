# Sistema di Bilanciamento del Carico per Server di Calcolo
***
Questo repository contiene un'implementazione in Python di un sistema client-server intermediato da un sistema di load balacing. Il load balancer sfrutta l'algoritmo di bilanciamento del carico Round Robin, che assegna in maniera sequenziale le richieste ai server ad esso collegati che risultano attivi. 

## Introduzione
Questo programma implementa un sistema client-server intermediato da un server di load balacing utilizzano Python. Per fare ciò utilizza tre classi: client, loadBalancer e server. Il client effettua delle richieste al load balancer, il quale le invia ai server sfruttando l'algoritmo di bilanciamento del carico Round Robin. Questo algoritmo assegna le richieste in maniera sequenziale ai server ad esso collegati e che risultano attivi nella sessione. Infine, il load balancer riceve le risposte dai server e le reindirizza al client.

## Descrizione dell'architettura
L'architettura prevede l'utilizzo di un client, un load balancer e tre server. Il `client` richiede in input un comando; se viene digitato il comando di creazione di richieste randomiche, e viene successivamente inserito il numero di richieste da effettuare, queste vengono scelte randomicamente all'interno di un set di operazioni pre-fissate e inviate al load balancer. Il `loadbalancer` invia le richieste ai server che risultano essere attivi; per verificare l'attività o l'inattività dei server effettua precedentemente un controllo di connessione con i server ad esso collegati. Le richieste vengono assegnate utilizzando l'algoritmo di bilanciamento del carico Round Robin: il load balancer invia richieste ai server in maniera sequenziale. In seguito, i `server` effettuano il calcolo richiesto e inviano la risposta al load balancer, che la inoltra al client. 

Il sistema permette quindi una gestione dinamica dei server: il load balancer tiene traccia dei server attivi e inattivi in ogni sessione, per inviare le richieste solo a quelli connessi. Con la stessa logica, il sistema appare altamente tollerante ai guasti, in quanto la disconnessione improvvisa di un server non causa interruzioni nell'invio delle richieste a quelli funzionanti.  

Il load balancer tiene inoltre traccia delle attività di ogni sessione; in particolare, registra sul file `loadbalancer.log` le connessioni e le richieste effettuate. 

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

Se nessuna delle due condizioni è verificata, il client rimane in attesa di ricevere una risposta dal server tramite la connessione socket.
La risposta ricevuta dal server viene quindi stampata e il numero di richieste rimanenti viene decrementato di uno.

Quando si verificano le condizioni di uscita, la connessione con il server viene chiusa.

### Loadbalancer:
Affichè il load balancer sia in ascolto per connessioni in arrivo dai client, è stata impostata la porta `self.port` ed è stato specificato l'indirizzo IP `self.ip`(127.0.0.1 per l'ascolto locale).

In seguito, sono stati definiti alcuni metodi:

Il metodo `monitor_keyboard_input`, che utilizza il modulo `pynput.keyboard`, è responsabile per la gestione dell'input da tastiera e, in particolare, per la rilevazione della pressione del tasto "esc" per la chiusura del load balancer. Quando il tasto "esc" viene premuto, il listener chiama la funzione `handle_esc_key` che, tramite il flag `shutdown_event`, segnala al loadbalancer che è necessario iniziare la procedura di chiusura.

#### Connessione: accettare e gestire le connessioni in entrata dai client.
La funzione `connessione_client` controlla il flag `shutdown_event`, oggetto `multiprocessing.Event` utilizzato per segnalare la chiusura del load balancer. Il loadbalancer accetta continuamente le connessioni dei client finché il flag di chiusura non è impostato.

E' stato impostato un timeout sulla socket del load balancer utilizzando `settimeout(1)` affinchè il loadbalancer aspetti al massimo un secondo per accettare una connessione prima di continuare l'esecuzione.

Quindi, finchè il flug non viene impostato, il loadbalancer accetta le connessioni in entrata dal client: la funzione `accept` sulla socket del load balancer attende finché un client si connette e quindi restituisce la nuova socket, `client_socket`, specifica per quel client in base al suo indirizzo IP `client_ip`.
Se una connessione viene accettata entro il timeout di 1 secondo, il client viene aggiunto alla lista `self.clients` che tiene traccia dei client connessi e viene stampato un messaggio sulla console per segnalare la connessione accettata, mostrando l'indirizzo IP e la porta del client.

La lista dei client connessi (`self.clients`) consente al load balancer di gestire simultaneamente più client, aspettando che si connettano e poi aggiungendoli alla lista per l'elaborazione futura delle loro richieste.

#### Gestione della comunicazione con il client:
La funzione `gestione_comunicazione_client` è responsabile della gestione della comunicazione con i client che si connettono al load balancer. 

La funzione attende la ricezione dei comandi dal client attraverso il socket `client_socket` che, una volta ricevuti dal client, vengono memorizzati nella variabile `data` e vengono decodificati dalla rappresentazione binaria in una stringa. La funzione, quindi, verifica il comando ricevuto dal client:

Se il comando è "exit", il client sta chiudendo la connessione e la funzione invia una risposta al client confermando la disconnessione, quindi elimina dalla lista dei clients attivi `active_clients` il client che si sta disconnettendo e termina il ciclo.

Se il comando ricevuto non è "exit", il load balancer stampa il messaggio che ha ricevuto dal client. L'esecuzione del comando viene svolta dalla funzione `esegui_comandi`.

...

#### Bilanciamento del carico: algoritmo di ROUND ROBIN
La funzione `round_robin` è un metodo che implementa l'algoritmo di bilanciamento del carico Round Robin. L'obiettivo di questo metodo è selezionare il server successivo a cui inoltrare una richiesta da parte di un client, garantendo una distribuzione equa del carico tra i server disponibili.

La funzione monitora lo stato dei server chiamando il metodo `monitoraggio_server`:
##### Monitoraggio dei server:
che dovrebbe controllare se i server sono attivi o meno e aggiornare i flag self.server_flags in base a questa informazione.


Monitorato lo stato dei server, il metodo sceglie il prossimo server a cui inoltrare la richiesta nell'ordine circolare: Inizia dal primo server nell'elenco e prosegue fino all'ultimo, quindi torna indietro e riparte dal server di partenza.
La funzione verifica, attraverso il flag corrispondente nell'elenco `self.server_flags` se il server è considerato attivo:

Se il server è attivo, viene selezionato per l'inoltro e l'indice del server corrente viene incrementato in modo che la prossima richiesta venga inoltrata al server successivo nell'ordine circolare.

Se il server selezionato non è attivo, il comando viene inoltrato al server attivo successivo, nell'ordine circolare.

Alla fine, il metodo restituisce l'indirizzo IP e la porta del server selezionato, che verranno utilizzati per inoltrare la richiesta del client a questo server specifico.




#### Inoltro del messaggio dal client al server:
La funzione `route_message` viene chiamata quando il load balancer ha ricevuto un messaggio da un client e ha bisogno di instradarlo a uno dei server disponibili.
Scelto il server di destinazione, secondo l'algoritmo di Round Robin descritto precednetemente, la funzione crea una connessione socket verso quel server utilizzando l'indirizzo IP (`server_address`) e la porta del server (`server_port`). Il messaggio ricevuto dal client viene inoltrato al server attraverso la socket appena creata, la funzione attende una risposta dal server, che viene ricevuta tramite la socket e può contenere il risultato dell'elaborazione del comando da parte del server, e la risposta viene inviata al client originale tramite la sua connessione socket. In questo modo, il client riceve la risposta alla sua richiesta.
La connessione socket tra il load balancer e il server viene quindi chiusa.

La funzione ha completato il processo di instradamento del messaggio e ritorna al loop principale del load balancer, pronto a gestire la prossima richiesta da un client.

#### Arresto: chiusura del load balancer in modo controllato.
La funzione `shutdown` assicura che tutte le connessioni siano chiuse in modo pulito e che tutte le attività in corso siano terminate prima che il programma del load balancer venga terminato. Questo contribuisce a evitare problemi di perdita di dati o connessioni incomplete durante la chiusura del load balancer.

Se, atraverso il flug `shutdown_event`, è stata richiesta la chiusura del load balancer, non è necessario eseguire ulteriori operazioni. Se, viceversa, la chiusura non è ancora stata richiesta, la funzione procede con la chiusura del load balancer. 

Per prima cosa, chiude la socket del load balancer, `self.balancer_socket`, se è stata creata. Questo assicura che il load balancer smetta di accettare nuove connessioni dai client.
Successivamente, chiude tutte le connessioni attive con i client che sono stati aggiunti alla lista `self.active_clients`. Questo garantisce che tutte le connessioni con i client vengano chiuse correttamente prima della chiusura del load balancer.

La funzione poi esegue un ciclo per attendere che tutti i thread attivi, tranne il thread principale, vengano completati.                                       
La funzione `threading.enumerate()` viene utilizzata per ottenere l'elenco di tutti i thread attivi, e quelli che non sono thread principali e non sono in modalità daemon vengono attesi e chiusi.

Infine, una volta che tutti i thread sono stati chiusi e il processo di chiusura è completo, la funzione emette un messaggio di conferma, indicando che il load balancer è stato chiuso correttamente.


