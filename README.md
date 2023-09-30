# Sistema di Bilanciamento del Carico per Server di Calcolo
***
Questo repository contiene un'implementazione in Python di un sistema client-server intermediato da un sistema di load balacing. Il load balancer sfrutta l'algoritmo di bilanciamento del carico Round Robin, che assegna in maniera sequenziale le richieste ai server ad esso collegati che risultano attivi. 

## Introduzione
Questo programma implementa un sistema di File Transfer Protocol (FTP) client-server intermediato da un server di load balacing utilizzando Python. Per fare ciò utilizza tre classi: client, loadBalancer e server. Il client effettua delle richieste di invio file al load balancer, il quale li invia ai server sfruttando l'algoritmo di bilanciamento del carico Round Robin. Questo algoritmo assegna le richieste in maniera sequenziale ai server ad esso collegati e che risultano attivi e non in sovraccarico nella sessione. Infine, il load balancer riceve le risposte dai server e le reindirizza al client.

## Descrizione dell'architettura
L'architettura prevede l'utilizzo di un client, un load balancer e tre server FTP (File Transfer Protocol). Il `client` richiede in input un comando da eseguire; se viene digitato il comando "FTP", e viene successivamente inserito il numero di file, questi vengono scelti randomicamente tra i file contenuti nella cartella `file` e inviate al load balancer. Il `loadbalancer` riceve file JSON, li inserisce in una coda e invia ai server che risultano essere disponibili alla recezione; per verificare la disponibilità dei server effettua precedentemente un monitoraggio di connessione e di carico con i server ad esso collegati. Le richieste vengono assegnate utilizzando l'algoritmo di bilanciamento del carico Round Robin: il load balancer invia richieste ai server in maniera sequenziale. Quindi, i `server` attivi che non sono in sovraccarico, ricevono i file dal loadbalancer, li salvano all'interno della cartella `json_files_1` e inviano la risposta di avvenuta ricezione dei file al loadbalancer, che la inoltra al client. 

Il sistema permette quindi una gestione dinamica dei server: il load balancer tiene traccia dei server attivi e inattivi in ogni sessione, per inviare le richieste solo a quelli connessi. Con la stessa logica, il sistema appare altamente tollerante ai guasti, in quanto la disconnessione improvvisa di un server non causa interruzioni nell'invio delle richieste a quelli funzionanti.  

Inoltre, il sistema, attraverso un thread separato, monitora continuamente il carico della cpu del server e, se la memoria virtuale utilizzata dal processo supera il limite imposto, viene inviato un byte che rappresenta lo stato di sovraccarico al client e il loadbalancer inoltra le richieste al server successivo nell' ordine circolare, come stabilito dall'algoritmo di bilanciamento del carico. 
Per simulare una situazione di sovraccarico per i server, se il tipo di richiesta è "file_di_testo", il server estrae il titolo e il contenuto dal file JSON e conta il numero di lettere "A" nel contenuto.

## Funzionamento
Abbiamo 5 file: `clientFTP.py`, `loadBalancerFTP.py`, `serverFTP1.py`, `serverFTP2.py' e `serverFTP3.py`. 

### Client:
Il file `clientFTP.py` contiene la classe `client` con tutti i metodi per consentire la comunicazione delle richieste e delle rispettive risposte con il load balancer. Il suo scopo principale è consentire agli utenti di interagire con un server FTP per eseguire operazioni di upload e download di file tra il client e il server remoto. 
 
* **Inizializzazione del Client:**
Il client viene inizializzato con l'indirizzo IP e la porta del load balancer sui quali il client si connetterà, un percorso del file da inviare, una lista utilizzata per memorizzare i file che il client desidera inviare al server e un attributo utilizzato per tenere traccia del numero di richieste effettuate dal client.
* **Avvio del client:**
La funzione **`avvio_client`**, è utilizzata per avviare il socket del client, che sarà utilizzato per stabilire una connessione con il load balancer, e i seguenti thread associati alle diverse operazioni:
  1. **Interfaccia:** La funzione **`interfaccia_utente`** consente l'interazione dell'utente con il cliant. In questa parte di codice è stata impiegata la funzione `time.sleep(1)` per aggiungere un ritardo tra le iterazioni del ciclo, evitando un loop troppo veloce. Il metodo entra in un ciclo infinito che permette all'utente di inserire comandi in modo continuo fino a quando non viene inserito il comando "exit" per chiudere la connessione. Nello specifico, vengono elencati i file che possono essere selezionati per il trasferimento ai server nella cartella "file".
Se la cartella non contiene file, il codice genera un'eccezione con il messaggio di errore *"La cartella non ha file al suo interno."* e interrompe il programma.
Se la cartella contiene file, l'utente viene invitato a inserire un comando tramite *input(" Digita il comando: ")*:
 Se l'utente inserisce il comando "exit", il client mostra il messaggio di chiusura della connessione *"Chiusura della connessione con il server..."* e termina il programma.
Se l'utente inserisce il comando "FTP", tramite il messaggio *"Inserisci il numero di file da trasferire: "*, viene richiesto di inserire il numero di file da trasferire `numero_file`. I file vengono selezionati casualmente.Se viene generata un'eccezione durante l'input del numero di file o se l'utente inserisce un comando diverso da "exit" o "FTP," viene visualizzato il messaggio di errore e l'utente viene invitato a riprovare.

     - **Selezione dei file da inviare:** Il metodo **`scegli_file_da_inviare`** ha lo scopo di selezionare e creare una lista di file da inviare ai server FTP.
Infatti, viene eseguito un loop for che itera per il numero di volte specificato da `numero_file` e, durante ogni iterazione, la funzione chiama il metodo **`scegli_file_random`** per selezionare casualmente un file dalla lista dei file disponibili nella cartella. In seguito, viene composto il percorso completo del file selezionato concatenando `"./file/"` con il nome del file. Questo percorso viene memorizzato nella variabile `filepath` che viene aggiunta alla lista `file_da_inviare` contenente i file da inviare ai server.

  2. **Invio dei comandi al load balancer:** la funzione **`invia_file_al_loadbalancer`** è responsabile dell'invio di file JSON al load balancer. 
Il metodo utilizza un ciclo while infinito per continuare a inviare file al load balancer finché ci sono file nella lista `file_da_inviare`.
All'interno del ciclo, il metodo controlla se la lista non è vuota. Se la lista contiene file da inviare, viene estratto dalla lista il percorso del primo file da inviare, che viene poi rimosso.
Quindi, il metodo chiama la funzione **`invia_file_scelto`** che, apre il file JSON specificato da filepath, ne legge il contenuto, lo converte in un dizionario e gli aggiunge una chiave "request_type" assegnandogli il valore `file_di_testo` per identificare il tipo di richiesta, converte il dizionario aggiornato in una stringa JSON in modo da poterlo inviare tramite una socket e invia la stringa JSON codificata in byte attraverso la socket del client. 
Dopo l'invio del file, il metodo attende brevemente con time.sleep(0.3) per evitare problemi di sovrapposizione nell'invio di file successivi.
Infine, la funzione stampa un messaggio indicando che il file JSON è stato inoltrato con successo al load balancer e incrementa il contatore delle richieste `counter_richieste`.
Se si verifica un errore di comunicazione durante l'invio, viene catturata un'eccezione di tipo socket.error e viene stampato un messaggio di errore e programma viene quindi terminato.

* **Ricezione delle risposte dei server dal loadbalancer:**
La funzione `ricevi_dati_dal_loadbalancer` entra in un ciclo while infinito che mantiene la socket del client in ascolto per ricevere messaggi dal load balancer come sequenze di byte. Tale sequenza viene decodificata convertendo così i dati in una stringa leggibile. Inoltre, viene decrementato il contatore delle richieste `counter_richieste` di uno per tenere traccia del fatto che è stata ricevuta una risposta. Infine, la stringa leggibile vine stampata.
Il ciclo while continua ad ascoltare per ulteriori messaggi dal load balancer finché non si verifica un errore di socket o finché il programma non viene interrotto.


### Loadbalancer:
Il file `LoadbalancerFTP.py` contiene una classe denominata `LoadBalancer`, che implementa un load balancer in ascolto per connessioni in arrivo dai client.

* **Inizializzazione del Load Balancer:**
  Nell'inizializzazione, vengono configurati parametri come la porta `self.port`, l'indirizzo IP `self.ip`, le liste dei server disponibili, le code delle richieste e i thread di monitoraggio. Il log delle attività viene registrato in un file chiamato "loadbalancer.log".

* **Avvio del Load Balancer:**
Il metodo **`avvio_loadbalancer`** è responsabile dell'avvio del load balancer. La sua funzione principale è quella di inizializzare e configurare il load balancer, creando la socket e connettendo il load balancer ai client. Vengono così chiamati i seguenti metodi:
     - **`creo_socket_loadBalancer:`**
       Questa funzione crea una socket di tipo IPv4 e di tipo TCP che viene associata all'indirizzo IP `self.ip` e alla porta `self.port` specificati, per essere messa in modalità "ascolto". In tal modo il load balancer può accettare le connessioni in entrata dai client e viene stampato il messaggio *"Server di load balancing in ascolto su {self.ip}:{self.port}".
     - **`connetto_il_client:`**

#### Arresto: chiusura del load balancer in modo controllato.
La funzione `shutdown` assicura che tutte le connessioni siano chiuse in modo pulito e che tutte le attività in corso siano terminate prima che il programma del load balancer venga terminato. Questo contribuisce a evitare problemi di perdita di dati o connessioni incomplete durante la chiusura del load balancer.

Se, atraverso il flug `shutdown_event`, è stata richiesta la chiusura del load balancer, non è necessario eseguire ulteriori operazioni. Se, viceversa, la chiusura non è ancora stata richiesta, la funzione procede con la chiusura del load balancer. 

Per prima cosa, chiude la socket del load balancer, `self.balancer_socket`, se è stata creata. Questo assicura che il load balancer smetta di accettare nuove connessioni dai client.
Successivamente, chiude tutte le connessioni attive con i client che sono stati aggiunti alla lista `self.active_clients`. Questo garantisce che tutte le connessioni con i client vengano chiuse correttamente prima della chiusura del load balancer.

La funzione poi esegue un ciclo per attendere che tutti i thread attivi, tranne il thread principale, vengano completati.                                       
La funzione `threading.enumerate()` viene utilizzata per ottenere l'elenco di tutti i thread attivi, e quelli che non sono thread principali e non sono in modalità daemon vengono attesi e chiusi.

Infine, una volta che tutti i thread sono stati chiusi e il processo di chiusura è completo, la funzione emette un messaggio di conferma, indicando che il load balancer è stato chiuso correttamente.

#### Connessione tra LoadBalancer e Server
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

### Sistema di tracciamento delle richieste: Memorizzazione delle Richieste e Accesso da Parte del Server

In un sistema distribuito in cui il LoadBalancer svolge un ruolo critico nell'indirizzare le richieste dei client ai server appropriati, è importante disporre di meccanismi adeguati per tenere traccia delle richieste effettuate e dei loro dettagli. Questo consente una gestione più efficace delle operazioni, nonché una risoluzione più efficiente dei problemi o degli errori che potrebbero verificarsi.

Per implementare questa funzionalità, devono essere effettuate le seguenti modifiche al codice:
