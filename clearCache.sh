#!/bin/bash
#
# Project:     ControlIES
# Description: Clear Cache
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
	rm -rf debian/controlies.debhelper.log
	rm -rf debian/controlies-thinclient.debhelper.log
	rm -rf debian/controlies-client.debhelper.log
	rm -rf debian/*.debhelper
	rm -rf debian/controlies.substvars
	rm -rf debian/controlies-thinclient.substvars
	rm -rf debian/controlies-client.substvars
	rm -rf debian/files
	find ./ -iname "*.pyc" -print0 | xargs -0 rm -rf
	find ./ -iname "*.*~" -print0 | xargs -0 rm -rf
}

clear_cache
