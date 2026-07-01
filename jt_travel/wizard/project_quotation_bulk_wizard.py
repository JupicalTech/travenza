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
from odoo.exceptions import UserError

class ProjectQuotationBulkWizard(models.TransientModel):
    _name = 'project.quotation.bulk.wizard'
    _description = 'Bulk Assign Lead Type and Assignees to Quotation Lines'

    project_id = fields.Many2one('project.project', required=True, ondelete='cascade')
    lead_type_id = fields.Many2one('lead.type', string="Lead Type")
    available_assignee_ids = fields.Many2many(
        'res.users',
        'proj_quot_bulk_avail_rel',
        'wizard_id', 'user_id',
        compute='_compute_available_assignee_ids',
        string="Available Assignees",
    )
    assignee_ids = fields.Many2many(
        'res.users',
        'proj_quot_bulk_user_rel',
        'wizard_id', 'user_id',
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
    selected_count = fields.Integer(compute='_compute_selected_count')

    @api.depends('project_id.quotation_line_ids.selected')
    def _compute_selected_count(self):
        for rec in self:
            rec.selected_count = len(rec.project_id.quotation_line_ids.filtered(lambda l: l.selected))

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

    def action_apply(self):
        self.ensure_one()
        if not self.lead_type_id:
            raise UserError("Please select a Lead Type.")
        lines = self.project_id.quotation_line_ids.filtered(lambda l: l.selected)
        if not lines:
            raise UserError("No lines selected.")
        vals = {
            'lead_type_id': self.lead_type_id.id,
            'assignee_ids': [(6, 0, self.assignee_ids.ids)],
            'selected': False,
        }
        if self.stage_id:
            vals['stage_id'] = self.stage_id.id
        lines.write(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }