# Sistema di Bilanciamento del Carico per Server di Calcolo
Questo repository contiene un'implementazione in Python di un sistema client-server intermediato da un sistema di load balacing. Il load balancer sfrutta l'algoritmo di bilanciamento del carico Round Robin, che assegna in maniera sequenziale le richieste ai server ad esso collegati che risultano attivi. 
# Introduzione
Questo programma implementa un sistema client-server intermediato da un server di load balacing utilizzano Python. Per fare ciò utilizza tre classi: client, loadBalancer e server. Il client effettua delle richieste al load balancer, il quale le invia ai server sfruttando l'algoritmo di bilanciamento del carico Round Robin. Questo algoritmo assegna le richieste in maniera sequenziale ai server ad esso collegati e che risultano attivi nella sessione. Infine, il load balancer riceve le risposte dai server e le reindirizza al client.

# Descrizione dell'architettura
L'architettura prevede l'utilizzo di un client, un load balancer e tre server.
