class ssh_confidence_controlies {

	file { "/root/.ssh/authorized_keys.controlies":
		source => "puppet:///ssh_confidence_controlies/id_rsa.pub",
		owner => root,
		mode => 600
        }

	exec { "add_controlies_key":
		path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
		command => "cat /root/.ssh/authorized_keys.controlies > /root/.ssh/authorized_keys",
		unless => "grep -f /root/.ssh/authorized_keys.controlies /root/.ssh/authorized_keys",
		require => File["/root/.ssh/authorized_keys.controlies"]
	}
}
