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

class TravelVisaApplication(models.Model):
    _name = 'travel.visa.application'
    _description = 'Visa Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Reference", copy=False,default=lambda self: 'New')
    application_number = fields.Char(string="Application Number")
    application_date = fields.Date(string="Application Date")
    remark = fields.Text(string="Remark")
    lead_id = fields.Many2one('crm.lead', string="CRM Lead")
    task_id = fields.Many2one('project.task', string="Project Task")
    applicant_id = fields.Many2one('res.partner', string="Applicant")
    state = fields.Selection([
        ('in_process', 'In Process'),
        ('under_processing', 'Under Processing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string="Status", default='in_process', tracking=True)
    assignee_id = fields.Many2one('res.users', string="Assignee")
    

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('travel.visa.application') or 'New'

            if not vals.get('assignee_id'):
                task_id = vals.get('task_id')
                lead_id = vals.get('lead_id')
                if task_id:
                    task = self.env['project.task'].browse(task_id)
                    if task.user_ids:
                        vals['assignee_id'] = task.user_ids[0].id
                elif lead_id:
                    lead = self.env['crm.lead'].browse(lead_id)
                    if lead.user_id:
                        vals['assignee_id'] = lead.user_id.id
        return super().create(vals_list)