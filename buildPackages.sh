#!/bin/bash
#
# Project:     ControlIES
# Description: Building packages and puppet module regeneration
# Language:    Bash
# Date:        19-Nov-2013.
# Author: Manuel Mora Gordillo
# Copyright:   2013 - Manuel Mora Gordillo    <manuel.mora.gordillo @nospam@ gmail.com>
#
# ControlIES is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ControlIES is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with ControlIES. If not, see <http://www.gnu.org/licenses/>.


clear_cache(){
	rm -rf applications/controlies/cache/*
	rm -rf applications/controlies/databases/*
	rm -rf applications/controlies/errors/*
	rm -rf applications/controlies/private/*
	rm -rf applications/controlies/sessions/*
	rm -rf debian/controlies
	rm -rf debian/controlies-thinclient
	rm -rf debian/controlies-client
	rm -rf debian/controlies-ltspserver
	rm -rf debian/controlies.debhelper.log
	rm -rf debian/controlies-thinclient.debhelper.log
	rm -rf debian/controlies-client.debhelper.log
	rm -rf debian/controlies-ltspserver.debhelper.log
	rm -rf debian/*.debhelper
	rm -rf debian/controlies.substvars
	rm -rf debian/controlies-thinclient.substvars
	rm -rf debian/controlies-client.substvars
	rm -rf debian/controlies-ltspserver.substvars
	rm -rf debian/files
	find ./ -iname "*.pyc" -print0 | xargs -0 rm -rf
	find ./ -iname "*.*~" -print0 | xargs -0 rm -rf
}

clear_packages(){
	rm ../controlies*.deb
	rm ../controlies*.dsc
	rm ../controlies*.changes
	rm ../controlies*.tar.gz
}

fzip() {
    zip -r $1 $1
}

clear_cache
clear_packages
dpkg-buildpackage -b

git rm ./packages/*.deb
#rm ./packages/*.deb
mkdir packages
mv ../controlies*.deb ./packages
git add ./packages/*.deb -v

clear_packages
clear_cache

git rm ./puppet/instala_controlies/files/*.deb
#rm ./puppet/instala_controlies/files/*.deb
mkdir ./puppet/instala_controlies/files
cp ./packages/*.deb ./puppet/instala_controlies/files
git add ./puppet/instala_controlies/files/*.deb -v

# Reemplaza la nueva version en init.pp
VERSION=`echo ./packages/controlies_* | cut -d'_' -f2`
sed -i.bak "s/version=\".*\"/version=\"${VERSION}\"/g" ./puppet/instala_controlies/manifests/init.pp
rm ./puppet/instala_controlies/manifests/init.pp.bak

rm ./puppet/instala_controlies.zip
cd ./puppet
fzip instala_controlies
cd ../
git add ./puppet/instala_controlies.zip -v
