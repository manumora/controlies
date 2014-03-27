
stage { [final]: }

Stage[main] -> Stage[final]

class { actualizaciones_controlies: stage => final }

class actualizaciones_controlies {

  case $use {
      "ltsp-server": {
				# configuracion del despertado automatico de los thinclients para el seguimiento de los mismos.
				        file {"/usr/share/controlies-client/":
						owner => root, group => root, mode => 755,
					ensure => directory,
					before => File["/usr/share/controlies-client/despierta_thinclients"],
				}

				file { "/usr/share/controlies-client/despierta_thinclients":
					owner => root, group => root, mode => 755,
					source => "puppet:///actualizaciones_controlies/despierta_thinclients",
				}

				cron { revision-matinal:
					command => "/usr/share/controlies-client/despierta_thinclients",
					user    => root,
					hour    => 8,
					minute  => 15
				}

		#		cron { revision-recreo:
		#		   command => "/usr/share/controlies-client/despierta_thinclients",
		#		   user    => root,
		#		   hour    => 11,
		#		   minute  => 25
		#		}

		#		cron { revision-vespertina:
		#		   command => "/usr/share/controlies-client/despierta_thinclients",
		#		   user    => root,
		#		   hour    => 14,
		#		   minute  => 45
		#		}

			}
        "portatil-profesor-2011","portatil-alumno-2011": {
		file {"/etc/dhcp/dhcp.conf":
			owner => root, group => root, mode => 644,
			source => "puppet:///actualizaciones_controlies/dhcp.conf",
		}        
	}
	default: {}
    }

    #Seguimiento impresión, parchea un bug en pkpgcounter.
    file {"/usr/share/pyshared/pkpgpdls/zjstream.py":
    	owner => root, group => root, mode => 644,
    	source => "puppet:///actualizaciones_controlies/zjstream.py",
    }        
}

