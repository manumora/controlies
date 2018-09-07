class ssh_confidence_controlies {

   file { "/root/.ssh/authorized_keys.controlies":
                source => "puppet:///modules/ssh_confidence_controlies/id_rsa.pub",
                owner => root,
                mode => 600
        }

   exec { "add_controlies_key":
                path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                command => "cat /root/.ssh/authorized_keys.controlies >> /root/.ssh/authorized_keys; chattr +i /root/.ssh/authorized_keys",
                unless => "grep -f /root/.ssh/authorized_keys.controlies /root/.ssh/authorized_keys",
                require => File["/root/.ssh/authorized_keys.controlies"]
        }


   case $ies_isltsp {  # Una imagen tipo ltsp puede ser un servidor de telefonica, una siatic, etc. Cualquiera que este
                       # en un aula con thinclients. Debe ser declarado con un facter propio ies_isltsp en /etc/escuela2.0
        "si","yes","true" : {
                file { "/usr/share/controlies-ltspserver/.ssh":
                        ensure => "directory"
                }
                file {"/usr/share/controlies-ltspserver/.ssh/id_rsa":
                        owner => root, group => root, mode => 600,
                        source => "puppet:///modules/ssh_confidence_controlies/id_rsa",
                        require => File["/usr/share/controlies-ltspserver/.ssh"]
                }
                #Servidores ltsp
        }
        default: {}
   }
}

