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
from odoo.addons.project.models.project_task import CLOSED_STATES
from odoo.exceptions import UserError

JT_CUSTOM_STATES = {
    '05_task_assigned', '06_processing', '07_blocked',
    '08_completed', '09_booked', '10_confirmed'
}

class ProjectTask(models.Model):
    _inherit = 'project.task'

    lead_id = fields.Many2one('crm.lead',string="Lead",ondelete='set null')
    lead_type_id = fields.Many2one('lead.type',string='Lead Type',store=True)
    document_count = fields.Integer(compute="_compute_document_count")

    lead_customer_name = fields.Char(compute='_compute_lead_info', string='Customer Name')
    lead_customer_email = fields.Char(compute='_compute_lead_info', string='Email')
    lead_customer_phone = fields.Char(compute='_compute_lead_info', string='Phone')
    lead_salesperson_id = fields.Many2one('res.users', compute='_compute_lead_info', string='Salesperson')

    billing_count = fields.Integer(compute='_compute_billing_count', string="Billings")
    can_create_billing = fields.Boolean(compute='_compute_can_create_billing')
    is_visa_type = fields.Boolean(string="Is Visa Task", default=False)
    task_service_type = fields.Char(string="Service Type")
    visa_application_ids = fields.One2many('travel.visa.application', 'task_id', string="Visa Applications")
    visa_count = fields.Integer(compute='_compute_visa_count')
    task_date = fields.Char(string="Date")
    task_price = fields.Float(string="Price", digits=(12, 2)) 
    number_of_passengers = fields.Html(
        string="Number of Passengers",
        compute="_compute_number_of_passengers",
        inverse="_inverse_number_of_passengers",
        readonly=False,
        store=True
    )


    @api.depends('project_id.number_of_passengers', 'lead_id.number_of_passengers')
    def _compute_number_of_passengers(self):
        for rec in self:
            if rec.project_id.number_of_passengers:
                rec.number_of_passengers = rec.project_id.number_of_passengers
            elif rec.lead_id.number_of_passengers:
                rec.number_of_passengers = rec.lead_id.number_of_passengers

    def _inverse_number_of_passengers(self):
        pass
  

    def _compute_visa_count(self):
        for rec in self:
            rec.visa_count = len(rec.visa_application_ids)

    def action_create_visa_application(self):
        lead = self.lead_id or (self.project_id.lead_id if self.project_id else False)
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Visa Application',
            'res_model': 'travel.visa.application',
            'view_mode': 'form',
            'context': {
            'default_task_id': self.id,
            'default_lead_id': lead.id if lead else False,
            'default_assignee_id': self.user_ids[0].id if self.user_ids else False,
            'default_applicant_id': lead.partner_id.id if lead and lead.partner_id else False,
            'default_destination': lead.destination if lead else False,
            'default_number_of_passengers': lead.number_of_passengers if lead else False,
        },
            'target': 'current',
        }
    

    def action_view_visa_applications(self):
        self.ensure_one()
        lead = self.lead_id or (self.project_id.lead_id if self.project_id else False)
        domain = ['|', ('task_id', '=', self.id), ('lead_id', '=', lead.id if lead else False)]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Visa Applications',
            'res_model': 'travel.visa.application',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {
                'default_task_id': self.id,
                'default_lead_id': lead.id if lead else False,
            },
        }

    @api.model_create_multi
    def create(self, vals_list):
        visa_type = self.env.ref('jt_travel.lead_type_visa_assistance', raise_if_not_found=False)
        
        for vals in vals_list:
            if visa_type and vals.get('lead_type_id') == visa_type.id:
                vals['is_visa_type'] = True
        return super().create(vals_list)
    
   
    

    @api.depends('lead_id', 'project_id.lead_id')
    def _compute_lead_info(self):
        for rec in self:
            lead = rec.lead_id or (rec.project_id.lead_id if rec.project_id else False)
            if lead:
                rec.lead_customer_name = lead.partner_id.name if lead.partner_id else ''
                rec.lead_customer_email = lead.partner_id.email if lead.partner_id else ''
                rec.lead_customer_phone = lead.partner_id.phone if lead.partner_id else ''
                rec.lead_salesperson_id = lead.user_id
            else:
                rec.lead_customer_name = ''
                rec.lead_customer_email = ''
                rec.lead_customer_phone = ''
                rec.lead_salesperson_id = False

    def _compute_document_count(self):
        for rec in self:
            rec.document_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'project.task'),
                ('res_id', '=', rec.id),
            ])


    @api.depends('lead_id', 'project_id.lead_id')
    def _compute_billing_count(self):
        for rec in self:
            lead = rec.lead_id or (rec.project_id.lead_id if rec.project_id else False)
            if lead:
                rec.billing_count = self.env['travel.billing'].search_count([
                    ('lead_id', '=', lead.id)
                ])
            else:
                rec.billing_count = 0

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        if self.env.context.get('jt_travel_tasks'):
            stage_xmlids = [
                'jt_travel.task_type_assigned',
                'jt_travel.task_type_in_progress',
                'jt_travel.task_type_processing',
                'jt_travel.task_type_confirmed',
            ]
            travenza_stages = self.env['project.task.type']
            for xmlid in stage_xmlids:
                stage = self.env.ref(xmlid, raise_if_not_found=False)
                if stage:
                    travenza_stages |= stage
            return travenza_stages
        return super()._read_group_stage_ids(stages, domain)
    
    

    @api.depends(
        'stage_id', 
        'lead_id', 
        'project_id.lead_id', 
        'lead_type_id.is_project_type'
    )
    def _compute_can_create_billing(self):
        processing_stage = self.env.ref('jt_travel.task_type_processing', raise_if_not_found=False)
        processing_seq = processing_stage.sequence if processing_stage else 3
 
        for rec in self:
            lead = rec.lead_id or (rec.project_id.lead_id if rec.project_id else False)
            
            is_package = bool(
                lead and 
                lead.lead_type_id and 
                lead.lead_type_id.is_project_type
            )
            stage_ok = bool(rec.stage_id and rec.stage_id.sequence >= processing_seq)
            
            rec.can_create_billing = is_package and stage_ok



    def action_view_task_documents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [
                ('res_model', '=', 'project.task'),
                ('res_id', '=', self.id),
            ],
            'context': {'create': False},
        }
    

    def action_create_billing(self):
        self.ensure_one()
        lead = self.lead_id or (self.project_id.lead_id if self.project_id else False)
        if not lead:
            raise UserError("No lead found for this task. Cannot create a billing form.")
        
        billing = self.env['travel.billing'].create({
            'lead_id': lead.id,
            'passenger_name': lead.contact_name or (lead.partner_id.name if lead.partner_id else ''),
            'billing_type_name': self.task_service_type or lead.lead_type_id.name,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Billing Form',
            'res_model': 'travel.billing',
            'view_mode': 'form',
            'res_id': billing.id,
            'target': 'current',
        }
 
    def action_view_billings(self):
        self.ensure_one()
        lead = self.lead_id or (self.project_id.lead_id if self.project_id else False)
        domain = [('lead_id', '=', lead.id)] if lead else [('id', '=', False)]
        ctx = {}
        if lead:
            ctx['default_lead_id'] = lead.id
            ctx['default_billing_type_name'] = self.task_service_type or (lead.lead_type_id.name if lead.lead_type_id else False)
            ctx['default_passenger_name'] = lead.contact_name or (lead.partner_id.name if lead.partner_id else False)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Billing Forms',
            'res_model': 'travel.billing',
            'view_mode': 'list,form',
            'domain': domain,
            'context': ctx,
        }
    
    def action_save_and_view_lead_tasks(self):
        self.ensure_one()
        lead = self.lead_id or (self.project_id.lead_id if self.project_id else False)
        if not lead:
            return

        direct_task_ids = self.env['project.task'].search([
            ('lead_id', '=', lead.id)
        ]).ids
        project_task_ids = self.env['project.task'].search([
            ('project_id.lead_id', '=', lead.id)
        ]).ids
        all_task_ids = list(set(direct_task_ids) | set(project_task_ids))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('id', 'in', all_task_ids)],
            'context': {'default_lead_id': lead.id},
            'target': 'main',  
        }



    