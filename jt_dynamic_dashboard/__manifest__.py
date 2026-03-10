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
    'name': "Jupical Dynamic Dashboard",
    'version': '19.0.1.0.0',
    'category': 'Extra Tools ',
    'summary': """Jupical Dynamic Dashboard""",
    'author': 'Jupical Technologies Pvt. Ltd.',
    'company': 'Jupical Technologies',
    'maintainer': 'Jupical Technologies',
    'website': 'https://jupical.io',
    'depends': ['web','contacts','jt_travel'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_view.xml',
        'views/dynamic_block_view.xml',
        'data/demo_data.xml',
        'views/config_settings_view.xml',
        'views/menu_items.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js',
            'jt_dynamic_dashboard/static/src/js/**/*.js',
            'jt_dynamic_dashboard/static/src/css/**/*.css',
            'jt_dynamic_dashboard/static/src/scss/**/*.scss',
            'jt_dynamic_dashboard/static/src/xml/**/*.xml',
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
    'application': False,
}
