##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:    ValidationUtils.py
# Purpose:     Utils of validation
# Language:    Python 2.5
# Date:        3-Oct-2011.
# Ver:         3-Oct-2011.
# Author:	Manuel Mora Gordillo
# Copyright:    2011 - Manuel Mora Gordillo <manuito @no-spam@ gmail.com>
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
#
##############################################################################

def validIP(address):
    parts = address.split(".")
    if len(parts) != 4:
        return False
    for item in parts:
        if not 0 <= int(item) <= 255:
            return False
    return True

def validMAC(address):
    import re
    if re.match("[0-9a-f]{2}([-:][0-9a-f]{2}){5}$", address.lower()):
        return True
    return False
