��          �   %   �      p  �   q  
   K  �   V     �  3   �  +   )  7   U  6   �  L   �  <        N  6   b  %   �     �  $   �  )   �  (     (   ?     h     �     �     �     �     �  !   �     �  	     
  $  1  /	     a
  �   w
  @   b  x   �  F     =   c  r   �  �     Y   �  +   �  O   +  Z   {     �  D   �  Q   8  Q   �  U   �  4   2     g     �     �  <   �  G   �  e   )  N   �     �                                                                              
                    	                         
For use as archive_cleanup_command in postgresql.conf:
  archive_cleanup_command = 'pg_archivecleanup [OPTION]... ARCHIVELOCATION %%r'
e.g.
  archive_cleanup_command = 'pg_archivecleanup /mnt/server/archiverdir %%r'
 
Options:
 
Or for use as a standalone archive cleaner:
e.g.
  pg_archivecleanup /mnt/server/archiverdir 000000010000000000000010.00000020.backup
 
Report bugs to <%s>.
   %s [OPTION]... ARCHIVELOCATION OLDESTKEPTWALFILE
   -?, --help     show this help, then exit
   -V, --version  output version information, then exit
   -d             generate debug output (verbose mode)
   -n             dry run, show the names of the files that would be removed
   -x EXT         clean up files if they have this extension
 %s home page: <%s>
 %s removes older WAL files from PostgreSQL archives.

 Try "%s --help" for more information. Usage:
 archive location "%s" does not exist could not close archive location "%s": %m could not open archive location "%s": %m could not read archive location "%s": %m could not remove file "%s": %m detail:  error:  hint:  invalid file name argument must specify archive location must specify oldest kept WAL file too many command-line arguments warning:  Project-Id-Version: pg_archivecleanup (PostgreSQL) 10
Report-Msgid-Bugs-To: pgsql-bugs@lists.postgresql.org
POT-Creation-Date: 2022-08-27 14:52+0300
PO-Revision-Date: 2024-09-07 06:17+0300
Last-Translator: Alexander Lakhin <exclusion@gmail.com>
Language-Team: Russian <pgsql-ru-general@postgresql.org>
Language: ru
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);
 
Для использования в качестве archive_cleanup_command в postgresql.conf:
  archive_cleanup_command = 'pg_archivecleanup [ПАРАМЕТР]... РАСПОЛОЖЕНИЕ_АРХИВА %%r'
например:
  archive_cleanup_command = 'pg_archivecleanup /mnt/server/archiverdir %%r'
 
Параметры:
 
Либо для использования в качестве отдельного средства очистки архива,
например:
  pg_archivecleanup /mnt/server/archiverdir 000000010000000000000010.00000020.backup
 
Об ошибках сообщайте по адресу <%s>.
   %s [ПАРАМЕТР]... РАСПОЛОЖЕНИЕ_АРХИВА СТАРЕЙШИЙ_СОХРАНЯЕМЫЙ_ФАЙЛ_WAL
   -?, --help     показать эту справку и выйти
   -V, --version  показать версию и выйти
   -d             генерировать подробные сообщения (отладочный режим)
   -n             холостой запуск, только показать имена файлов, которые будут удалены
   -x РСШ         удалить файлы с заданным расширением
 Домашняя страница %s: <%s>
 %s удаляет старые файлы WAL из архивов PostgreSQL.

 Для дополнительной информации попробуйте "%s --help". Использование:
 расположение архива "%s" не существует не удалось закрыть расположение архива "%s": %m не удалось открыть расположение архива "%s": %m не удалось прочитать расположение архива "%s": %m не удалось стереть файл "%s": %m подробности:  ошибка:  подсказка:  неверный аргумент с именем файла необходимо задать расположение архива необходимо задать имя старейшего сохраняемого файла WAL слишком много аргументов командной строки предупреждение:  