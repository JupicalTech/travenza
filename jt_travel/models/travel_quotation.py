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
from markupsafe import Markup
from odoo.exceptions import UserError

class TravelQuotation(models.Model):
    _name = 'travel.quotation'
    _description = 'Travel Quotation'
    _rec_name="name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    lead_id = fields.Many2one('crm.lead', string="Opportunity")
    name = fields.Char(string="Reference", copy=False, default='New')
    version = fields.Char(
        string="Version", 
        compute="_compute_version", 
        store=True, 
        copy=False,
    )

    destination = fields.Char(related='lead_id.destination', store=True)
    travel_date_from = fields.Date(related='lead_id.travel_date_from', store=True)
    travel_date_to = fields.Date(related='lead_id.travel_date_to', store=True)
    number_of_passengers = fields.Html(related='lead_id.number_of_passengers', store=True)
    lead_type_id = fields.Many2one('lead.type', related='lead_id.lead_type_id', store=True)
    is_holiday_type = fields.Boolean(compute='_compute_is_holiday_type', store=True)
    is_project_type = fields.Boolean(compute='_compute_is_project_type', store=True)
    has_project = fields.Boolean(compute='_compute_has_project')
    is_lead_won = fields.Boolean(compute='_compute_is_lead_won')
    currency_id = fields.Many2one('res.currency',default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many('travel.quotation.line','quotation_id',string="Quotation Lines", copy=True)

    markup = fields.Float(string="Markup", tracking=True)
    client_cost = fields.Monetary(string="Client Cost",compute="_compute_client_cost",store=True,tracking=True,currency_field='currency_id')
    total_amount = fields.Monetary(string="Net Cost",compute="_compute_total",store=True,currency_field='currency_id')
    working = fields.Html(string="Working")
    task_count = fields.Integer(string="Tasks", compute='_compute_task_count')
    assign_to_id = fields.Many2one('res.users', string="Assign To", tracking=True)
    is_only_assignee = fields.Boolean(compute='_compute_is_only_assignee')

    def _compute_is_only_assignee(self):
        for rec in self:
            is_assignee = rec.assign_to_id and rec.assign_to_id.id == self.env.uid
            is_lead_owner = rec.lead_id and rec.lead_id.user_id and rec.lead_id.user_id.id == self.env.uid
            rec.is_only_assignee = bool(is_assignee and not is_lead_owner)
 


    @api.depends('lead_id')
    def _compute_version(self):
        for rec in self:
            if not rec.lead_id:
                rec.version = "1"
                continue
            if rec.version and rec.version != "1":
                continue

            domain = [('lead_id', '=', rec.lead_id.id)]
            if rec.ids and isinstance(rec.id, int):
                domain.append(('id', '!=', rec.id))
            elif rec._origin.id:
                domain.append(('id', '!=', rec._origin.id))
            existing_count = self.env['travel.quotation'].sudo().search_count(domain)
            rec.version = str(existing_count + 1)
                

    @api.depends('lead_id')
    def _compute_task_count(self):
        for rec in self:
            if rec.lead_id:
                rec.task_count = self.env['project.task'].search_count([('lead_id', '=', rec.lead_id.id)])
            else:
                rec.task_count = 0

    
    @api.depends('lead_type_id')
    def _compute_is_holiday_type(self):
        holiday_type = self.env.ref('jt_travel.lead_type_holiday_package', raise_if_not_found=False)
        for rec in self:
            is_holiday = bool(holiday_type and rec.lead_type_id == holiday_type)
            rec.is_holiday_type = is_holiday


    @api.depends('lead_type_id')
    def _compute_is_project_type(self):
        holiday_ref = self.env.ref('jt_travel.lead_type_holiday_package', raise_if_not_found=False)
        corporate_ref = self.env.ref('jt_travel.lead_type_corporate_group', raise_if_not_found=False)
        
        for rec in self:
            is_holiday = bool(holiday_ref and rec.lead_type_id == holiday_ref)
            is_corporate = bool(corporate_ref and rec.lead_type_id == corporate_ref)
            rec.is_project_type = is_holiday or is_corporate

    @api.depends('lead_id')
    def _compute_has_project(self):
        for rec in self:
            if rec.lead_id:
                project_count = self.env['project.project'].search_count([('lead_id', '=', rec.lead_id.id)])
                rec.has_project = project_count > 0
            else:
                rec.has_project = False

    @api.depends('lead_id.stage_id')
    def _compute_is_lead_won(self):
        for rec in self:
            rec.is_lead_won = bool(rec.lead_id and rec.lead_id.stage_id and rec.lead_id.stage_id.is_won)


    @api.depends('line_ids.price')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(line.price for line in rec.line_ids)

    @api.depends('total_amount', 'markup')
    def _compute_client_cost(self):
        for rec in self:
            rec.client_cost = rec.total_amount + rec.markup

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                generated_name = self.env['ir.sequence'].next_by_code('travel.quotation.seq')
                vals['name'] = generated_name or 'New'

        records = super(TravelQuotation, self).create(vals_list)

        for record in records:
            record.message_post(body=Markup("<b>Travel Quotation created.</b>"))
            if record.lead_id:
                record.lead_id.message_post(body=Markup("<b>New Travel Quotation Created</b>"))
                
        return records

    
    def write(self, vals):
        for record in self:
            changed_lines = []
            for field_name, new_value in vals.items():
                change_vals = self._fields.get(field_name)
                if change_vals:
                    label = change_vals.string or field_name
                    changed_lines.append(f"<li><b>{label}</b> was updated.</li>")

            if changed_lines:
                body = Markup("<b> Travel Quotation Updated:</b><ul>{}</ul>").format(
                    Markup("".join(changed_lines))
                )
                record.message_post(
                    body=body,
                    subtype_xmlid="mail.mt_note"
                )
        return super().write(vals)




    def action_view_tasks(self):
        self.ensure_one()
        return {
            'name': 'Tasks',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('lead_id', '=', self.lead_id.id)],
            'context': {'default_lead_id': self.lead_id.id},
        }

    def _get_partner_ids_for_lead_types(self, lead_types):
        if not lead_types:
            return []
            
        TEAM_MAP = {
            'jt_travel.lead_type_air_tickets': 'ticketing',
            'jt_travel.lead_type_visa_assistance': 'visa',
            'jt_travel.lead_type_hotels': 'operations',
            'jt_travel.lead_type_transfers_tours': 'operations',
            'jt_travel.lead_type_cruise': 'sales',
            'jt_travel.lead_type_insurance': 'operations', 
            'jt_travel.lead_type_forex': 'accounts',
            'jt_travel.lead_type_passport_renewal': 'visa',
            'jt_travel.lead_type_holiday_package': 'sales',
            'jt_travel.lead_type_corporate_group': 'sales',
            'jt_travel.lead_type_miscellaneous': 'operations',
        }
        
        team_keys = set()
        for lead_type in lead_types:
            for xml_id, team_key in TEAM_MAP.items():
                mapped_type = self.env.ref(xml_id, raise_if_not_found=False)
                if mapped_type and lead_type == mapped_type:
                    team_keys.add(team_key)
                    break  
                    
        if not team_keys:
            return []
            
        teams = self.env['travel.team'].search([('team_type', 'in', list(team_keys))])
        users = teams.mapped('team_leader_id') + teams.mapped('member_ids')
        return users.mapped('partner_id').ids
    

    def action_create_tasks(self):
        self.ensure_one()
        project = self.env['project.project'].sudo().search([('lead_id', '=', self.lead_id.id)], limit=1)
        if not project:
            raise UserError("No project found for this lead.")
            
        tasks_created_ids = []
        lines_to_process = self.line_ids.filtered(lambda l: not l.task_id and l.description and l.lead_type_ids)

        for line in lines_to_process:
            task_assignees = line.task_assignee_ids.sudo()
            all_partner_ids = task_assignees.mapped('partner_id').ids
            visa_type = self.env.ref('jt_travel.lead_type_visa_assistance', raise_if_not_found=False)
            is_visa = bool(visa_type and any(lt.id == visa_type.id for lt in line.lead_type_ids))
            
            task = self.env['project.task'].sudo().create({
                'name': line.description,
                'project_id': project.id,
                'lead_id': self.lead_id.id,
                'is_visa_type': is_visa,
                'partner_id': self.lead_id.partner_id.id if self.lead_id.partner_id else False,
                'lead_type_id': line.lead_type_ids[0].id if line.lead_type_ids else False,
                'task_service_type': ", ".join(line.lead_type_ids.mapped('name')),
                'user_ids': [(6, 0, task_assignees.ids)],
                'task_date': line.date,
            })
            
            line.task_id = task.id
            if all_partner_ids:
                task.sudo().message_subscribe(partner_ids=all_partner_ids)
                
            tasks_created_ids.append(task.id)
                
        if not tasks_created_ids:
            raise UserError("No new tasks to create. All valid lines already have associated tasks.")

        return {
            'name': 'Generated Tasks',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('id', 'in', tasks_created_ids)],
            'target': 'current',
            'effect': {
                'fadeout': 'slow',
                'message': Markup("Success! {} new tasks created.").format(len(tasks_created_ids)),
                'type': 'rainbow_man',
            }
        }
    


class TravelQuotationLine(models.Model):
    _name = 'travel.quotation.line'
    _description = 'Travel Quotation Line'   


    sequence = fields.Integer(string="Sequence", default=10)
    quotation_id = fields.Many2one('travel.quotation',string="Quotation",ondelete='cascade')
    lead_type_ids = fields.Many2many('lead.type',string="Lead Types")
    date = fields.Char(string="Date")
    description = fields.Char(string="Description")
    price = fields.Float(string="Price")
    remark = fields.Text(string="Remark")
    task_id = fields.Many2one('project.task', string="Created Task")
    task_assignee_ids = fields.Many2many(
    'res.users',
    'travel_quotation_line_assignee_rel',
    'line_id',
    'user_id',
    string="Assignees"
    )
    available_assignee_ids = fields.Many2many(
    'res.users',
    compute='_compute_available_assignee_ids',
    string="Available Assignees"
)

    @api.depends('lead_type_ids')
    def _compute_available_assignee_ids(self):
        for rec in self:
            if rec.lead_type_ids:
                teams = rec.lead_type_ids.mapped('team_ids')
                users = teams.mapped('member_ids') | teams.mapped('team_leader_id')
                rec.available_assignee_ids = users
            else:
                rec.available_assignee_ids = self.env['res.users']

    