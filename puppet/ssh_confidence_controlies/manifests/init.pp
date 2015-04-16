class ssh_confidence_controlies {

        file { "/root/.ssh/authorized_keys.controlies":
                source => "puppet:///ssh_confidence_controlies/id_rsa.pub",
                owner => root,
                mode => 600
        }

        exec { "add_controlies_key":
                path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                command => "cat /root/.ssh/authorized_keys.controlies >> /root/.ssh/authorized_keys; chattr +i /root/.ssh/authorized_keys",
                unless => "grep -f /root/.ssh/authorized_keys.controlies /root/.ssh/authorized_keys",
                require => File["/root/.ssh/authorized_keys.controlies"]
        }

   case $use {
        #Servidores ltsp
        "ltsp-server", "ltsp-wheezy" : {
                file { "/usr/share/controlies-ltspserver/.ssh":
                        ensure => "directory"
                }
                file {"/usr/share/controlies-ltspserver/.ssh/id_rsa":
                        owner => root, group => root, mode => 600,
                        source => "puppet:///ssh_confidence_controlies/id_rsa",
                        require => File["/usr/share/controlies-ltspserver/.ssh"]
                }
        }
   }
}

