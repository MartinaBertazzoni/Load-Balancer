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
       Questa funzione crea una socket di tipo IPv4 e di tipo TCP che viene associata all'indirizzo IP `self.ip` e alla porta `self.port` specificati, per essere messa in modalità "ascolto". In tal modo il load balancer può accettare le connessioni in entrata dai client e viene stampato il messaggio *"Server di load balancing in ascolto su {self.ip}:{self.port}"*.
     - **`connetto_il_client:`**
       Questo metodo gestisce la connessione tra il load balancer e i client. È responsabile dell'accettare le connessioni in arrivo dai client, avviare un thread separato per la ricezione dei file dal client e un altro thread per gestire la coda delle richieste in arrivo.
Nello specifico, il metodo utilizza un loop while True per continuare a ricevere connessioni dai client.
Quando una connessione in arrivo viene accettata, il `client_socket` e il `client_ip` vengono registrati, la connessione accettata viene aggiunta alla lista `clients` e viene visualizzato il messaggio che indica la connessione accettata.
Un thread denominato `ricezione_file` viene creato per gestire la ricezione dei file dal client e un altro thread viene creato per gestire la coda delle richieste in arrivo dai client. I due thread chiamano rispettivamente i metodi:

       1. **Ricezione dei File dal Client:** Il metodo **`ricevo_file_dal_client`** utilizza un loop while True per rimanere in attesa di dati in arrivo dal client attraverso la socket. Il load balancer può ricevere fino a 4096 byte di dati come stringa codificata `file_ricevuto`, dal client.
La funzione verifica se la stringa è vuota. In tal caso il client ha chiuso la connessione, quindi il loop viene interrotto con break.
Se la stringa contiene dati, viene decodificata da JSON in un dizionario Python, convertendo il contenuto del file inviato dal client in una struttura dati utilizzabile.
Dal dizionario viene estratto il valore del campo `titolo`, che viene aggiunto alla lista `nomi_file_ricevuti` per tenere traccia dei titoli dei file ricevuti. Viene quindi visualizzato un messaggio che indica il titolo del file ricevuto.
Infine, viene cretata una tupla contenente il socket del client, il dizionario file e il titolo del file, e questa tupla viene inserita nella coda delle richieste `request_queue`. 

          La coda delle richieste è un componente critico nel sistema di bilanciamento del carico FTP, poiché consente una gestione efficiente, ordinata e asincrona delle richieste dei client e dei file associati, migliorando le prestazioni complessive del sistema.
 
       2. **Gestione della Coda delle Richieste:** Il metodo **`process_request_queue`** viene eseguito in un ciclo infinito per consentire al load balancer di continuare a elaborare richieste in arrivo da clienti in modo continuo. All'interno del ciclo, il metodo estrae il primo elemento dalla coda delle richieste Questo blocca l'esecuzione finché non è disponibile almeno un elemento nella coda. Una volta disponibile, il metodo estrae tre valori:
          - client_socket: la socket associata al client che ha inviato la richiesta.
          - file: i dati del file da inviare ai server, rappresentati come un dizionario.
          - titolo: il titolo del file ricevuto dalla richiesta.
            
          Dopo aver estratto questi dati, il metodo introduce una breve pausa di 0.2 secondi, utile per evitare il sovraccarico del server e dei client durante l'elaborazione continua delle richieste.
In fine, la funzione procede con l'invio dei file JSON:

* **Invio ai Server:**
I file JSON vengono inviati ai server selezionati utilizzando l'algoritmo di bilanciamento del carico Round Robin. A tal proposito, sono resposabili le funzioni:
  
  + **`invia_ai_server`:** Questo metodo si occupa di instradare una richiesta di un client al server appropriato in base all'algoritmo Round Robin. Nello specifico, il metodo ottiene l'indirizzo IP e la porta del server scelto dall'algoritmo di bilanciamento del carico Round Robin; stampa a schermo il messaggio *"Server scelto"* seguito dalla porta del server selezionato; registra l'evento nel file di log `loadbalancer.log`, indicando quale client sta inoltrando la richiesta e quale server riceverà la richiesta; effettua l'effettivo invio del file al server selezionato.

  + **`invia_al_server_scelto`:** Questo metodo si occupa di connettersi al server selezionato e inviare il contenuto del file JSON. Nello specifico, crea una nuova socket `server_socket` per la comunicazione con il server selezionato; incrementa il numero della richiesta elaborata `numero_della_richiesta` per tener traccia delle richieste inoltrate e lo stampa; aggiunge tale nuemro al dizionario `file` con la chiave `numero_richiesta` per identificare univocamente la richiesta; stampa il messaggio *"Ho inviato il file al server{server_port} status: "* ; invia il file JSON codificato al server e chiude la connessione con esso.
 
* **Monitoraggio dei Server:** Il monitoraggio dei server viene effettuato con un thread separato che consente di controllare lo stato di connessione dei server, quindi se sono attivi o inattivi, e verifica se sono sovraccarichi o meno. Tale monitoraggio è fondamentale per il funzionamento efficace del load balancer, poiché consente di instradare le richieste solo verso i server disponibili e non sovraccaricati. A tal proposito, svolgono un ruolo fondamentale le funzioni:

  + **`monitoraggio_stato_server`:**
    Il metodo è implementato come un ciclo infinito in modo che continui costantemente a monitorare lo stato dei server. Il ciclo viene iterato su tutti i server di destinazione della lista `servers` e, per ciascun server, viene creato un oggetto socket `server_socket` di tipo TCP che verrà utilizzato per provare a stabilire una connessione con il server.
Viene impostato un timeout di 1 secondo per la connessione affichè, se la connessione non riesce entro 1 secondo, verrà sollevata un'eccezione.
Viene quindi effettuato un tentativo di connessione al server e, se la connessione non riesce,  il server è considerato inattivo e non può servire le richieste dei client. Pertanto, la bandiera corrispondente a quel server nell'elenco `server_flags_connection` viene impostata su False.
Se la connessione ha successo, il server è considerato attivo e funzionante. In questo caso, la bandiera corrispondente a quel server nell'elenco `server_flags_connection` viene impostata su True e il metodo chiama la funzione:

  + **`monitoraggio_carico_server`:**
    All'interno del metodo, viene creato un messaggio di richiesta di monitoraggio chiamato `messaggio_di_monitoraggio`. Questo messaggio è un dizionario con una chiave chiamata `request_type` impostata su `richiesta_status`.
Il messaggio di richiesta viene quindi convertito in una stringa JSON affinchè i dati vengano inviati attraverso la rete.
Successivamente, il metodo utilizza la socket `server_socket` per inviare il messaggio di richiesta di monitoraggio al server e attende una risposta da esso. La risposta è prevista come un singolo byte che viene convertito in un valore booleano (1 rappresenta True, 0 rappresenta False).
Infine, il valore booleano ottenuto dalla risposta del server viene memorizzato nella lista `server_sovracarichi` all'indice i, dove True rappresenta lo stato di sovraccarico del server monitorato.
La socket viene quindi chiusa poiché la comunicazione è stata completata.

* **Bilanciamento del Carico --> Algoritmo di ROUND ROBIN:** 
La funzione **`round_robin`** è un metodo che implementa l'algoritmo di bilanciamento del carico Round Robin. L'obiettivo di questo metodo è selezionare il server successivo a cui inoltrare una richiesta da parte di un client, garantendo una distribuzione equa del carico tra i server disponibili. Il metodo si assicura che il server selezionato sia attivo e non sovraccarico prima di restituire la sua informazione di connessione. 
Il metodo utilizza un ciclo while True per continuare a cercare un server fino a quando non trova un server disponibile.
All'interno del ciclo, il metodo seleziona il prossimo server nell'ordine circolare utilizzando l'indice `current_server_index` che tiene traccia del server successivo da selezionare e fornisce l'indirizzo IP la porta del server.
Viene quindi verificato se il server selezionato è attivo (flag True) e non sovraccarico (flag False). Questo controllo è importante perché si desidera inviare la richiesta solo a server attivi e non sovraccarichi. Se il server selezionato soddisfa questi criteri, il ciclo viene interrotto utilizzando l'istruzione break.
Se il server selezionato non è attivo o è sovraccarico, l'indice viene incrementato in modo da passare al successivo nell'ordine.
Alla fine del ciclo, l'indice viene nuovamente incrementato in modo che il prossimo server venga selezionato alla successiva richiesta.

* **Ricezione delle Risposte dal Server:**
Il metodo **`ricevi_risposta_server`** ha lo scopo di ricevere le risposte inviate dal server al Load Balancer e quindi inoltrarle al client. Questo consente al Load Balancer di agire come intermediario tra il client e il server, garantendo che le risposte dal server raggiungano il client corretto.
All'interno del metodo, viene utilizzata una struttura try-except per gestire eventuali eccezioni che possono verificarsi durante la comunicazione con il server.
All'interno del blocco try, il metodo riceve fino a 1024 byte di dati dal server tramite la socket `server_socket` e li decodifica. Il risultato viene memorizzato nella variabile `message_from_server` e tale messaggio ricevuto dal server viene stampato sulla console.
Infine, il metodo invia il messaggio ricevuto dal server al client utilizzando la socket `client_socket`. In questo modo, il client riceverà la risposta dal server attraverso il Load Balancer.
All'interno del blocco except, vengono gestite eventuali eccezioni di socket, ad esempio se si verifica un errore durante la comunicazione con il server. In tal caso, viene stampato il messaggio di errore *"Impossibile ricevere dati dal server: {error}"* e il programma viene terminato.

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
