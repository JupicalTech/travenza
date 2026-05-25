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
from odoo.exceptions import UserError

class Project(models.Model):
    _inherit = 'project.project'

    proj_seq = fields.Char(string="Reference", copy=False, default='New')
    package_name = fields.Char("Package Name")
    number_of_passengers = fields.Html("Number of Passengers")
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
 
    spreadsheet_ids = fields.One2many(
        'spreadsheet.spreadsheet',
        'project_id',
        string="Spreadsheets",
    )
    spreadsheet_count = fields.Integer(compute='_compute_spreadsheet_count',string="Spreadsheets")

   
 
    @api.depends('lead_id', 'spreadsheet_ids')
    def _compute_spreadsheet_count(self):
        for rec in self:
            if rec.lead_id:
                rec.spreadsheet_count = self.env['spreadsheet.spreadsheet'].search_count([
                    ('lead_id', '=', rec.lead_id.id)
                ])
            else:
                rec.spreadsheet_count = len(rec.spreadsheet_ids)
 
   

    def action_view_spreadsheets(self):
        self.ensure_one()
        if self.lead_id:
            domain = [('lead_id', '=', self.lead_id.id)]
        else:
            domain = [('project_id', '=', self.id)]

        spreadsheets = self.env['spreadsheet.spreadsheet'].search(domain)
        
        ctx = {
            'default_project_id': self.id,
            'default_lead_id': self.lead_id.id if self.lead_id else False,
            'create': False,
            'from_project': True,
        }

        if len(spreadsheets) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Spreadsheets',
                'res_model': 'spreadsheet.spreadsheet',
                'view_mode': 'form',
                'res_id': spreadsheets.id,
                'context': ctx,
            }

        return {
            'type': 'ir.actions.act_window',
            'name': 'Spreadsheets',
            'res_model': 'spreadsheet.spreadsheet',
            'view_mode': 'list,form',
            'domain': domain,
            'context': ctx,
        }

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



    quotation_line_ids = fields.One2many(
        'project.quotation.line',
        'project_id',
        string="Quotation Lines",
    )

    def action_load_confirmed_quotation_lines(self):
        self.ensure_one()
        if not self.lead_id:
            return
        confirmed = self.env['spreadsheet.spreadsheet'].search([
            ('lead_id', '=', self.lead_id.id),
            ('is_done', '=', True),
        ], limit=1)
        if not confirmed:
            return
        rows = confirmed._parse_spreadsheet_rows()
        self.quotation_line_ids.unlink()
        for i, row in enumerate(rows):
            self.env['project.quotation.line'].create({
                'project_id': self.id,
                'sequence': (i + 1) * 10,
                'date': row.get('date', ''),
                'description': row.get('description', ''),
                'price': row.get('price', 0.0), 
                'booked_price': row.get('booked_price', 0.0),
                'remark': row.get('remarks', ''),
                'vendor_reference': row.get('vendor_reference', ''),
                'mode_of_payment': row.get('mode_of_payment', ''),
            })

    def _sync_confirmed_quotation_lines(self):
        for rec in self:
            if not rec.lead_id:
                continue
            confirmed = self.env['spreadsheet.spreadsheet'].search([
                ('lead_id', '=', rec.lead_id.id),
                ('is_done', '=', True),
            ], limit=1)
            if not confirmed:
                continue
            existing_descs = rec.quotation_line_ids.mapped('description')
            max_seq = max(rec.quotation_line_ids.mapped('sequence') or [0])
            try:
                rows = confirmed._parse_spreadsheet_rows()
            except Exception:
                continue
            counter = max_seq + 10
            for i, row in enumerate(rows):
                if row.get('description') and row['description'] not in existing_descs:
                    self.env['project.quotation.line'].create({
                        'project_id': rec.id,
                        'sequence': (i + 1) * 10,
                        'date': row.get('date', ''),
                        'description': row.get('description', ''),
                        'price': row.get('price', 0.0),
                        'booked_price': row.get('booked_price', 0.0),
                        'remark': row.get('remarks', ''),
                        'vendor_reference': row.get('vendor_reference', ''),
                        'mode_of_payment': row.get('mode_of_payment', ''),
                    })

    def action_bulk_assign_quotation_lines(self):
        self.ensure_one()
        selected = self.quotation_line_ids.filtered(lambda l: l.selected)
        if not selected:
            raise UserError("Please select at least one line first.")
        bulk = self.env['project.quotation.bulk.wizard'].create({
            'project_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bulk Assign',
            'res_model': 'project.quotation.bulk.wizard',
            'res_id': bulk.id,
            'view_mode': 'form',
            'target': 'new',
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

            if project.lead_id:
                project.action_load_confirmed_quotation_lines()

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


