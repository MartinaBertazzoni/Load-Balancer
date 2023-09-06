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

#### Avvio del client:
La funzione `avvio client` avvia e chiude tre thread:                                                  
 
                                                                                                                                                            

#### 1) Interfaccia: prende in imput  i comandi che devono essere eseguiti.
Con il metodo  `interfaccia_client` viene avviata un'interfaccia utente che permette agli utenti di inserire comandi manualmente o , digitando "random", generare comandi casuali (`crea_comando_random()`) e, in tal caso, comunicare il numero di richieste randomiche che devono essere create. Digitando "exit" sull'interfaccia, si ha la chiusura della connessione con il server.

Questi comandi vengono aggiunti alla lista di comandi da eseguire `self.comandi`.

2.thread che invia i comandi al load balancer
 3.thread che rimane in ascolto per ricevere le risposte delle richieste inviate
