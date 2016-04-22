class instala_controlies {

   $version="0.7.0-3"
   $paquete_client="controlies-client_${version}_all.deb"
   $paquete_ltspserver="controlies-ltspserver_${version}_all.deb"
   $paquete_thinclient="controlies-thinclient_${version}_all.deb"

   file {"/usr/lib/ruby/vendor_ruby/facter/is_ltsp.rb":
                                owner => root, group => root, mode => 644,
                                source => "puppet:///modules/instala_controlies/is_ltsp.rb",
   }

   #Usamos el facter is_ltsp para determinar si el equipo es un LTSP
   case $is_ltsp {
      "SI" : {
        $tipo_imagen="ltsp"
      }
      "NO" : {
        $tipo_imagen="otro"
      }
      default:  { #Todavia no está el facter instalado, no podemos determinar el tipo de imagen
        $tipo_imagen=""
      }
   }

   #################################
   #Paquete thinclients
   #################################
   case $tipo_imagen {
        #Servidores ltsp
        "ltsp" : {
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



                #El comando para actualizar la imagen de los thinclient difiere entre squeeze/wheezy-ubuntu
        
                case $use {
                     "ltsp-wheezy", "aulatic-profesor-wheezy", "ubuntu": {
                         $comandoupdateimagen="/usr/sbin/ltsp-update-image"
                     }

                     "ltsp-server": {
                         $comandoupdateimagen="/usr/sbin/ltsp-update-image --arch i386"
                     }

                     default: {
                         $comandoupdateimagen="/usr/sbin/ltsp-update-image"
                     }
                }

                exec { "actualiza-imagen-controlies":
                         command => "$comandoupdateimagen",
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
	}
	"otro": {

		   #################################
		   #Paquete clients
		   #################################
		   file {"/var/cache/$paquete_client":
				owner => root, group => root, mode => 755,
				source => "puppet:///modules/instala_controlies/$paquete_client",
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
