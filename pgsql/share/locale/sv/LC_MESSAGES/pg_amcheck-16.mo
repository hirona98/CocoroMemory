��    b      ,  �   <      H      I     j     �     �     �     �  S   �  H   (	  V   q	  =   �	  A   
  U   H
  Z   �
  K   �
  M   E  I   �  I   �  T   '  T   |     �  <   �  D   )  B   n  <   �  D   �  B   3  A   v  :   �  H   �  8   <  6   u  =   �  M   �  K   8  ;   �  U   �  7     =   N  ;   �  :   �  8     <   <  ,   y  0   �  7   �       <        O     c  +   ~     �     �     �     �  %   �     #     +  V   D  )   �  9   �     �       /   >     n     �     �     �  *   �     �  :   �  ,   .  !   [     }     �  3   �  2   �  ;        ?  :   W  :   �     �     �     �        '   3  /   [     �  %   �     �  .   �  #        0     A  0   P     �  /   �  	   �    �  (   U     ~     �     �  $   �     �  W   	  F   a  R   �  D   �  <   @  `   }  h   �  G   G  Q   �  \   �  S   >  b   �  W   �     M   C   h   I   �   C   �   <   :!  J   w!  G   �!  G   
"  A   R"  J   �"  ?   �"  =   #  D   ]#  J   �#  L   �#  >   :$  L   y$  7   �$  E   �$  B   D%  B   �%  :   �%  <   &  -   B&  1   p&  8   �&     �&  L   �&     +'  #   B'  .   f'  "   �'     �'  -   �'     �'  .   (     7(     E(  X   ^(  /   �(  ;   �(  #   #)  #   G)  2   k)     �)     �)  "   �)  %   �)  3   *     5*  :   ;*  -   v*  "   �*     �*     �*  =   �*  9   %+  <   _+     �+  9   �+  :   �+  !   (,     J,     ],  &   q,  9   �,  E   �,     -  <   7-  %   t-  <   �-  7   �-     .     '.  7   8.  #   p.  3   �.  	   �.                           8   ^            $   @   1   b      Y       3           W           )          C      [   R               !   X   O   Q              0   D      "   7   .   ;   =   A      /   
   ?   P                 6   N          &   	       2   H             #      -       %   >          '      J       M   ]          T   +   (       G      S   9       `       B           4       U       ,       V   *      :   F   5   I         L      \   _      <          a      K   Z       E    
B-tree index checking options:
 
Connection options:
 
Other options:
 
Report bugs to <%s>.
 
Table checking options:
 
Target options:
       --endblock=BLOCK            check table(s) only up to the given block number
       --exclude-toast-pointers    do NOT follow relation TOAST pointers
       --heapallindexed            check that all heap tuples are found within indexes
       --install-missing           install missing extensions
       --maintenance-db=DBNAME     alternate maintenance database
       --no-dependent-indexes      do NOT expand list of relations to include indexes
       --no-dependent-toast        do NOT expand list of relations to include TOAST tables
       --no-strict-names           do NOT require patterns to match objects
       --on-error-stop             stop checking at end of first corrupt page
       --parent-check              check index parent/child relationships
       --rootdescend               search from root page to refind tuples
       --skip=OPTION               do NOT check "all-frozen" or "all-visible" blocks
       --startblock=BLOCK          begin checking table(s) at the given block number
   %s [OPTION]... [DBNAME]
   -?, --help                      show this help, then exit
   -D, --exclude-database=PATTERN  do NOT check matching database(s)
   -I, --exclude-index=PATTERN     do NOT check matching index(es)
   -P, --progress                  show progress information
   -R, --exclude-relation=PATTERN  do NOT check matching relation(s)
   -S, --exclude-schema=PATTERN    do NOT check matching schema(s)
   -T, --exclude-table=PATTERN     do NOT check matching table(s)
   -U, --username=USERNAME         user name to connect as
   -V, --version                   output version information, then exit
   -W, --password                  force password prompt
   -a, --all                       check all databases
   -d, --database=PATTERN          check matching database(s)
   -e, --echo                      show the commands being sent to the server
   -h, --host=HOSTNAME             database server host or socket directory
   -i, --index=PATTERN             check matching index(es)
   -j, --jobs=NUM                  use this many concurrent connections to the server
   -p, --port=PORT                 database server port
   -r, --relation=PATTERN          check matching relation(s)
   -s, --schema=PATTERN            check matching schema(s)
   -t, --table=PATTERN             check matching table(s)
   -v, --verbose                   write a lot of output
   -w, --no-password               never prompt for password
 %*s/%s relations (%d%%), %*s/%s pages (%d%%) %*s/%s relations (%d%%), %*s/%s pages (%d%%) %*s %*s/%s relations (%d%%), %*s/%s pages (%d%%) (%s%-*.*s) %s %s checks objects in a PostgreSQL database for corruption.

 %s home page: <%s>
 %s must be in range %d..%d Are %s's and amcheck's versions compatible? Cancel request sent
 Command was: %s Could not send cancel request:  Query was: %s Try "%s --help" for more information. Usage:
 btree index "%s.%s.%s":
 btree index "%s.%s.%s": btree checking function returned unexpected number of rows: %d cannot specify a database name with --all cannot specify both a database name and database patterns checking btree index "%s.%s.%s" checking heap table "%s.%s.%s" could not connect to database %s: out of memory database "%s": %s detail:  end block out of bounds end block precedes start block error sending command to database "%s": %s error:  heap table "%s.%s.%s", block %s, offset %s, attribute %s:
 heap table "%s.%s.%s", block %s, offset %s:
 heap table "%s.%s.%s", block %s:
 heap table "%s.%s.%s":
 hint:  improper qualified name (too many dotted names): %s improper relation name (too many dotted names): %s in database "%s": using amcheck version "%s" in schema "%s" including database "%s" internal error: received unexpected database pattern_id %d internal error: received unexpected relation pattern_id %d invalid argument for option %s invalid end block invalid start block invalid value "%s" for option %s no btree indexes to check matching "%s" no connectable databases to check matching "%s" no databases to check no heap tables to check matching "%s" no relations to check no relations to check in schemas matching "%s" no relations to check matching "%s" query failed: %s query was: %s
 skipping database "%s": amcheck is not installed start block out of bounds too many command-line arguments (first is "%s") warning:  Project-Id-Version: PostgreSQL 15
Report-Msgid-Bugs-To: pgsql-bugs@lists.postgresql.org
POT-Creation-Date: 2022-05-09 18:50+0000
PO-Revision-Date: 2023-09-05 08:59+0200
Last-Translator: Dennis Björklund <db@zigo.dhs.org>
Language-Team: Swedish <pgsql-translators@postgresql.org>
Language: sv
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
 
Flaggor för kontroll av B-tree-index:
 
Flaggor för anslutning:
 
Andra flaggor:
 
Rapportera fel till <%s>.
 
Flaggor för kontroll av tabeller:
 
Flaggor för destinationen:
       --endblock=BLOCK            kontrollera tabell(er) fram till angivet blocknummer
       --exclude-toast-pointers    följ INTE relationers TOAST-pekare
       --heapallindexed            kontrollera att alla heap-tupler hittas i index
       --install-missing           installera utökningar som saknas
       --maintenance-db=DBNAMN     val av underhållsdatabas
       --no-dependent-indexes      expandera INTE listan med relationer för att inkludera index
       --no-dependent-toast        expandera inte listan av relationer för att inkludera TOAST-tabeller
       --no-strict-names           kräv INTE mallar för matcha objekt
       --on-error-stop             sluta kontrollera efter första korrupta sidan
       --parent-check              kontrollera förhållandet mellan barn/förälder i index
       --rootdescend               sök från root-sidan för att återfinna tupler
       --skip=FLAGGA               kontrollera INTE block som är "all-frozen" eller "all-visible"
       --startblock=BLOCK          börja kontollera tabell(er) vid angivet blocknummer
   %s [FLAGGA]... [DBNAMN]
   -?, --help                      visa denna hjälp, avsluta sedan
   -D, --exclude-database=MALL     kontrollera INTE matchande databas(er)
   -I, --exclude-index=MALL        kontrollera INTE matchande index
   -P, --progress                  visa förloppsinformation
   -R, --exclude-relation=MALL     kontrollera INTE matchande relation(er)
   -S, --exclude-schema=MALL       kontrollera INTE matchande schema(n)
   -T, --exclude-table=MALL        kontollera INTE matchande tabell(er)
   -U, --username=ANVÄNDARE        användarnamn att ansluta som
   -V, --version                   visa versionsinformation, avsluta sedan
   -W, --password                  tvinga fram lösenordsfråga
   -a, --all                       kontrollera alla databaser
   -d, --database=MALL             kontrollera matchande databas(er)
   -e, --echo                      visa kommandon som skickas till servern
   -h, --host=VÄRDNAMN             databasens värdnamn eller socketkatalog
   -i, --index=MALL                kontrollera matchande index
   -j, --jobs=NUM                  antal samtidiga anslutningar till servern
   -p, --port=PORT                 databasserverns port
   -r, --relation=MALL             kontrollera matchande relation(er)
   -s, --schema=MALL               kontrollera matchande schema(n)
   -t, --table=MALL                kontollera matchande tabell(er)
   -v, --verbose                   skriv massor med utdata
   -w, --no-password               fråga ej efter lösenord
 %*s/%s relationer (%d%%), %*s/%s sidor (%d%%) %*s/%s relationer (%d%%), %*s/%s sidor (%d%%) %*s %*s/%s relationer (%d%%), %*s/%s sidor (%d%%) (%s%-*.*s) %s %s kontrollerar objekt i en PostgreSQL-database för att hitta korruption.

 hemsida för %s: <%s>
 %s måste vara i intervallet %d..%d Är versionerna på %s och amcheck kompatibla? Förfrågan om avbrytning skickad
 Kommandot var: %s Kunde inte skicka förfrågan om avbrytning:  Frågan var: %s Försök med "%s --help" för mer information. Användning:
 btree-index "%s.%s.%s":
 btree-index "%s.%s.%s": kontrollfunktion för btree returnerade oväntat antal rader: %d kan inte ange databasnamn tillsammans med --all kan inte ange både ett databasnamn och ett databasmönster kontrollerar btree-index "%s.%s.%s" kontrollerar heap-tabell "%s.%s.%s" kunde inte ansluta till databas %s: slut på minne databas "%s": %s detalj:  slutblocket utanför giltig gräns slutblocket kommer före startblocket fel vid skickande av kommando till databas "%s": %s fel:  heap-tabell "%s.%s.%s", block %s, offset %s, attribut %s:
 heap-tabell "%s.%s.%s", block %s, offset %s:
 heap-tabell "%s.%s.%s", block %s:
 heap-tabell "%s.%s.%s":
 tips:  ej korrekt kvalificerat namn (för många namn med punkt): %s ej korrekt relationsnamn (för många namn med punkt): %s i databas "%s": använder amcheck version "%s" i schema "%s" inkludera databas "%s" internt fel: tog emot oväntat pattern_id %d för databas internt fel: tog emot oväntat pattern_id %d för relation ogiltigt argument för flaggan %s ogiltigt slutblock ogiltigt startblock ogiltigt värde "%s" för flaggan "%s" finns inga btree-index för att kontrollera matching "%s" finns inga anslutningsbara databaser att kontrollera som matchar "%s" inga databaser att kontrollera finns inga heap-tabeller för att kontrollera matchning "%s" finns inga relationer att kontrollera finns inga relationer att kontrollera i schemamatchning "%s" finns inga relations för att kontrollera matching "%s" fråga misslyckades: %s frågan var: %s
 hoppar över databas "%s": amcheck är inte installerad startblocket utanför giltig gräns för många kommandoradsargument (första är "%s") varning:  