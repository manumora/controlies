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

   #file {"/usr/lib/ruby/vendor_ruby/facter/file_exists.rb":
   #                             owner => root, group => root, mode => 644,
   #                             source => "puppet:///modules/instala_controlies/file_exits.rb",
   #}

   if file_exists ("/opt/ltsp/images/i386.img") == 1 {
        $tipo_imagen="ltsp"
   } else {
        $tipo_imagen="otro"
   }


   case $tipo_imagen {
        #Servidores ltsp
        "ltsp" : {
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

