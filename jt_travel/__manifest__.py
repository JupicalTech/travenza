# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies Pvt. Ltd.(<https://www.jupical.io>).
#    Author: Jupical Technologies Pvt. Ltd.(<https://www.jupical.io>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'JT Travel',
    'summary': 'Comprehensive Travel CRM and Operations Management for Travenza Holidays',
    'description': 'A comprehensive ERP solution for managing travel inquiries, specialized holiday quotations, automated project creation for bookings, and document-linked billing processes.',
    'version': '19.0.1.0.4',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'website': 'https://www.jupical.io',
    'license': 'LGPL-3',
    'depends': ['base', 'crm', 'mail', 'project', 'sale_project', 'web_datetime_widget', 'sale', 'sale_crm','crm_iap_enrich', 'sales_team', 'spreadsheet_oca', 'spreadsheet'],
    'data': [
        'security/security_groups.xml',
        'security/ir_rules.xml',
        'security/ir.model.access.csv',
        
        'data/ir_sequence_data.xml',

        'demo/lead_type_data.xml',
        'demo/demo_tasks.xml',
        'demo/demo_task_stages.xml',
        'demo/crm_stages.xml',
        'demo/crm_tags.xml',

        'wizard/project_wizard_view.xml',
        'wizard/spreadsheet_task_wizard_view.xml',
        'wizard/project_quotation_bulk_wizard_view.xml',

        'views/lead_type_views.xml',
        'views/crm_lead_inh_view.xml',
        'views/travel_team_views.xml',
        'views/project_views_inh.xml',
        'views/task_views_inh.xml',
        'views/travel_quotation_view.xml',
        'views/travel_billing_views.xml',
        'views/visa_application_view.xml',
        'views/spreadsheet_inh_view.xml',

    ],
    'assets': {
    'web.assets_backend': [
        'jt_travel/static/src/xml/template_inheritance.xml',
        'jt_travel/static/src/js/activity_patch.js',
        'jt_travel/static/src/css/priority_colors.css',
    ],
},
    'application': True,
    'installable': True,
    'auto_install': False,
}
