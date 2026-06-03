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
from odoo import api, fields, models
from odoo.exceptions import UserError


class SpreadsheetTaskWizardLine(models.Model):
    _name = 'spreadsheet.task.wizard.line'
    _description = 'Spreadsheet Task Wizard Line'

    wizard_id = fields.Many2one('spreadsheet.task.wizard', ondelete='cascade')

    date = fields.Char(string='Date')
    description = fields.Char(string='Description')
    remarks     = fields.Char(string='Remarks')

    lead_type_id = fields.Many2one('lead.type', string='Lead Type')
    price = fields.Float(string='Price', digits=(12, 2))

    available_assignee_ids = fields.Many2many(
        'res.users',
        'wizard_line_avail_assignee_rel',
        'line_id', 'user_id',
        compute='_compute_available_assignee_ids',
        string='Available Assignees',
    )
    assignee_ids = fields.Many2many(
        'res.users',
        'wizard_line_assignee_rel',
        'line_id', 'user_id',
        string='Assignees',
    )

    already_exists = fields.Boolean(default=False)
    selected = fields.Boolean(string='Select', default=False)

    @api.depends('lead_type_id')
    def _compute_available_assignee_ids(self):
        for rec in self:
            if rec.lead_type_id and rec.lead_type_id.team_ids:
                teams = rec.lead_type_id.team_ids
                rec.available_assignee_ids = (
                    teams.mapped('member_ids') | teams.mapped('team_leader_id')
                )
            else:
                rec.available_assignee_ids = self.env['res.users']

    @api.onchange('lead_type_id')
    def _onchange_lead_type_id(self):
        self.assignee_ids = [(5, 0, 0)]
        if not self.lead_type_id or not self.wizard_id:
            return

        current_id = self._origin.id 
        first_matching_line = None
        for line in self.wizard_id.line_ids:
            if line._origin.id and line._origin.id == current_id:
                continue
            line_lead_type = line._origin.lead_type_id or line.lead_type_id
            line_assignees = line._origin.assignee_ids or line.assignee_ids
            if line_lead_type == self.lead_type_id and line_assignees:
                first_matching_line = line
                break

        if first_matching_line:
            assignee_ids = (
                first_matching_line._origin.assignee_ids.ids
                or first_matching_line.assignee_ids.ids
            )
            self.assignee_ids = [(6, 0, assignee_ids)]


class SpreadsheetTaskWizard(models.Model):
    _name = 'spreadsheet.task.wizard'
    _description = 'Create Tasks'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _rec_name = "project_id"
 
    spreadsheet_id = fields.Many2one('spreadsheet.spreadsheet')
    project_id     = fields.Many2one('project.project')
 
    line_ids = fields.One2many('spreadsheet.task.wizard.line', 'wizard_id', string='Rows')
 
    pending_line_ids = fields.One2many(
        'spreadsheet.task.wizard.line',
        'wizard_id',
        string='Pending Rows',
        domain=[('already_exists', '=', False)],
    )
 
    created_line_ids = fields.One2many(
        'spreadsheet.task.wizard.line',
        'wizard_id',
        string='Tasks Already Created',
        domain=[('already_exists', '=', True)],
    )
 
    def action_create_tasks(self):
        self.ensure_one()
        project = self.project_id
        lead    = project.lead_id

        lines_to_create = self.line_ids.filtered(
            lambda l: l.lead_type_id and l.assignee_ids and not l.already_exists
        )

        if not lines_to_create:
            raise UserError(
                "No rows have both Lead Type and Assignees filled in. "
                "Please fill those columns for the rows you want to create tasks for."
            )

        tasks_created = self.env['project.task']
        for line in lines_to_create:
            task_vals = {
                'name':              line.description,
                'project_id':        project.id,
                'lead_id':           lead.id if lead else False,
                'lead_type_id':      line.lead_type_id.id,
                'task_service_type': line.lead_type_id.name,
                'task_date':         line.date or '',
                'task_price':        line.price,
                'user_ids':          [(6, 0, line.assignee_ids.ids)],
            }
            if lead and lead.partner_id:
                task_vals['partner_id'] = lead.partner_id.id
            tasks_created |= self.env['project.task'].sudo().create(task_vals)

        lines_to_create.sudo().write({'already_exists': True})
        
        all_project_task_ids = self.env['project.task'].sudo().search([
            ('project_id', '=', project.id)
        ]).ids

        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('id', 'in', all_project_task_ids)],
            'target': 'current',
            'effect': {
                'fadeout': 'slow',
                'message': f"Success! {len(tasks_created)} task(s) created.",
                'type': 'rainbow_man',
            },
        }
    

    def action_open_bulk_assign(self):
        self.ensure_one()
        selected = self.line_ids.filtered(
            lambda l: l.selected and not l.already_exists
        )
        if not selected:
            raise UserError(
                "Please tick the 'Select' checkbox on at least one row first."
            )
        bulk = self.env['spreadsheet.bulk.assign.wizard'].create({
            'parent_wizard_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bulk Assign',
            'res_model': 'spreadsheet.bulk.assign.wizard',
            'res_id': bulk.id,
            'view_mode': 'form',
            'target': 'new',
        }
    

class SpreadsheetBulkAssignWizard(models.TransientModel):
    _name = 'spreadsheet.bulk.assign.wizard'
    _description = 'Bulk Assign Lead Type and Assignees'

    parent_wizard_id = fields.Many2one(
        'spreadsheet.task.wizard',
        required=True,
        ondelete='cascade',
    )
    lead_type_id = fields.Many2one('lead.type', string='Lead Type')
    available_assignee_ids = fields.Many2many(
        'res.users',
        'bulk_assign_avail_assignee_rel',
        'wizard_id', 'user_id',
        compute='_compute_available_assignee_ids',
        string='Available Assignees',
    )
    assignee_ids = fields.Many2many(
        'res.users',
        'bulk_assign_assignee_rel',
        'wizard_id', 'user_id',
        string='Assignees',
    )
    selected_count = fields.Integer(compute='_compute_selected_count', string='Selected Lines')

    @api.depends('parent_wizard_id.line_ids.selected',
                 'parent_wizard_id.line_ids.already_exists')
    def _compute_selected_count(self):
        for rec in self:
            rec.selected_count = len(rec.parent_wizard_id.line_ids.filtered(
                lambda l: l.selected and not l.already_exists
            ))

    @api.depends('lead_type_id')
    def _compute_available_assignee_ids(self):
        for rec in self:
            if rec.lead_type_id and rec.lead_type_id.team_ids:
                teams = rec.lead_type_id.team_ids
                rec.available_assignee_ids = (
                    teams.mapped('member_ids') | teams.mapped('team_leader_id')
                )
            else:
                rec.available_assignee_ids = self.env['res.users']

    @api.onchange('lead_type_id')
    def _onchange_lead_type_id(self):
        self.assignee_ids = [(5, 0, 0)]

    def action_apply(self):
        self.ensure_one()
        if not self.lead_type_id:
            raise UserError("Please select a Lead Type before applying.")
        lines = self.parent_wizard_id.line_ids.filtered(
            lambda l: l.selected and not l.already_exists
        )
        if not lines:
            raise UserError("No lines are selected.")
        lines.write({
            'lead_type_id': self.lead_type_id.id,
            'assignee_ids': [(6, 0, self.assignee_ids.ids)],
            'selected': False,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Tasks',
            'res_model': 'spreadsheet.task.wizard',
            'res_id': self.parent_wizard_id.id,
            'view_mode': 'form',
            'target': 'current',
        }