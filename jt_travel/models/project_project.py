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
#############################################################################
from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    proj_seq = fields.Char(string="Reference", copy=False, default='New')
    package_name = fields.Char("Package Name")
    number_of_passengers = fields.Integer("Number of Passengers")
    destination = fields.Char("Destination")
    travel_date_from = fields.Date("Travel Date From")
    travel_date_to = fields.Date("Travel Date To")
    client_price = fields.Monetary("Client Selling Price", currency_field='lead_currency_id')
    advance_payment = fields.Monetary("Advance / Payment Received", currency_field='lead_currency_id')

    lead_id = fields.Many2one('crm.lead', string="Lead")
    task_ids = fields.Many2many('project.task','project_task_rel',  'project_id','task_id',string="Tasks")
    document_count = fields.Integer(compute="_compute_document_count")
    lead_currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id,)
    lead_type_name = fields.Char(
        related='lead_id.lead_type_id.name', 
        string="Lead Type", 
        store=True
    )


    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        if self.env.context.get('travel_calendar'):
            self = self.with_context(force_travel_calendar=True)
        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order,**read_kwargs)


    def _compute_display_name(self):
        is_travel = self.env.context.get('force_travel_calendar')
        for rec in self:
            name = rec.name or ''
            if is_travel and rec.number_of_passengers:
                rec.display_name = f"{name} - [{rec.number_of_passengers} Pax]"
            else:
                rec.display_name = name

    

    @api.depends('task_ids')
    def _compute_document_count(self):
        for rec in self:
            task_ids = self.env['project.task'].search([
                ('project_id', '=', rec.id)
            ]).ids

            task_attachments = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'project.task'),
                ('res_id', 'in', task_ids),
            ])
            project_attachments = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'project.project'),
                ('res_id', '=', rec.id),
            ])
            rec.document_count = task_attachments + project_attachments

    def action_view_project_documents(self):
        self.ensure_one()
        task_ids = self.env['project.task'].search([
            ('project_id', '=', self.id)
        ]).ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': ['|',
                '&', ('res_model', '=', 'project.project'), ('res_id', '=', self.id),
                '&', ('res_model', '=', 'project.task'), ('res_id', 'in', task_ids),
            ],
            'context': {'create': False},
        }


    

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            if vals.get('name', 'New') == 'New' or not vals.get('proj_seq'):
                vals['proj_seq'] = self.env['ir.sequence'].sudo().next_by_code('project.project.travel.seq') or 'New'

        projects = super(Project, self).create(vals_list)

        for project in projects:
            if project.lead_id and project.lead_id.user_id:
                project.user_id = project.lead_id.user_id
            if not project.lead_id:
                continue

            stage_xmlids = [
                'jt_travel.task_type_assigned',
                'jt_travel.task_type_in_progress',
                'jt_travel.task_type_processing',
                'jt_travel.task_type_blocked',
                'jt_travel.task_type_completed',
                'jt_travel.task_type_booked',
                'jt_travel.task_type_confirmed',
            ]

            stages = self.env['project.task.type']
            for xmlid in stage_xmlids:
                stage = self.env.ref(xmlid, raise_if_not_found=False)
                if stage:
                    stages |= stage

            if stages:
                stages.sudo().write({'project_ids': [(4, project.id)]})
                
        return projects
    

    
    

    def action_create_and_view_project(self):
        self.ensure_one()
        return {
            'view_mode': 'form',
            'res_model': 'project.project',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'current', 
        }


