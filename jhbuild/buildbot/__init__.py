# jhbuild - a build script for GNOME 1.x and 2.x
# Copyright (C) 2008  apinheiro@igalia.com, John Carr, Frederic Peters
#
#   __init__.py: utility functions for master.cfg
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import jhbuild.moduleset

def jhbuild_list():
    module_set = jhbuild.moduleset.load(jhbuild_config)
    module_list = module_set.get_module_list(
            jhbuild_config.modules,
            jhbuild_config.skip,
            include_optional_modules=True)
    return [x.name for x in module_list if not x.name.startswith('meta-')]