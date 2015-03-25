
class instala_controlies {

   $version="0.6.6-6"
   $paquete_client="controlies-client_${version}_all.deb"
   $paquete_ltspserver="controlies-ltspserver_${version}_all.deb"
   $paquete_thinclient="controlies-thinclient_${version}_all.deb"

   #################################
   #Paquete thinclients
   #################################
   case $use {
        #Servidores ltsp
        "ltsp-server", "ltsp-wheezy" : {
                file {"/opt/ltsp/i386/var/cache/$paquete_thinclient":
                        owner => root, group => root, mode => 755,
                        source => "puppet:///instala_controlies/$paquete_thinclient",
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
			command => "/usr/sbin/ltsp-update-image --arch i386",
			refreshonly => true,
		}

		#################################
		# Paquete ltspservers
		#################################
		package { "controlies-client": ensure => "purged"}

		file {"/var/cache/$paquete_ltspserver":
			owner => root, group => root, mode => 755,
			source => "puppet:///instala_controlies/$paquete_ltspserver",
			notify => Exec["instala_controlies_ltspserver"]
		}
		exec { "instala_controlies_ltspserver":
			path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
			command => "apt-get remove --purge controlies-ltspserver; dpkg -i --force-confnew  --force-overwrite $paquete_ltspserver; apt-get -f -y install ",
		#		command => "dpkg -i --force-confnew  --force-overwrite $paquete_client; apt-get -f -y install ",
			cwd => "/var/cache",
			unless => "dpkg -l | grep controlies-ltspserver | grep $version | grep ^ii",
			require => File["/var/cache/$paquete_ltspserver"],
		}
	}
	default: {

		   #################################
		   #Paquete clients
		   #################################
		   file {"/var/cache/$paquete_client":
				owner => root, group => root, mode => 755,
				source => "puppet:///instala_controlies/$paquete_client",
				notify => Exec["instala_controlies_client"]
		   }
		   exec { "instala_controlies_client":
				path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
				command => "apt-get remove --purge controlies-client; dpkg -i --force-confnew  --force-overwrite $paquete_client; apt-get -f -y install ",
		#		command => "dpkg -i --force-confnew  --force-overwrite $paquete_client; apt-get -f -y install ",
				cwd => "/var/cache",
				unless => "dpkg -l | grep controlies-client | grep $version | grep ^ii",
				require => File["/var/cache/$paquete_client"],
		   }
	}
   }    
}
