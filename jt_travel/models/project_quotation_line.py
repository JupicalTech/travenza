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
from odoo import models, fields, api

class ProjectQuotationLine(models.Model):
    _name = 'project.quotation.line'
    _description = 'Project Quotation Line'
    _order = 'sequence, id'

    project_id = fields.Many2one('project.project', string="Project", ondelete='cascade')
    selected = fields.Boolean(string="Select", default=False)
    sequence = fields.Integer(default=10)
    date = fields.Char(string="Date", tracking=True)
    description = fields.Char(string="Description")
    price = fields.Float(string="Est. Price", digits=(12, 2))
    booked_price = fields.Monetary(string="Booked Price", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    vendor_reference = fields.Char(string="Vendor Reference")
    mode_of_payment = fields.Char(string="Mode of Payment")
    remark = fields.Char(string="Remarks")
    lead_type_id = fields.Many2one('lead.type', string="Lead Type", options="{'no_create': True}")
    available_assignee_ids = fields.Many2many(
        'res.users',
        'proj_quot_line_avail_user_rel',
        'line_id', 'user_id',
        compute='_compute_available_assignee_ids',
        string="Available Assignees",
    )
    assignee_ids = fields.Many2many(
        'res.users',
        'proj_quot_line_user_rel',
        'line_id', 'user_id',
        string="Assignees",
    )
    stage_id = fields.Many2one(
        'project.task.type',
        string="Task Stage",
        domain=lambda self: [('id', 'in', [
            s.id for s in [
                self.env.ref('jt_travel.task_type_assigned', raise_if_not_found=False),
                self.env.ref('jt_travel.task_type_in_progress', raise_if_not_found=False),
                self.env.ref('jt_travel.task_type_processing', raise_if_not_found=False),
                self.env.ref('jt_travel.task_type_confirmed', raise_if_not_found=False),
            ] if s
        ])]
    )


    

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('sequence') and vals.get('project_id'):
                max_seq = max(
                    self.search([('project_id', '=', vals['project_id'])]).mapped('sequence') or [0]
                )
                vals['sequence'] = max_seq + 10
        return super().create(vals_list)
  

    @api.depends('lead_type_id')
    def _compute_available_assignee_ids(self):
        for rec in self:
            if rec.lead_type_id and rec.lead_type_id.team_ids:
                teams = rec.lead_type_id.team_ids
                rec.available_assignee_ids = teams.mapped('member_ids') | teams.mapped('team_leader_id')
            else:
                rec.available_assignee_ids = self.env['res.users']

    @api.onchange('lead_type_id')
    def _onchange_lead_type_id(self):
        self.assignee_ids = [(5, 0, 0)]
        if not self.lead_type_id or not self.project_id:
            return

        current_origin_id = self._origin.id
        for line in self.project_id.quotation_line_ids:
            if line._origin.id and line._origin.id == current_origin_id:
                continue
            line_lead_type = line._origin.lead_type_id or line.lead_type_id
            line_assignees = line._origin.assignee_ids or line.assignee_ids
            if line_lead_type == self.lead_type_id and line_assignees:
                self.assignee_ids = [(6, 0, (line._origin.assignee_ids or line.assignee_ids).ids)]
                break