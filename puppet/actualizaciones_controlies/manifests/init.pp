stage { [final]: }

Stage[main] -> Stage[final]

class { actualizaciones_controlies: stage => final }

class actualizaciones_controlies {

  if $is_ltsp  == "SI" {
        $tipo_imagen="ltsp"
  } else {
        $tipo_imagen="otro"
  }
 
  case $tipo_imagen {
      "ltsp": {
				# configuracion del despertado automatico de los thinclients para el seguimiento de los mismos.
				        file {"/usr/share/controlies-ltspserver/":
						owner => root, group => root, mode => 755,
					ensure => directory,
					before => File["/usr/share/controlies-ltspserver/despierta_thinclients"],
				}

				file { "/usr/share/controlies-ltspserver/despierta_thinclients":
					owner => root, group => root, mode => 755,
					source => "puppet:///modules/actualizaciones_controlies/despierta_thinclients",
				}

                                file { "/usr/share/controlies-client/despierta_thinclients":
                                        ensure=>absent
                                }


				cron { revision-matinal:
					command => "/usr/share/controlies-ltspserver/despierta_thinclients",
					user    => root,
					hour    => 8,
					minute  => 15
				}

#				cron { revision-recreo:
#				   command => "/usr/share/controlies-ltspserver/despierta_thinclients",
#				   user    => root,
#				   hour    => 11,
#				   minute  => 25
#				}

#				cron { revision-vespertina:
#				   command => "/usr/share/controlies-ltspserver/despierta_thinclients",
#				   user    => root,
#				   hour    => 14,
#				   minute  => 45
#				}

	}
        "otro": {}
	default: {}
    }

    package { "pkpgcounter":
             name => pkpgcounter,
             ensure => installed,
             before => File["/usr/share/pyshared/pkpgpdls/zjstream.py"],

    }    
	
    # Asegurando la existencia de la carpeta
    file {"/usr/share/pyshared/pkpgpdls":
          owner => root, group => root, mode => 755,
          ensure => directory,
          before => File["/usr/share/pyshared/pkpgpdls/zjstream.py"],    
    }

    #Seguimiento impresión, parchea un bug en pkpgcounter.
    file {"/usr/share/pyshared/pkpgpdls/zjstream.py":
    	owner => root, group => root, mode => 644,
    	source => "puppet:///modules/actualizaciones_controlies/zjstream.py",
    }        
}

