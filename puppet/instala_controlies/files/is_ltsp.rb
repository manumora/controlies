# Archivo /usr/lib/ruby/vendor_ruby/facter/is_ltsp.rbb
# Se utiliza para determinar si el equipo es LTSP comprobando
# la existencia de /opt/ltsp/images/i386.img

if File.exists?("/opt/ltsp/images/i386.img")
   Facter.add("IS_LTSP") do
            setcode { "SI" }
   end
else
   Facter.add("IS_LTSP") do
            setcode { "NO" }
   end
end
####

