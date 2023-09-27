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

#### Avvio del client:
La funzione `avvio_client`, per prima cosa, stabilisce la connessione tra il client e il load balancer:
##### Connessione al load balancer:
Con la funzione `connessione_al_loadbalancer` si ha la connessione del client al load balancer tramite una socket TCP. Nello specifico, viene impostato l'indirizzo IP del load balancer (`loadBalancer_ip`) e la porta su cui il load balancer è in ascolto (`loadBalancer_port`) per creare una nuova istanza di socket TCP/IP per il client (`socket.socket(socket.AF_INET, socket.SOCK_STREAM)`) e il client utilizza il metodo `connect` per stabilire una connessione con il load balancer specificando l'indirizzo IP e la porta del load balancer come argomenti.
Se la connessione ha successo, viene stampato un messaggio di conferma e la funzione restituisce la socket del client connesso al load balancer.
In caso di errore durante la connessione, viene stampato un messaggio di errore e il programma viene chiuso.

La socket del client connesso verrà utilizzata per inviare i comandi al load balancer e ricevere le risposte.

Dopo aver stabilito la connessione con il load balancer, la funzione `avvio client` avvia e chiude tre thread:                                                
##### 1) Interfaccia: prende in imput  i comandi che devono essere eseguiti.
Con il metodo  `interfaccia_client` viene avviata un'interfaccia utente che permette agli utenti di inserire comandi manualmente. Digitando "random", vengono generati comandi casuali (richiamando la funzione `crea_comando_random()`) e, in tal caso, occorre comunicare il numero di richieste randomiche che devono essere create. Digitando "exit" sull'interfaccia, si ha la chiusura della connessione con il server.
Questi comandi vengono aggiunti alla lista di comandi da eseguire `self.comandi`.

In questa parte di codice è stata impiegata la funzione `time.sleep()` per mettere in pausa l'esecuzione del programma per un certo periodo di tempo. Infatti, in tal modo, è stato possibile sincronizzare l'esecuzione dell'operazione affinchè fosse in linea con altre parti del programma.

##### 2) Invio dei comandi al load balancer.
 La funzione `invia_richieste_al_loadbalancer` controlla se la lista `self.comandi` contiene comandi da inviare: Se la lista è vuota, continua a scorrere il thread senza inviare nulla.
Se ci sono comandi nella lista, estrae il primo comando e lo assegna alla variabile `comando`.

Se il comando è "exit", imposta la flag `self.chiusura` su True per segnalare che il client sta chiudendo la connessione, converte il comando "exit" in una stringa di byte e lo invia al load balancer tramite la connessione socket, incrementa il contatore `self.counter_richieste` per tener traccia delle richieste inviate e stampa un messaggio di chiusura della connessione con il server.

Se il comando non è "exit", invia il comando, convertito in una stringa di byte, al load balancer tramite la connessione socket e incrementa il contatore `self.counter_richieste` per tener traccia delle richieste inviate.

Dopo l'invio del comando, la funzione continua ad attendere nuovi comandi da inviare. 
La funzione continua ad eseguire questo ciclo fino a quando il client non decide di chiudere la connessione.

##### 3) Ricezione delle risposte dai server:
La funzione `ricezione_risposta` verifica due condizioni: 
 
Se `self.counter_richieste`, che indica il numero di richieste inviate, è inferiore o uguale a zero, tutte le richieste sono state elaborate e il client può chiudere la connessione con il server interrompendo il loop.

Se la flag `self.chiusura` è impostata su True, il client sta richiedendo la chiusura della connessione tramite il comando "exit" e il loop si interrompe anche in questo caso.

Se nessuna delle due condizioni è verificata, il client rimane in attesa di ricevere una risposta dal server tramite la connessione socket.
La risposta ricevuta dal server viene quindi decodificata e stampata e il numero di richieste rimanenti viene decrementato di uno.

#### Creazione del comando random:
La funzione `crea_comando_random` utilizza la funzione `random.choice()` del modulo random di Python per selezionare casualmente uno dei quattro comandi della lista `comandi_possibili`: "somma," "sottrazione," "moltiplicazione," o "divisione".

Il comando selezionato casualmente è memorizzato nella variabile `comando_casuale` e può essere successivamente inviato al load balancer per l'elaborazione del server disponibile.

### Loadbalancer:
Affichè il load balancer sia in ascolto per connessioni in arrivo dai client, è stata impostata la porta `self.port` ed è stato specificato l'indirizzo IP `self.ip`(127.0.0.1 per l'ascolto locale).

In seguito, sono stati definiti alcuni metodi:

Il metodo `monitor_keyboard_input`, che utilizza il modulo `pynput.keyboard`, è responsabile per la gestione dell'input da tastiera e, in particolare, per la rilevazione della pressione del tasto "esc" per la chiusura del load balancer. Quando il tasto "esc" viene premuto, il listener chiama la funzione `handle_esc_key` che, tramite il flag `shutdown_event`, segnala al loadbalancer che è necessario iniziare la procedura di chiusura.

#### Arresto: chiusura del load balancer in modo controllato.
La funzione `shutdown` assicura che tutte le connessioni siano chiuse in modo pulito e che tutte le attività in corso siano terminate prima che il programma del load balancer venga terminato. Questo contribuisce a evitare problemi di perdita di dati o connessioni incomplete durante la chiusura del load balancer.

Se, atraverso il flug `shutdown_event`, è stata richiesta la chiusura del load balancer, non è necessario eseguire ulteriori operazioni. Se, viceversa, la chiusura non è ancora stata richiesta, la funzione procede con la chiusura del load balancer. 

Per prima cosa, chiude la socket del load balancer, `self.balancer_socket`, se è stata creata. Questo assicura che il load balancer smetta di accettare nuove connessioni dai client.
Successivamente, chiude tutte le connessioni attive con i client che sono stati aggiunti alla lista `self.active_clients`. Questo garantisce che tutte le connessioni con i client vengano chiuse correttamente prima della chiusura del load balancer.

La funzione poi esegue un ciclo per attendere che tutti i thread attivi, tranne il thread principale, vengano completati.                                       
La funzione `threading.enumerate()` viene utilizzata per ottenere l'elenco di tutti i thread attivi, e quelli che non sono thread principali e non sono in modalità daemon vengono attesi e chiusi.

Infine, una volta che tutti i thread sono stati chiusi e il processo di chiusura è completo, la funzione emette un messaggio di conferma, indicando che il load balancer è stato chiuso correttamente.

#### Connessione tra loadbalancer e server
Con la funzione `creazione_socket_loadBalancer`, viene creata una socket server di tipo TCP, che viene collegata all'indirizzo (`self.ip`) e alla posta (`self.porta`) specificati.
Una volta configurata la socket, viene chiamato il metodo `listen()` su di essa. Questo metodo mette effettivamente in ascolto la socket, permettendo al load balancer di accettare le connessioni in entrata dai client.
Viene visualizzato un messaggio di log che indica che il server di load balancing è in ascolto su un certo indirizzo e porta e vengono avviati due thread separati:

##### 1) Connessione: accettare e gestire le connessioni in entrata dai client.
La funzione `connessione_client` controlla il flag `shutdown_event`, oggetto `multiprocessing.Event` utilizzato per segnalare la chiusura del load balancer. Il loadbalancer accetta continuamente le connessioni dei client finché il flag di chiusura non è impostato.

E' stato impostato un timeout sulla socket del load balancer utilizzando `settimeout(1)` affinchè il loadbalancer aspetti al massimo un secondo per accettare una connessione prima di continuare l'esecuzione.

Quindi, finchè il flug non viene impostato, il loadbalancer accetta le connessioni in entrata dal client: la funzione `accept` sulla socket del load balancer attende finché un client si connette e quindi restituisce la nuova socket, `client_socket`, specifica per quel client in base al suo indirizzo IP `client_ip`.
Se una connessione viene accettata entro il timeout di 1 secondo, il client viene aggiunto alla lista `self.clients` che tiene traccia dei client connessi e viene stampato un messaggio sulla console per segnalare la connessione accettata, mostrando l'indirizzo IP e la porta del client.

La lista dei client connessi (`self.clients`) consente al load balancer di gestire simultaneamente più client, aspettando che si connettano e poi aggiungendoli alla lista per l'elaborazione futura delle loro richieste.

##### 2) Gestione della comunicazione con il client:
La funzione `thread_client` è responsabile della gestione dei client connessi al load balancer attraverso l'uso di thread separati. La lista `active_threads` è utilizzata per tenere traccia dei thread attivi, ossia i thread che gestiscono le connessioni dei client.

Finchè il codice è in esecuzione, la funzione verifica se la lista `self.clients`, contiene client che sono in attesa di essere eseguiti in quanto hanno stabilito una connessione con il load balancer ma non sono ancora stati associati a un thread per la gestione delle loro richieste.
Quindi, la funzione estrae il primo client dalla lista self.clients rimuovendolo e lo aggiunge alla lista `self.active_clients`.

Viene creato un nuovo thread chiamato `client_thread` che, quando viene avviato, fa sì che ogni client connesso riceva un thread dedicato per gestire le sue richieste.
opo aver avviato il thread per un client, la funzione continua a controllare la lista active_threads per verificare se ci sono thread che hanno completato la loro esecuzione.
Se un thread nella lista active_threads ha completato la sua esecuzione, il thread viene rimosso dalla lista e il ciclo continua a controllare gli altri thread.

Questo approccio multithreading è fondamentale per consentire al load balancer di essere reattivo e gestire più client contemporaneamente.

La funzione `gestione_comunicazione_client` è responsabile della gestione della comunicazione con i client che si connettono al load balancer. 
La funzione attende la ricezione dei comandi dal client attraverso il socket `client_socket` che, una volta ricevuti dal client, vengono memorizzati nella variabile `data` e vengono decodificati dalla rappresentazione binaria in una stringa. La funzione, quindi, verifica il comando ricevuto dal client:

Se il comando è "exit", il client sta chiudendo la connessione e la funzione invia una risposta al client confermando la disconnessione, quindi elimina dalla lista dei clients attivi `active_clients` il client che si sta disconnettendo e termina il ciclo.

Se il comando ricevuto non è "exit", il load balancer stampa il messaggio che ha ricevuto dal client. L'esecuzione del comando viene svolta dalla funzione `esegui_comandi`.

...

#### Bilanciamento del carico: algoritmo di ROUND ROBIN
La funzione `round_robin` è un metodo che implementa l'algoritmo di bilanciamento del carico Round Robin. L'obiettivo di questo metodo è selezionare il server successivo a cui inoltrare una richiesta da parte di un client, garantendo una distribuzione equa del carico tra i server disponibili.

La funzione monitora lo stato dei server chiamando il metodo monitoraggio_server:
##### Monitoraggio dei server:
La funzione `monitoraggio_server` controlla se i server sono attivi attraverso un tentativo di connessione alla porta del server utilizzando una socket `server_socket`. 

Se il tentativo di connessione riesce senza errori, il server è attivo e operativo e la funzione imposta il flag corrispondente a quel server nella lista `self.server_flags` su True.

Se il tentativo di connessione fallisce, significa che il server non è attivo o non è raggiungibile. In tal caso, il flag corrispondente a quel server nella lista self.server_flags viene impostato su False.

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

### Server
#### Connessione:
La funzione `socket_server` è responsabile per la creazione della socket TCP del server e l'avvio di un thread separato che rimarrà in ascolto per ricevere i comandi dal load balancer.
Creata la socket, il server la collega a un indirizzo IP e una porta specifici utilizzando il metodo `bind`.
Dopo aver effettuato il binding della socket, il server la mette in ascolto, utilizzando il metodo `listen`, così che sia pronto ad accettare le connessioni in arrivo dai client sulla porta specificata.

Successivamente, la funzione crea un thread separato chiamato `thread_gestione_client`, responsabile di rimanere in ascolto per le richieste provenienti dal load balancer e gestirle.
Quando il thread viene avviato, esegue il codice nel metodo `self.gestione_client`e, con il metodo il metodo `start()`, l'esecuzuione avviene in parallelo al thread principale del server.
Una volta avviato il thread di ascolto, la funzione socket_server termina.

#### Gestione del client:
La funzione `gestione_client` accetta le connessioni dei client e avvia un thread separato per gestire ciascun client.

La funzione è in attesa di accettare una connessione in entrata da un client tramite `server_socket.accept()`e, quando una connessione viene accettata, restituisce una nuova socket `client_socket` e l'indirizzo IP del client `client_ip`.

Accettata una connessione da un client , la funzione avvia un nuovo thread responsabile di gestire tutte le comunicazioni tra il server e il client specifico.
Il thread viene creato utilizzando la funzione `richieste_client`.

#### Gestione delle richieste: 
La funzione `richieste_client` gestisce la comunicazione tra il server e il client: riceve comandi dal client tramite il `client_socket`, li elabora eseguendoli e invia le risposte al client.

Ricevuta le richiesta, viene effettuato un controllo per verificare la ricezione dei dati . Se non sono stati ricevuti comandi nuovi, la funzione esce dal ciclo e termina.
Una volta ricevuto un comando dal client, la funzione lo decodifica e procede ad elaborarlo.
La funzione chiama il metodo `esegui_comandi` per eseguire il comando ricevuto e memorizza il risultato dell'elaborazione in una variabile `risultato`.
Il risultato viene convertito in una stringa ed inviato al client utilizzando il metodo `sendall()` del client_socket. 
La funzione continua a rimanere in attesa di ulteriori comandi dallo stesso client fintanto che la connessione non viene chiusa dal client o dal server (client o server).

#### Esecuzione dei comandi:
La funzione `esegui_comandi` genera A e B, numeri interi generati casualmente tra 1 e 50, esegue un'operazione matematica specificata dal comando ricevuto dal client ("somma", "sottrazione", "moltiplicazione" o "divisione") e restituisce un dizionario che contiene i valori di `A`, `B`, il comando (`operazione`) e il `risultato` dell'operazione.
Il dizionario creato viene restituito come risultato della funzione. 

Dopo aver avviato il thread per gestire il client corrente, utilizzando la funzione `richieste_client`, la funzione torna indietro e continua ad ascoltare nuove connessioni dai client.
Poiché ogni client ha il proprio thread dedicato, il server può gestire più client contemporaneamente.

Quando un client si disconnette o viene chiusa la connessione con il client, il thread termina.
Questo ciclo di ascolto e gestione dei client continua fino a quando il server è in esecuzione.

## Future Implementazioni

### Modificare il numero di treath:
Per garantire un funzionamento efficiente del sistema in scenari con un numero crescente di client, è fondamentale configurare un numero adeguato di thread per gestire le diverse attività. Quando il sistema è soggetto a un carico elevato, si consiglia di allocare sei thread distinti, ciascuno dedicato a specifiche responsabilità:

1. **Thread di Accettazione Client:** Questo thread è responsabile dell'accettazione delle connessioni in ingresso dai client. Si mette in ascolto sulla porta del server e accetta le richieste di connessione dai client entranti.

2. **Thread di Accettazione Server:** Questo thread gestisce le connessioni tra il load balancer e i server. Si mette in ascolto per stabilire connessioni con i server disponibili.

3. **Thread di Accettazione Richieste Client-Server:** Questo thread è incaricato di accettare e gestire le richieste inviate dai client ai server. Riceve le richieste dai client attraverso il load balancer e le inoltra ai server appropriati.

4. **Thread di Invio Richieste dal Load Balancer ai Server:** Questo thread è responsabile dell'inoltro delle richieste dai client ai server. Riceve le richieste dal thread di accettazione delle richieste client-server e le instrada verso i server in base all'algoritmo di bilanciamento del carico.

5. **Thread di Ricezione Richieste dai Server al Load Balancer:** Questo thread riceve le risposte dai server dopo aver elaborato le richieste. Le risposte vengono quindi instradate verso il load balancer per essere inviate ai client corrispondenti.

6. **Thread di Invio Risposte dai Server al Load Balancer ai Client:** Questo thread si occupa dell'inoltro delle risposte dai server al load balancer e, successivamente, al client corretto. Assicura che le risposte siano recapitate ai client in modo efficiente.

7. **Thread di Monitoraggio:** E' possibile creare un thread di monitoraggio che supervisioni lo stato del sistema. Questo thread può raccogliere metriche, gestire errori e garantire che il sistema funzioni in modo affidabile.

Configurando correttamente questi sei thread, il sistema sarà in grado di gestire simultaneamente numerose richieste dai client in modo efficiente e scalabile, garantendo prestazioni ottimali anche in situazioni di carico elevato. 
