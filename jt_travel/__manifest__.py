# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
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
    'name': 'JT Travel',
    'summary': 'Travel CRM',
    'version': '19.0.1.0.0',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'website': 'https://www.jupical.io',
    'license': 'LGPL-3',
    'depends': ['base', 'crm', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        


        'demo/lead_type_data.xml',
        'demo/visa_type_data.xml',

        'data/sequence.xml',

        'views/lead_type_view.xml',
        'views/country_checklist_view.xml',
        'views/customer_visa_application_view.xml',
        'views/customer_booking_view.xml',
        'views/crm_lead_inh_view.xml',
        'views/visa_type_view.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
