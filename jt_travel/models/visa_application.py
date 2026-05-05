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
from odoo import models, fields, api


class VisaApplicationContact(models.Model):
    _name = 'visa.application.contact'
    

    visa_application_id = fields.Many2one('travel.visa.application', string="Visa Application", ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string="Contacts" , domain=[('user_ids', '=', False)])
    application_number = fields.Char(string="Application Number")
    state = fields.Selection([
        ('in_process', 'In Process'),
        ('under_processing', 'Under Processing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string="Status", default='in_process', tracking=True)


class TravelVisaApplication(models.Model):
    _name = 'travel.visa.application'
    _description = 'Visa Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char(string="Reference", copy=False,default=lambda self: 'New')
    # application_number = fields.Char(string="Application Number")
    application_date = fields.Date(string="Application Date")
    visa_expected_date = fields.Date(string="Visa Expected Date")
    travel_date = fields.Date(string="Travel Date")
    number_of_passengers = fields.Html(string="Number of Passengers")
    destination = fields.Char(string="Destination")
    remark = fields.Text(string="Remark")
    lead_id = fields.Many2one('crm.lead', string="CRM Lead")
    task_id = fields.Many2one('project.task', string="Project Task")
    applicant_id = fields.Many2one('res.partner', string="Applicant")
    # state = fields.Selection([
    #     ('in_process', 'In Process'),
    #     ('under_processing', 'Under Processing'),
    #     ('approved', 'Approved'),
    #     ('rejected', 'Rejected'),
    # ], string="Status", default='in_process', tracking=True)
    assignee_id = fields.Many2one('res.users', string="Assignee")
    contact_ids = fields.One2many('visa.application.contact', 'visa_application_id', string="Contacts")
    

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        lead_id = defaults.get('lead_id') or self.env.context.get('default_lead_id')
        task_id = defaults.get('task_id') or self.env.context.get('default_task_id')
        if lead_id:
            lead = self.env['crm.lead'].browse(lead_id)
            if 'applicant_id' in fields_list and not defaults.get('applicant_id'):
                defaults['applicant_id'] = lead.partner_id.id if lead.partner_id else False
            if 'destination' in fields_list and not defaults.get('destination'):
                defaults['destination'] = lead.destination
            if 'number_of_passengers' in fields_list and not defaults.get('number_of_passengers'):
                defaults['number_of_passengers'] = lead.number_of_passengers
            if 'assignee_id' in fields_list and not defaults.get('assignee_id'):
                if task_id:
                    task = self.env['project.task'].browse(task_id)
                    if task.user_ids:
                        defaults['assignee_id'] = task.user_ids[0].id
                elif lead.user_id:
                    defaults['assignee_id'] = lead.user_id.id
            
            if lead_id:
                billing = self.env['travel.billing'].search(
                    [('lead_id', '=', lead_id)],
                    order='id desc',
                    limit=1
                )
                if billing:
                    if 'application_date' in fields_list and not defaults.get('application_date'):
                        defaults['application_date'] = billing.visa_applied_date or False
                    if 'visa_expected_date' in fields_list and not defaults.get('visa_expected_date'):
                        defaults['visa_expected_date'] = billing.visa_expected_date or False

            if 'travel_date' in fields_list and not defaults.get('travel_date'):
                defaults['travel_date'] = lead.travel_date_from or False

        return defaults


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('travel.visa.application') or 'New'
        return super().create(vals_list)