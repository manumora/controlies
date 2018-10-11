import "/etc/puppet/defines/*.pp"

class instala_controlies {

   $version="0.7.0-8"
   $paquete_client="controlies-client_${version}_all.deb"
   $paquete_ltspserver="controlies-ltspserver_${version}_all.deb"
   $paquete_thinclient="controlies-thinclient_${version}_all.deb"

   #Limpiamos facter is_ltsp por si estuviera de antes
   file {"/usr/lib/ruby/vendor_ruby/facter/is_ltsp.rb":
           ensure => absent,
   }

   case $ies_isltsp {  # Una imagen tipo ltsp puede ser un servidor de telefonica, una siatic, etc. Cualquiera que este
                       # en un aula con thinclients. Debe ser declarado con un facter propio ies_isltsp en /etc/escuela2.0
        "si","yes","true" : {

		    #################################
		    #Paquete thinclients
		    #################################

			file {"/opt/ltsp/i386/var/cache/$paquete_thinclient":
					owner => root, group => root, mode => 755,
					source => "puppet:///modules/instala_controlies/$paquete_thinclient",
					notify => Exec["instala_controlies_thinclient"]
			}

			exec { "instala_controlies_thinclient":
					path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
					command => "chroot /opt/ltsp/i386 /usr/bin/dpkg -i --force-confnew  --force-overwrite /var/cache/$paquete_thinclient",
						       #No se incluye el montaje de proc en el comando. Si se pone daba problemas en la instalacion del paquete.
					unless => "chroot /opt/ltsp/i386 dpkg -l | grep controlies-thinclient | grep $version | grep ^ii",
					require => File["/opt/ltsp/i386/var/cache/$paquete_thinclient"],
					notify => Exec["actualiza-imagen-controlies"]
			}

			exec { "actualiza-imagen-controlies":
					 command => "/usr/sbin/ltsp-update-image",
					 refreshonly => true,
			}
 
			#################################
			# Paquete ltspservers
			#################################
			package { "controlies-client": ensure => "purged"}

			file {"/var/cache/$paquete_ltspserver":
				owner => root, group => root, mode => 755,
				source => "puppet:///modules/instala_controlies/$paquete_ltspserver",
				notify => Exec["instala_controlies_ltspserver"]
			}
			exec { "instala_controlies_ltspserver":
				path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
				command => "apt-get remove --purge controlies-ltspserver; dpkg -i --force-confnew  --force-overwrite $paquete_ltspserver; apt-get -f -y install ",
				cwd => "/var/cache",
				unless => "dpkg -l | grep controlies-ltspserver | grep $version | grep ^ii",
				require => File["/var/cache/$paquete_ltspserver"],
			}


		    ###################################################################################################
			# configuracion del despertado automatico de los thinclients para el seguimiento de los mismos.
		    ###################################################################################################

			file {"/usr/share/controlies-ltspserver/":
					owner => root, group => root, mode => 755,
				ensure => directory,
				before => File["/usr/share/controlies-ltspserver/despierta_thinclients"],
			}

			file { "/usr/share/controlies-ltspserver/despierta_thinclients":
				owner => root, group => root, mode => 755,
				source => "puppet:///modules/instala_controlies/despierta_thinclients",
			}

			cron { revision-matinal:
				command => "/usr/share/controlies-ltspserver/despierta_thinclients",
				user    => root, hour    => 8, minute  => 15
			}

			#cron { revision-recreo:
			#    command => "/usr/share/controlies-ltspserver/despierta_thinclients",
			#    user    => root,    hour    => 11,   minute  => 25
			#}

			#cron { revision-vespertina:
			#    command => "/usr/share/controlies-ltspserver/despierta_thinclients",
			#    user    => root,	   hour    => 14,	   minute  => 45
			#}

	}
	default: {

		   ##################################################################
		   #Paquete clients, para workstations, portatiles, etc...
		   ##################################################################
                   package { "controlies-ltspserver": ensure => "purged"}

		   file {"/var/cache/$paquete_client":
				owner => root, group => root, mode => 755,
				source => "puppet:///modules/instala_controlies/$paquete_client",
				notify => Exec["instala_controlies_client"]
		   }
		   exec { "instala_controlies_client":
				path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
				command => "apt-get remove --purge controlies-client; dpkg -i --force-confnew  --force-overwrite $paquete_client; apt-get -f -y install ",
				cwd => "/var/cache",
				unless => "dpkg -l | grep controlies-client | grep $version | grep ^ii",
				require => File["/var/cache/$paquete_client"],
		   }

	}


   }    

}
