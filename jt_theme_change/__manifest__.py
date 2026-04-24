# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Jupical Technologies(<http://www.jupical.io>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.io>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Theme Change",
    'version': '19.0.1.0.0',
    'author': "Jupical Technologies Pvt. Ltd.",
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'website': "https://www.jupical.io",
    'category': 'Theme',
    'depends': ['web','mail'],
    'data': [],
    "assets": {
        "web.assets_backend": [
            "jt_theme_change/static/src/scss/theme_change_backend.scss",
        ],
        'web.assets_frontend': [
            "jt_theme_change/static/src/scss/theme_change_frontend.scss",
        ],
    },
    'application':False,
    'installable':True,
    'auto_install':False
}

