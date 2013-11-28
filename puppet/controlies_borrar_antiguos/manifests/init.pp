#======================================================================================================================
#Reglas de limpieza de los rastros de la versión anterior de controlies:
#   Se quitan antiguos scripts y rastros de la version preliminar de controlies-seguimiento, antes de la debianización
#   para evitar que queden rastros inútiles de antiguas tareas
#======================================================================================================================

class controlies_borrar_antiguos {

       file { "/root/scripts/despierta_thinclients": 
            ensure => absent,
       }

       exec { "limpia_crontab_dc":
                path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                command => "sed -i.bak '\/root\/scripts\/despierta_thinclients/d' /var/spool/cron/crontabs/root",
                onlyif => "grep '/root/scripts/despierta_thinclients' /var/spool/cron/crontabs/root"
       }

       file { "/root/scripts/seguimiento_equipo":
            ensure => absent,
       }

       exec { "limpia_crontab_se":
                path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                command => "sed -i.bak '\/root\/scripts\/seguimiento_equipo/d' /var/spool/cron/crontabs/root",
                onlyif => "grep '/root/scripts/seguimiento_equipo' /var/spool/cron/crontabs/root"
       }
 
       file { "/root/scripts/seguimiento_impresion":
               ensure => absent,
       }

       exec {"limpieza_gdm3":
                path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                command => "sed -i.bak '/equipo=$(hostname -s)/,+5d' /etc/gdm3/PostSession/Default",
                cwd => "/root",
                onlyif =>"grep 'equipo=$(hostname -s)' /etc/gdm3/PostSession/Default",
       }

       exec {"limpieza_gdm":
                path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                command => "sed -i.bak '/equipo=$(hostname -s)/,+5d' /etc/gdm/PostSession/Default",
                cwd => "/root",
                onlyif =>"grep 'equipo=$(hostname -s)' /etc/gdm/PostSession/Default",
       }
}

