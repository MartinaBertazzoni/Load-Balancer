# -*- coding: utf-8 -*-
"""
Schema client

Un thread mi gestisce l'interfaccia, in particolare comandi di STOP e numero di richieste
Un thread gestisce tutti gli altri processi

"""

def interfaccia_col_client():
    """
    Funzione che richiede comandi di input

    Returns
    -------
    None.

    """

def gestisci_richieste():
    """
    Funzione target del processo 2: crea le richieste, invia richieste, riceve richieste e le printa su terminale.
    Richiama funzioni:
        - invia comandi al server
        - crea_richieste random

    Returns
    -------
    None.

    """
    
def invia_richieste_al_loadbalancer():
    """
    Funzione che invia i comandi al server (connessione TCP e socket)

    Returns
    -------
    None.

    """
def crea_richieste_random():
    """
    Funzione che crea richieste di carico random e durata random 

    Returns
    -------
    None.

    """

def connetti_al_loadbalancer():
    """
    Funzione che crea la connessione con il load balancer (possiamo utilizzare connect oppure setsocketopt e bind)

    Returns
    -------
    None.

    """
def sconnetti_dal_load_balancer():
    """
    Funzione che chiude la connessione fra client e load balancer

    Returns
    -------
    None.

    """

def chiusura_richiesta():
    """
    Funzione che printa una notifica di chiusura della richiesta notificata dal loadbalancer

    Returns
    -------
    None.

    """


if __name__ == "__client2__":
    
    # creazione della variabile globale (deve essere una lista che contiene comandi di input
    # e deve essere inizializzata anche nelle funzioni: da verificare)

    
    # Creazione del processo 1 (interfaccia)
    # Creazione del processo 2 (ricevi e invia richieste)
    
    #Avvio con start e chiudo con join i processi
    
    
    
    
    
    pass
    
    

