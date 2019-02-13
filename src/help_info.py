"""
This module will be responsible for
providing help information on commands
"""

"""
AIUTO SOCIETA
    'creasocieta': "Crea una nuova societa e ti imposta come CEO. Costo: 1,000,000 Mem€.",
    'licenzia': "Rimuove i membri dalla societa. Solo il CEO può licenziare un executive.",
    'societa': "Mostra riguardo la tua societa.",
    'invita': "Invita l'utente selezionato nella societa` command.",
    'entrainsocieta': "Entra nella societa da te selezionata. Se la societa è privata, dovrai prima essere stato invitato.",
    'lasciasocieta': "Ti rimuove dalla tua societa attuale.",
    'promuovi': "Promuove un membro della societa. Se il membro era un trader semplice, verrà promosso a Executive. Se era Executive, verrà promosso a CEO (scambiando posto col CEO attuale)",
    'impostaprivato': "Imposta una societa come privata. Gli utenti potranno accedere solo usando il comando `!invita`.",
    'impostapubblico': "Imposta la societa come pubblica. Tutti gli utenti possono accedere",
    'upgrade': "Aumenta il livello della societa, così da aumentare il numero di utenti che possono farne parte. Costa 4 milioni Mem€ per aumentare al livello 2, 16M per il livello 3, 64 per il livello 4 e così via.",
"""

help_dict = {
    'attivi': "Mostra una lista di tutti gli investimenti attivi.",
    'saldo': "Mostra il tuo saldo in Mem€.",
    'bancarotta': "Se hai meno di 100 Mem€, questo comando portera il tuo saldo a 100.",
    'crea': "Crea il tuo conto.",
    'aiuto': "Mostra un aiuto.",
	'investi': "Investi l'ammontare specificato di Mem€ in uno specifico post. A seconda dell'ammontare di upvotes del post, dopo 4 ore potrai ricevere o perdere il tuo investimento.",
    'mercato': "Mostra delle statistiche sul mercato.",
    'template': "Permette a OP di specificare il link del template che verrà inserito nel messaggio sticky del post.",
    'top': "Mostra i migliori investitori.",
    'versione': "Mostra quando è stata installata la versione corrente del bot."
}
