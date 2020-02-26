import datetime
import time

import config
import utils

INVESTMENT_DURATION_VAR = utils.investment_duration_string(config.INVESTMENT_DURATION)

# This message will be sent if an account has been
# successfully created
CREATE_ORG = """
*Conto creato!*

Grazie %USERNAME% per aver creato un conto /r/BancaDelMeme!

Il tuo saldo iniziale è **%BALANCE% Mem€**.
"""


def modify_create(username, balance):
    return CREATE_ORG.\
        replace("%USERNAME%", str(username)).\
        replace("%BALANCE%", format(balance, ",d"))


# This message will be sent if a user tries to create an account but already
# has one.
CREATE_EXISTS_ORG = """
Non capisco se sei troppo entusiasta o stai cercando di truffarmi. Hai già un account!
"""

# This message will be sent when an investment
# was successful

INVEST_ORG = """
*%AMOUNT% Mem€ investiti @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

Il tuo investimento è ora attivo. Valuterò il tuo profitto in %TIME% e aggiornerò questo stesso commento. Non facciamo che ci perdiamo di vista!

Il tuo saldo attuale è **%BALANCE% Mem€**.
""".replace("%TIME%", INVESTMENT_DURATION_VAR).\
    replace("%UPVOTES_WORD%", utils.upvote_string())


def modify_invest(amount, initial_upvotes, new_balance):
    return INVEST_ORG.\
        replace("%AMOUNT%", format(amount, ",d")).\
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")).\
        replace("%BALANCE%", format(new_balance, ",d"))


INVEST_WIN_ORG = """
*%AMOUNT% Mem€ investiti @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Il tuo investimento è maturato. È andato alla grande! Hai guadagnato %PROFIT% Mem€ (%PERCENT%).

*%RETURNED% Mem€ restituiti @ %FINAL_UPVOTES% %UPVOTES_WORD%*

Il tuo nuovo saldo is **%BALANCE% Mem€**.
""".replace("%UPVOTES_WORD%", utils.upvote_string())

INVEST_LOSE_ORG = """
*%AMOUNT% Mem€ investiti @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Il tuo investimento è maturato. Non è andato bene! Hai perso %PROFIT% Mem€ (%PERCENT%).

*%RETURNED% Mem€ restituiti @ %FINAL_UPVOTES% %UPVOTES_WORD%*

Il tuo nuovo saldo is **%BALANCE% Mem€**.
""".replace("%UPVOTES_WORD%", utils.upvote_string())

INVEST_BREAK_EVEN_ORG = """
*%AMOUNT% Mem€ investiti @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Il tuo investimento è maturato. Sei andato in pari! Hai guadagnato %PROFIT% Mem€ (%PERCENT%).

*%RETURNED% Mem€ restituiti @ %FINAL_UPVOTES% %UPVOTES_WORD%*

Il tuo nuovo saldo is **%BALANCE% Mem€**.
""".replace("%UPVOTES_WORD%", utils.upvote_string())


def modify_invest_return(amount, initial_upvotes,
                         final_upvotes, returned,
                         profit, percent_str, new_balance):
    if profit > 0:
        original = INVEST_WIN_ORG
    elif profit < 0:
        original = INVEST_LOSE_ORG
        profit *= -1
    else:
        original = INVEST_BREAK_EVEN_ORG

    return original.\
        replace("%AMOUNT%", format(amount, ",d")).\
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")).\
        replace("%FINAL_UPVOTES%", format(final_upvotes, ",d")).\
        replace("%RETURNED%", format(returned, ",d")).\
        replace("%PROFIT%", format(profit, ",d")).\
        replace("%PERCENT%", format(percent_str)).\
        replace("%BALANCE%", format(int(new_balance), ",d"))


INVEST_CAPPED_ORG = """
*%AMOUNT% Mem€ investiti @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Il tuo investimento è maturato a %FINAL_UPVOTES% %UPVOTES_WORD%, con un profitto di %PROFIT% Mem€ (%PERCENT%).

**Congratulazioni,** hai raggiunto il saldo massimo! Hai trionfato in questa sanguinosa competizione nel marketplace, e il tuo portafoglio è gonfissimo! Le future generazioni ti ricorderanno come titano degli investimenti.

*"Alessandro pianse, poiché non c'erano altri mondi da conquistare.."* (...ancora)

Il tuo saldo attuale è **%BALANCE% Mem€** (il saldo massimo).
""".replace("%UPVOTES_WORD%", utils.upvote_string())


def modify_invest_capped(amount, initial_upvotes,
                         final_upvotes, returned,
                         profit, percent_str, new_balance):
    return INVEST_CAPPED_ORG.\
        replace("%AMOUNT%", format(amount, ",d")).\
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")).\
        replace("%FINAL_UPVOTES%", format(final_upvotes, ",d")).\
        replace("%PROFIT%", format(profit, ",d")).\
        replace("%PERCENT%", str(percent_str)).\
        replace("%BALANCE%", format(new_balance, ",d"))


# If funds are insufficient to make an investment
# say that
INSUFF_ORG = """
Non hai abbastanza Mem€ per fare questo investimento.

Il tuo saldo attuale è **%BALANCE% Mem€**.

Se hai meno di 100 Mem€ e nessun investimento in corso, prova ad inviare `!bancarotta`!
"""


def modify_insuff(balance_t):
    return INSUFF_ORG.\
        replace("%BALANCE%", format(balance_t, ",d"))


# Message if you are broke
BROKE_ORG = """
OOps, sei in bancarotta.

Il tuo saldo è stato resettato a 100 Mem€. Sta attento la prossima volta.

Sei andato in bancarotta %NUMBER% volte.
"""


def modify_broke(times):
    return BROKE_ORG.\
        replace("%NUMBER%", str(times))

# Message if you are broke and have investimenti attivi
BROKE_ACTIVE_ORG = """
Hai ancora %ACTIVE% investmento/i attivi.

Dovrai attendere che vengano completati.
"""


def modify_broke_active(active):
    return BROKE_ACTIVE_ORG.\
        replace("%ACTIVE%", str(active))

# Message if you are broke and have more than 100 Mem€
BROKE_MONEY_ORG = """
Non sei così povero! Hai ancora **%AMOUNT% Mem€**.
"""


def modify_broke_money(amount):
    return BROKE_MONEY_ORG.\
        replace("%AMOUNT%", format(amount, ",d"))

"""
COMANDI PER LE societa (BETA)
- `!societa` 
- `!creasocieta <name>`
- `!entrainsocieta <name>`
- `!lasciasocieta`
- `!promuovi <username>` **(Solo per i CEO e dirigenti)**
- `!licenzia <username>` **(Solo per i CEO and dirigenti)**
- `!upgrade` **(Solo per i CEO)**
- `!impostaprivato` **(Solo per i CEO)**
- `!impostapubblico` **(Solo per i CEO)**
- `!invita <username>` **(Solo per i CEO e dirigenti)**
"""

HELP_ORG = """
*Benvenuto su BancaDelMeme!*

Io sono un bot che vi aiuterà ad investire in *MEME* e farci una fortuna. Mica come le criptovalute.

Ecco una lista di tutti i comandi che funzionano con me:

### COMANDI GENERALI
- `!attivi` - Mostra gli investimenti attivi
- `!saldo` - Mostra quanti Mem€ si hanno ancora da spendere
- `!bancarotta` - Da usare se si scende sotto i 100 Mem€
- `!crea` - Crea un conto di investimento
- `!aiuto` - Mostra questo messaggio
- `!investi <quantità>` - Permette di investire i propri Mem€
- `!investitutto` - Permette di investire tutti i propri Mem€
- `!mercato` - Mostra il MeMercato Azionario attuale
- `!top` - Mostra i migliori investitori
- `!vendi` - Chiude in anticipo gli investimenti in quel topic (con penalità)
- `!versione` - Mostra la versione attuale del bot
- `!template https://imgur.com/...` **(solo per OP, utile per linkare i template)**

Per avere aiuto su un singolo comando, semplicemente scrivi `!aiuto`

Per altre informazioni e più dettagli,
fai riferimento alla [spiegazione estesa](https://www.reddit.com/r/BancaDelMeme/wiki/regolamento).
"""

BALANCE_ORG = """
Attualmente, il tuo saldo è **%BALANCE% Mem€**.

In investimenti hai %ACTIVES% Mem€ impegnati, per un patrimonio totale di %NET_WORTH% Mem€.
"""


def modify_balance(balance, net_worth):
    return BALANCE_ORG.\
        replace("%BALANCE%", format(balance, ",d")).\
        replace("%ACTIVES%", format(net_worth-balance, ",d")).\
        replace("%NET_WORTH%", format(net_worth, ",d"))


ACTIVE_ORG = """
Hai %NUMBER% investimenti attivi:

%INVESTMENTS_LIST%
"""


def modify_active(active_investments):
    if not active_investments:
        return "Non hai alcun investimento attivo al momento."

    investments_strings = []
    i = 1
    for inv in active_investments:
        seconds_remaining = inv.time + config.INVESTMENT_DURATION - time.time()
        if seconds_remaining > 0:
            td = datetime.timedelta(seconds=seconds_remaining)
            remaining_string = str(td).split(".")[0] + " rimanenti"
        else:
            remaining_string = "in elaborazione"
        post_url = f"https://www.reddit.com/r/BancaDelMeme/comments/{inv.post}/_/{inv.comment}"
        inv_string = f"[#{i}]({post_url}): {inv.amount:,d} Mem€ @ {inv.upvotes} %UPVOTES_WORD% ({remaining_string})"\
            .replace("%UPVOTES_WORD%", utils.upvote_string())
        investments_strings.append(inv_string)
        i += 1
    investments_list = "\n\n".join(investments_strings)

    return ACTIVE_ORG.\
        replace("%NUMBER%", str(len(active_investments))).\
        replace("%INVESTMENTS_LIST%", investments_list)


MIN_INVEST_ORG = """
L'investimento minimo consentito è di 100 Mem€ o di %MIN% (1% del tuo saldo); il più alto dei due.
"""


def modify_min_invest(minim):
    return MIN_INVEST_ORG.\
        replace("%MIN%", format(int(minim), ",d"))


MARKET_ORG = """
Il mercato, in questo momento, ha **%NUMBER%** investimenti attivi.

Tutti gli investitori possiedono **%MONEY% Mem€**.

Ci sono **%HODL% Mem€** in circolazione su investimenti al momento.
"""


def modify_market(inves, cap, invs_cap):
    return MARKET_ORG.\
        replace("%NUMBER%", format(int(inves), ",d")).\
        replace("%MONEY%", format(int(cap), ",d")).\
        replace("%HODL%", format(int(invs_cap), ",d"))


# Message used for !top command
TOP_ORG = """
Gli investitori con il valore netto più alto (saldo + investimenti attivi): 

%TOP_STRING%
"""


def modify_top(leaders):
    top_string = ""
    for leader in leaders:
        top_string = f"{top_string}\n\n{leader.name}: {int(leader.networth):,} Mem€"

    top_response = TOP_ORG
    top_response = top_response.replace("%TOP_STRING%", top_string)
    return top_response


DELETED_COMMENT_ORG = """
Dov'è finito?

Comunque, l'investimento è andato perduto.
"""

TEMPLATE_HINT_ORG = """
---

Psst, %NAME%, puoi scrivere `!template https://imgur.com/...` per pubblicare il template del tuo post! Alla fine è uno degli scopi di BancaDelMeme! ;)
"""

INVEST_PLACE_HERE_NO_FEE = """
**GLI INVESTIMENTI VANNO QUI - SOLO LE RISPOSTE DIRETTE A QUESTO MESSAGGIO VERRANNO ELABORATE**

Per prevenire spam e altri catastrofi naturali, considero solamente risposte a questo messaggio. Altri comandi verranno ignorati e potrebbero addirittura venire penalizzati. Teniamo il nostro MeMercato Azionario bello pulito!

---

- Visita [BancaDelMeme](/r/BancaDelMeme) per aiuto, statistiche di MeMercato Azionario, e profili degli investitori.

- Nuovo utente? Ti senti perso e confuso? Rispondi `!aiuto` a questo messaggio, o visita la pagina [Wiki](https://www.reddit.com/r/BancaDelMeme/wiki/index) per una spiegazione più dettagliata.
"""


def invest_no_fee(name):
    return INVEST_PLACE_HERE_NO_FEE + TEMPLATE_HINT_ORG.\
        replace("%NAME%", name)


INSIDE_TRADING_ORG = """
Non puoi investire nei tuoi stessi meme! Non è consentito fare insider trading!
"""


def modify_grant_success(grantee, badge):
    return f"Badge assegnato con successo `{badge}` a {grantee}!"


def modify_grant_failure(failure_message):
    return f"Oops, Non ho potuto assegnare il badge ({failure_message})"


NO_ACCOUNT_POST_ORG = """
Hai bisogno di creare un account per postare un meme. Per favore, rispondi ad uno dei miei commenti con `!crea`.

Per avere più informazioni, scrivi `!aiuto`
"""

PAY_TO_POST_ORG = """
Date le ultime regolamentazioni di mercato, per postare un meme dovrai pagare una tassa del 6% con un minimo di 250 Mem€.

Se non puoi permettertelo, il tuo post verrà cancellato. Nulla di personale, barbùn. Sono le regole di MeMercato Azionario.

Fatti risentire quando avrai più soldi, rimanda il meme con un nuovo post.

Il tuo saldo attuale è **%MEMECOINS% Mem€**.
"""


def modify_pay_to_post(balance):
    return PAY_TO_POST_ORG.\
        replace("%MEMECOINS%", format(int(balance), ",d"))


MAINTENANCE_ORG = """
**Il bot è in manutenzione per ragioni tecniche.**

**Dovrebbe tornare online a breve. (Qualche ora)**

**Ci scusiamo per ogni disagio causato.**
"""

firm_none_org = """
Non ti trovi in una societa.

Puoi crearne una con il comando **!creasocieta <NOME societa>**, oppure richiedere di accedere ad una esistente con il comando **!entrainsocieta <NOME societa ESISTENTE>**.
"""

firm_other_org = """
# %FIRM_NAME%

BILANCIO societa: **%BALANCE%** Mem€

Livello di tasse: **%TAX%%**

Dimensione: **%MEMBERS% membri**

Livello: **%LEVEL%**
"""


def modify_firm_other(firm):
    return firm_other_org.\
        replace("%FIRM_NAME%", firm.name).\
        replace("%FIRM_ID%", str(firm.id)).\
        replace("%BALANCE%", "{:,}".format(firm.balance)).\
        replace("%TAX%", str(firm.tax)).\
        replace("%MEMBERS%", str(firm.size)).\
        replace("%LEVEL%", str(firm.rank + 1))


firm_self_org = """
societa: **%FIRM_NAME%**

Livello di tasse: **%TAX%%**

Dimensione: **%MEMBERS% membri**

Livello: **%LEVEL%**

Il tuo livello: **%RANK%**

Puoi lasciare questa societa con il comando **!escidallasocieta**.
"""


def modify_firm_self(rank, firm):
    rank_str = rank_strs[rank]
    return firm_self_org.\
        replace("%RANK%", rank_str).\
        replace("%FIRM_NAME%", firm.name).\
        replace("%FIRM_ID%", str(firm.id)).\
        replace("%BALANCE%", "{:,}".format(firm.balance)).\
        replace("%TAX%", str(firm.tax)).\
        replace("%MEMBERS%", str(firm.size)).\
        replace("%LEVEL%", str(firm.rank + 1))


firm_notfound_org = """
Nessuna societa trovata con questo nome.
"""

rank_strs = {
    "ceo": "CEO",
    "coo": "COO",
    "cfo": "CFO",
    "exec": "Dirigente",
    "assoc": "Associato",
    "": "Trader semplice"
}

createfirm_exists_failure_org = """
Sei già all'interno di questa societa: **%FIRM_NAME%**

Per favore, esci usando il comando *!escidallasocieta*, prima di accedere in una nuova societa.
"""

createfirm_cost_failure_org = """
Creare una societa costa 1,000,000 Mem€, e tu sei un poveraccio. Vai a fare della grana, e fatti rivedere solo quando ne avrai abbastanza.
"""


def modify_createfirm_exists_failure(firm_name):
    return createfirm_exists_failure_org.\
        replace("%FIRM_NAME%", firm_name)


createfirm_format_failure_org = """
I nomi delle societa devono avere tra 4 e 32 caratteri. Sono consentiti solo caratteri alfanumerici, spazi, trattini medi e bassi (- e _)
"""

createfirm_nametaken_failure_org = """
Il nome scelto per la societa è già in uso. Se non stai tentando di organizzare una truffa finanziaria, per favore riprova.
"""

createfirm_org = """
La nuova societa è stata creata correttamente, sto chiamando il notaio.

Tu sei il CEO della societa e hai il potere di
"""

nofirm_failure_org = leavefirm_none_failure_org = """
Non sei in una societa.
"""
no_firm_failure_org = leavefirm_none_failure_org

leavefirm_ceo_failure_org = """
Al momento sei il CEO della tua societa, quindi non ti è permesso andartene. Non fare lo schettino della finanza.

Se davvero vuoi andartene, dovrai prima rinunciare al tuo ruolo. Per farlo dovrai promuovere un dirigente al ruolo di CEO col comando **!promuovi <username>**.
"""

leavefirm_org = """
Sei uscito dalla societa.
"""

not_ceo_org = """
Solo il CEO può farlo.
"""

not_ceo_or_coo_org = """
Solo il CEO o il COO può farlo.
"""

not_ceo_or_cfo_org = """
Solo il CEO o il CFO può farlo.
"""

not_ceo_or_exec_org = """
Solo il CEO o un dirigente può farlo.
"""

not_assoc_org = """
I trader semplici non possono mandare inviti
"""

promote_failure_org = """
Non sono riuscito a promuovere l'utente, assicurati che sia corretto (o che non sia un prestanome).
"""

promote_coo_full_org = """
Non ho potuto promuovere questo impiegato, poiché la societa ha già un COO
"""

promote_cfo_full_org = """
Non ho potuto promuovere questo impiegato, poiché la societa ha già un CFO
"""

promote_execs_full_org = """
Non ho potuto promuovere questo impiegato, poiché la societa è alla sua capacità di dirigenti massima. 
**Numero di dirigenti:** %EXECS%
**Livello societa:** %LEVEL%

Il CEO della societa può aumentare il livello col comando `!upgrade`.
"""


def modify_promote_execs_full(firm):
    return promote_execs_full_org.\
        replace("%EXECS%", str(firm.execs)).\
        replace("%LEVEL%", str(firm.rank + 1))


promote_assocs_full_org = """
Non ho potuto promuovere questo impiegato, poiché la societa è alla sua capacità di associati massima. 
**Numero di associati:** %ASSOCS%
**Livello societa:** %LEVEL%

Il CEO o il CFO della societa possono aumentare il livello col comando `!upgrade`.
"""


def modify_promote_assocs_full(firm):
    return promote_assocs_full_org.\
        replace("%ASSOCS%", str(firm.assocs)).\
        replace("%LEVEL%", str(firm.rank + 1))


promote_org = """
 Promosso con successo! **/u/%NAME%**, da **%OLDRANK%** a **%NEWRANK%**.
"""


def modify_promote(user, old_role):
    return promote_org.\
        replace("%NAME%", user.name).\
        replace("%OLDRANK%", rank_strs[old_role]).\
        replace("%NEWRANK%", rank_strs[user.firm_role])


demote_failure_org = """
Failed to demote user, make sure you used the correct username.
"""

demote_failure_trader_org = """
Failed to demote user, they are already a Floor Trader. Use `!fire <username>` if you would like to remove them from the firm.
"""

demote_cfo_full_org = """
Could not demote this employee since the firm already has a CFO.
"""

demote_execs_full_org = """
Could not demote this employee since the firm is at its maximum executive limit.
**Number of executives:** %EXECS%
**Firm level:** %LEVEL%

The CEO or CFO of the firm can raise this limit by upgrading with `!upgrade`.
"""


def modify_demote_execs_full(firm):
    return demote_execs_full_org.\
        replace("%EXECS%", str(firm.execs)).\
        replace("%LEVEL%", str(firm.rank + 1))


demote_assocs_full_org = """
Could not demote this employee since the firm is at its maximum associate limit.
**Number of associates:** %ASSOCS%
**Firm level:** %LEVEL%

The CEO or CFO of the firm can raise this limit by upgrading with `!upgrade`.
"""


def modify_demote_assocs_full(firm):
    return demote_assocs_full_org.\
        replace("%ASSOCS%", str(firm.assocs)).\
        replace("%LEVEL%", str(firm.rank + 1))


demote_org = """
Successfully demoted **/u/%NAME%** from **%OLDRANK%** to **%NEWRANK%**.
"""


def modify_demote(user, old_role):
    return demote_org.\
        replace("%NAME%", user.name).\
        replace("%OLDRANK%", rank_strs[old_role]).\
        replace("%NEWRANK%", rank_strs[user.firm_role])


fire_org = """
Licenziato con successo **/u/%NAME%** dalla societa.
"""


def modify_fire(user):
    return fire_org.\
        replace("%NAME%", user.name)


fire_failure_org = """
Non sono riuscito a cacciare l'utente, assicurati di aver scritto il nome correttamente, o che non abbia intestato a prestanomi il suo conto.
"""

joinfirm_exists_failure_org = """
Non puoi unirti ad una societa perché sei già all'interno di un'altra.  
Utilizza il comando *!escidallasocieta* per lasciare la societa prima di unirti ad una nuova.
"""

joinfirm_private_failure_org = """
Impossibile unirsi a questa societa perché è privata e non sei stato invitato alla festa.

Il CEO o gli Executives devono prima invitarti col comando `!invita <username>`.
"""

joinfirm_failure_org = """
Non riesco a trovare la societa che hai inserito. Che cazzo di truffa stai organizzando? Scrivi meglio il nome e riprova
"""

joinfirm_full_org = """
Non puoi unirti alla societa poiché ha raggiunto il numero massimo di membri.
**Numero di impiegati:** %MEMBERS%
**Livello societa:** %LEVEL%

Il CEO della societa può aumentare il livello col comando `!upgrade`
"""


def modify_joinfirm_full(firm):
    return joinfirm_full_org.\
        replace("%MEMBERS%", str(firm.size)).\
        replace("%LEVEL%", str(firm.rank + 1))


joinfirm_org = """
Adesso sei un trader semplice della societa **%NAME%**. Se vuoi uscire dalla societa scrivi *!escidallasocieta*.
"""


def modify_joinfirm(firm):
    return joinfirm_org.\
        replace("%NAME%", firm.name)


FIRM_TAX_ORG = """

--

%AMOUNT% Mem€ sono stati inviati alla societa - %NAME%.
"""


def modify_firm_tax(tax_amount, firm_name):
    return FIRM_TAX_ORG.\
        replace("%AMOUNT%", format(int(tax_amount), ",d")).\
        replace("%NAME%", firm_name)


TEMPLATE_NOT_OP = """
Spiacente, ma non sei OP
"""

TEMPLATE_ALREADY_DONE = """
Spiacente, ma hai già inviato il link template.
"""

TEMPLATE_NOT_STICKY = """
Spiacente, ma devi rispondere *direttamente* al messaggio stickato del bot.
"""

TEMPLATE_OP = """
---

OP %NAME% ha postato *[IL LINK AL TEMPLATE](%LINK%)*, Evviva!
"""


def modify_template_op(link, name):
    return TEMPLATE_OP.\
        replace("%LINK%", link).\
        replace("%NAME%", name)


invite_not_private_failure_org = """
Non hai bisogno di invitare qualcuno poiché la tua societa non è privata.

Gli investitori possono unirsi col comando `!entrainsocieta <firm_name>`.

Se sei il CEO e vuoi impostare la societa come privata, usa il comando `!impostaprivato`.
"""

invite_no_user_failure_org = """
Impossibile invitare l'utente, assicurati di aver scritto il nome correttamente.
"""

invite_in_firm_failure_org = """
Questo utente fa già parte di un'altra societa. Assicurati che esca prima di invitarlo nuovamente.
"""

invite_org = """
Hai invitato /u/%NAME% nella societa.

Possono accettare questa richiesta usando il comando `!entrainsocieta %FIRM%`.
"""


def modify_invite(invitee, firm):
    return invite_org.\
        replace("%NAME%", invitee.name).\
        replace("%FIRM%", firm.name)


setprivate_org = """
La societa è ora privata. I nuovi investitori potranno accedere solo se tu o uno degli Executives invia loro un invito col comando `!invita <user>`.

Se vuoi annullare tutto e tornare con una societa pubblica, scrivi `!impostapubblico`.
"""

setpublic_org = """
La tua societa è ora pubblica. I nuovi investitori potranno accedere senza essere invitati utilizzando il comando `!entrainsocieta <firm_name>`.

"""
upgrade_insufficient_funds_org = """
La societa non ha abbastanza fondi per aumentare il proprio livello.


**Saldo societa:** %BALANCE%
**Costo per passare al livello %LEVEL%:** %COST%
"""


def modify_upgrade_insufficient_funds_org(firm, cost):
    return upgrade_insufficient_funds_org.\
        replace("%BALANCE%", format(int(firm.balance), ",d")).\
        replace("%LEVEL%", str(firm.rank + 2)).\
        replace("%COST%", format(int(cost), ",d"))


upgrade_org = """
Hai migliorato con successo il livello della societa:  **Livello %LEVEL%**!

La societa adesso supporta un massimo di **%MAX_MEMBERS% impiegati**, incluso un massimo di **%MAX_EXECS% executives**.
"""


def modify_upgrade(firm, max_members, max_execs, max_assocs):
    return upgrade_org.\
        replace("%LEVEL%", str(firm.rank + 1)).\
        replace("%MAX_MEMBERS%", str(max_members)).\
        replace("%MAX_EXECS%", str(max_execs)).\
        replace("%MAX_ASSOCS%", str(max_assocs))


DEPLOY_VERSION = """
La versione corrente del bot è stata installata il `%DATE%`
"""


def modify_deploy_version(date):
    return DEPLOY_VERSION.\
        replace("%DATE%", date)


TAX_TOO_HIGH = """
La tassa è troppo alta. Dovrebbe essere tra il 5% e il 75%.
"""

TAX_TOO_LOW = """
La tassa è troppo bassa. Dovrebbe essere tra il 5% e il 75%.
"""

TAX_SUCCESS = """
La nuova tassa è stata impostata con successo
"""

TEMPLATE_SUCCESS = """
Template postato con successo! Grazie per aver reso /r/BancaDelMeme un posto migliore!
"""

WIKI_HEADER = """
Tempo | Link | Importo | Upvotes | Final | Profitto
--- | --- | --- | --- | --- | ---"""

WIKI_ROW = """
%TIME% | [link](https://www.reddit.com/r/BancaDelMeme/comments/%POST%/_/%COMM%) | %AMOUNT% | %SSTART% | %SEND% | %RESULT%"""

WIKI_COMMENT = """
Puoi trovare la lista dei tuoi investimenti conclusi sulla [tua pagina wiki](https://www.reddit.com/r/BancaDelMeme/wiki/%PAGE%)
"""

SELL_INVESTMENTS = """
I{il} tuo{tuo} investiment{agg} {verb} stat{agg} tassat{agg} e chius{agg}.

A breve i{il} comment{agg} verr{verr} aggiornat{agg} con il risultato.
"""

SELL_NO_INVESTMENTS = """
Nessun investimento attivo trovato in questo post"""

def modify_sell_investment(num_investments):
    if num_investments < 1:
        return SELL_NO_INVESTMENTS
    endings = {'il': 'l', 'agg': 'o', 'verb': 'è', 'tuo': '', 'verr': 'à'}
    if num_investments > 1:
        endings = {'il': '', 'agg': 'i', 'verb': 'sono', 'tuo': 'i', 'verr': 'anno'}
    return SELL_INVESTMENTS.format(**endings)

def modify_oc_return(profit):
    return """\n\n---\n\nGrazie del tuo OC!  
Per premiarti ti è stato accreditato un bonus pari all'1% degli investimenti su questo post (ma non i tuoi).

Hai guadagnato cosi {:,d} Mem€""".format(profit)

def modify_oc_capped():
    return """\n\n---\n\nGrazie del tuo OC!  
Per premiarti ti è stato accreditato un bonus pari all'1% degli investimenti su questo post (ma non i tuoi).

Hai cosi raggiunto il saldo massimo! Hai trionfato in questa sanguinosa competizione nel marketplace, e il tuo portafoglio è gonfissimo! Le future generazioni ti ricorderanno come titano degli investimenti.

*"Alessandro pianse, poiché non c'erano altri mondi da conquistare.."""

def cmd_sconosciuto():
    return """Non conosco il comando che mi hai inviato, il tuo messaggio è stato ignorato."""
