��    i      d  �   �       	     	  8   	  8   Q	  D   �	  8   �	  4   
  >   =
  <   |
  I   �
  9     ?   =  7   }     �  /   �  /     1   5     g     �  3   �  ,   �  !   �  $     $   =     b  $   �  .   �  &   �  '   �      #  	   D  $   N     s  %   �  I   �  d   �  8   _  3   �  #   �  "   �  #        7  $   U  /   z     �     �     �  "        &     D  (   _  '   �  *   �  )   �  !        '  #   D     h     �     �  )   �     �  )   �  &   (  %   O     u  ,   ~     �     �     �  4   �  6        T     p  $   w     �      �     �     �          -     =     O     \     n          �     �     �  L   �  A        X  /   s     �     �     �     �                2     J     b  %   t     �  	   �  �  �       >   �  F   �  >   %  D   d  8   �  M   �  F   0  L   w  N   �  Q     F   e  .   �  ;   �  ;     <   S     �     �  B   �  4     3   A  2   u  2   �  '   �  ,     ?   0  8   p  2   �  (   �  
      6      #   G   1   k   Z   �   �   �   I   �!  I   �!  (   !"  ,   J"  +   w"  #   �"  ,   �"  7   �"  *   ,#  :   W#  "   �#  .   �#  *   �#  %   $  >   5$  7   t$  @   �$  9   �$  .   '%  *   V%  3   �%  !   �%  $   �%  (   �%  6   %&  *   \&  S   �&  C   �&  <   '  
   \'  B   g'  	   �'     �'     �'  V   �'  S   J(  (   �(  
   �(  ?   �(  3   )  8   F)  3   )  ,   �)  *   �)     *      *     7*     H*     `*  +   s*     �*     �*     �*  p   �*  \   K+     �+  B   �+  #   ,     /,     I,     e,     �,     �,     �,     �,     �,  3   �,     /-     I-     0             U   &       1       :   (   V          T       S           5   6   +      W          *      7                            X       '   =      R                        /              Z   @   ,   ?              ]   `   Y   4           -       C          O      P       I       A   [               >   M       E   F   d   "       b   G          9      g      L   e   
   !          J   c   D   \          B   .   2       Q   #          ;   f   H   )           _   a       	           $   <   %   ^             N   i      K   h             8           3    
Report bugs to <%s>.
   -?, --help                  show this help, then exit
   -P, --progress              show progress information
   -V, --version               output version information, then exit
   -e, --exit-on-error         exit immediately on error
   -i, --ignore=RELATIVE_PATH  ignore indicated path
   -m, --manifest-path=PATH    use specified path for manifest
   -n, --no-parse-wal          do not try to parse WAL files
   -q, --quiet                 do not print any output, except for errors
   -s, --skip-checksums        skip checksum verification
   -w, --wal-directory=PATH    use specified path for WAL files
 "%s" has size %lld on disk but size %zu in the manifest "%s" is not a file or directory "%s" is present in the manifest but not on disk "%s" is present on disk but not in the manifest "\u" must be followed by four hexadecimal digits. %*s/%s kB (%d%%) verified %s home page: <%s>
 %s verifies a backup against the backup manifest.

 Character with value 0x%02x must be escaped. Escape sequence "\%s" is invalid. Expected "," or "]", but found "%s". Expected "," or "}", but found "%s". Expected ":", but found "%s". Expected JSON value, but found "%s". Expected array element or "]", but found "%s". Expected end of input, but found "%s". Expected string or "}", but found "%s". Expected string, but found "%s". Options:
 The input string ended unexpectedly. Token "%s" is invalid. Try "%s --help" for more information. Unicode escape value could not be translated to the server's encoding %s. Unicode escape values cannot be used for code point values above 007F when the encoding is not UTF8. Unicode high surrogate must not follow a high surrogate. Unicode low surrogate must follow a high surrogate. Usage:
  %s [OPTION]... BACKUPDIR

 WAL parsing failed for timeline %u \u0000 cannot be converted to text. backup successfully verified
 both path name and encoded path name cannot duplicate null pointer (internal error)
 cannot specify both %s and %s checksum mismatch for file "%s" checksum without algorithm could not close directory "%s": %m could not close file "%s": %m could not decode file name could not finalize checksum of file "%s" could not finalize checksum of manifest could not initialize checksum of file "%s" could not initialize checksum of manifest could not open directory "%s": %m could not open file "%s": %m could not parse backup manifest: %s could not parse end LSN could not parse start LSN could not read file "%s": %m could not read file "%s": read %d of %lld could not stat file "%s": %m could not stat file or directory "%s": %m could not update checksum of file "%s" could not update checksum of manifest detail:  duplicate path name in backup manifest: "%s" error:  expected at least 2 lines expected version indicator file "%s" has checksum of length %d, but expected %d file "%s" should contain %zu bytes, but read %zu bytes file size is not an integer hint:  invalid checksum for file "%s": "%s" invalid manifest checksum: "%s" last line not newline-terminated manifest checksum mismatch manifest ended unexpectedly manifest has no checksum missing end LSN missing path name missing size missing start LSN missing timeline no backup directory specified out of memory out of memory
 parsing failed program "%s" is needed by %s but was not found in the same directory as "%s" program "%s" was found by "%s" but was not the same version as %s timeline is not an integer too many command-line arguments (first is "%s") unexpected WAL range field unexpected array end unexpected array start unexpected file field unexpected manifest version unexpected object end unexpected object field unexpected object start unexpected scalar unrecognized checksum algorithm: "%s" unrecognized top-level field warning:  Project-Id-Version: PostgreSQL 16
Report-Msgid-Bugs-To: pgsql-bugs@lists.postgresql.org
POT-Creation-Date: 2023-07-29 09:17+0000
PO-Revision-Date: 2024-09-16 16:35+0200
Last-Translator: Guillaume Lelarge <guillaume@lelarge.info>
Language-Team: French <guillaume@lelarge.info>
Language: fr
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n > 1);
X-Generator: Poedit 3.5
 
Rapporter les bogues à <%s>.
   -?, --help                  affiche cette aide, puis quitte
   -P, --progress              affiche les informations de progression
   -V, --version               affiche la version, puis quitte
   -e, --exit-on-error         quitte immédiatement en cas d'erreur
   -i, --ignore=CHEMIN_RELATIF ignore le chemin indiqué
   -m, --manifest-path=CHEMIN  utilise le chemin spécifié pour le manifeste
   -n, --no-parse-wal          n'essaie pas d'analyse les fichiers WAL
   -q, --quiet                 n'affiche aucun message sauf pour les erreurs
   -s, --skip-checksums        ignore la vérification des sommes de contrôle
   -w, --wal-directory=CHEMIN  utilise le chemin spécifié pour les fichiers WAL
 « %s » a une taille de %lld sur disque mais de %zu dans le manifeste « %s » n'est ni un fichier ni un répertoire « %s » est présent dans le manifeste mais pas sur disque « %s » est présent sur disque mais pas dans le manifeste « \u » doit être suivi par quatre chiffres hexadécimaux. %*s/%s Ko (%d%%) vérifiés Page d'accueil de %s : <%s>
 %s vérifie une sauvegarde à partir du manifeste de sauvegarde.

 Le caractère de valeur 0x%02x doit être échappé. La séquence d'échappement « \%s » est invalide. « , » ou « ] » attendu, mais trouvé « %s ». « , » ou « } » attendu, mais trouvé « %s ». « : » attendu, mais trouvé « %s ». Valeur JSON attendue, mais « %s » trouvé. Élément de tableau ou « ] » attendu, mais trouvé « %s ». Attendait une fin de l'entrée, mais a trouvé « %s ». Chaîne ou « } » attendu, mais « %s » trouvé. Chaîne attendue, mais « %s » trouvé. Options :
 La chaîne en entrée se ferme de manière inattendue. Le jeton « %s » n'est pas valide. Essayez « %s --help » pour plus d'informations. La valeur d'échappement unicode ne peut pas être traduite dans l'encodage du serveur %s. Les valeurs d'échappement Unicode ne peuvent pas être utilisées pour des valeurs de point code au-dessus de 007F quand l'encodage n'est pas UTF8. Une substitution unicode haute ne doit pas suivre une substitution haute. Une substitution unicode basse ne doit pas suivre une substitution haute. Usage:
  %s [OPTION]... REP_SAUVEGARDE

 analyse du WAL échouée pour la timeline %u \u0000 ne peut pas être converti en texte. sauvegarde vérifiée avec succès
 le nom du chemin et le nom du chemin encodé ne peut pas dupliquer un pointeur nul (erreur interne)
 ne peut pas spécifier à la fois %s et %s différence de somme de contrôle pour le fichier « %s » somme de contrôle sans algorithme n'a pas pu fermer le répertoire « %s » : %m n'a pas pu fermer le fichier « %s » : %m n'a pas pu décoder le nom du fichier n'a pas pu finaliser la somme de contrôle du fichier « %s » n'a pas pu finaliser la somme de contrôle du manifeste n'a pas pu initialiser la somme de contrôle du fichier « %s » n'a pas pu initialiser la somme de contrôle du manifeste n'a pas pu ouvrir le répertoire « %s » : %m n'a pas pu ouvrir le fichier « %s » : %m n'a pas pu analyser le manifeste de sauvegarde : %s n'a pas pu analyser le LSN de fin n'a pas pu analyser le LSN de début n'a pas pu lire le fichier « %s » : %m n'a pas pu lire le fichier « %s » : a lu %d sur %lld n'a pas pu tester le fichier « %s » : %m n'a pas pu récupérer les informations sur le fichier ou répertoire
« %s » : %m n'a pas pu mettre à jour la somme de contrôle du fichier « %s » n'a pas pu mettre à jour la somme de contrôle du manifeste détail :  nom de chemin dupliqué dans le manifeste de sauvegarde : « %s » erreur :  attendait au moins deux lignes indicateur de version inattendu le fichier « %s » a une somme de contrôle de taille %d, alors que %d était attendu le fichier « %s » devrait contenir %zu octets, mais la lecture produit %zu octets la taille du fichier n'est pas un entier astuce :   somme de contrôle invalide pour le fichier « %s » : « %s » somme de contrôle du manifeste invalide : « %s » dernière ligne non terminée avec un caractère newline différence de somme de contrôle pour le manifeste le manifeste se termine de façon inattendue le manifeste n'a pas de somme de contrôle LSN de fin manquante nom de chemin manquant taille manquante LSN de début manquante timeline manquante pas de répertoire de sauvegarde spécifié mémoire épuisée mémoire épuisée
 échec de l'analyse le programme « %s » est nécessaire pour %s, mais n'a pas été trouvé dans le même répertoire que « %s » le programme « %s » a été trouvé par « %s » mais n'est pas de la même version que %s la timeline n'est pas un entier trop d'arguments en ligne de commande (le premier étant « %s ») champ d'intervalle de WAL inattendu fin de tableau inattendue début de tableau inattendu champ de fichier inattendu version du manifeste inattendue fin d'objet inattendue champ d'objet inattendu début d'objet inattendu scalaire inattendu algorithme de somme de contrôle inconnu : « %s » champ haut niveau inconnu attention :  