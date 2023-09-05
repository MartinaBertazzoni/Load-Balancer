# Sistema di Bilanciamento del Carico per Server di Calcolo
Questo repository contiene un'implementazione in Python di un sistema client-server intermediato da un sistema di load balacing. Il load balancer sfrutta l'algoritmo di bilanciamento del carico Round Robin, che assegna in maniera sequenziale le richieste ai server ad esso collegati che risultano attivi. 
# Introduzione
Questo programma implementa un sistema client-server intermediato da un server di load balacing utilizzano Python. Per fare ciò utilizza tre classi: client, loadBalancer e server. Il client effettua delle richieste al load balancer, il quale le invia ai server sfruttando l'algoritmo di bilanciamento del carico Round Robin. Questo algoritmo assegna le richieste in maniera sequenziale ai server ad esso collegati e che risultano attivi nella sessione. Infine, il load balancer riceve le risposte dai server e le reindirizza al client.

# Descrizione dell'architettura
L'architettura prevede l'utilizzo di un client, un load balancer e tre server. Il client richiede in input un comando; se viene digitato il comando per effettuare richieste randomiche, e viene successivamente inserito il numero di richieste da effettuare, queste vengono scelte randomicamente all'interno di un set di operazioni pre-fissate e inviate al load balancer. Il load balancer invia le richieste ai server ad esso collegati e che risultano essere attivi; per verificare l'attività o l'inattività dei server effettua precedentemente un controllo sui server ad esso connessi. Le richieste vengono assegnate utilizzando l'algoritmo di bilanciamento del carico Round robin: il load balancer invia richieste ai server attivi in maniera sequenziale. In seguito, i server effettuano il calcolo richiesto e inviano la risposta al load balancer, il quale la inoltra al client. 

Il sistema permette quindi una gestione dinamica dei server: il load balancer tiene traccia dei server attivi e quelli inattivi in ogni sessione, per inviare le richieste solo ai server connessi. Con la stessa logica, il sistema appare altamente tollerante ai guasti, in quanto la disconnessione improvvisa di un server non causa interruzioni nell'invio delle richieste ai server funzionanti. 

Il load balancer tiene traccia delle attività di ogni sessione; in particolare, registra sul file loadbalancer.log le connessioni e le richieste effettuate. 

