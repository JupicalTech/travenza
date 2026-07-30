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
from odoo.exceptions import UserError, ValidationError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    lead_type_id = fields.Many2one('lead.type', string="Lead Type")
    partner_id = fields.Many2one('res.partner', domain=[('user_ids', '=', False)])

    is_holiday_type = fields.Boolean(compute="_compute_lead_type_flags", store=True)
    is_not_holiday_type = fields.Boolean(compute="_compute_lead_type_flags")
    is_project_type = fields.Boolean(compute="_compute_lead_type_flags", store=True)

    package_name = fields.Char("Package Name")
    destination = fields.Char("Destination")
    travel_date_from = fields.Date("Travel Date From")
    travel_date_to = fields.Date("Travel Date To")
    client_price = fields.Float("Client Selling Price")
    advance_payment = fields.Float("Advance / Payment Received")
    priority = fields.Selection(default='1')
    proj_ref = fields.Char(string="Reference Number", copy=False, readonly=True)
    lead_currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')], limit=1))
    # task_count = fields.Integer(compute="_compute_counts")
    # project_count = fields.Integer(compute="_compute_counts")
    number_of_passengers = fields.Html('Number of Passengers')
    client_category = fields.Selection([
    ('silver', 'Silver'),
    ('gold', 'Gold'),
    ('platinum', 'Platinum'),
    ], string='Client Category', default='silver')
#     document_count = fields.Integer(compute="_compute_document_count")
#     allowed_user_ids = fields.Many2many('res.users', compute='_compute_allowed_user_ids', compute_sudo=True)
#     quotation_ids = fields.One2many('travel.quotation', 'lead_id', string="Travel Quotations")
#     quotation_count = fields.Integer(string="Quotations", compute='_compute_quotation_count')
#     billing_ids = fields.One2many('travel.billing', 'lead_id', string="Billing Forms")
#     billing_count = fields.Integer(compute="_compute_billing_count", string="Billings")
#     is_in_process = fields.Boolean(compute="_compute_is_in_process", string="Is In Process")
#     is_project_created = fields.Boolean(compute="_compute_counts", string="Project Created")
#     visa_application_ids = fields.One2many('travel.visa.application', 'lead_id', string="Visa Applications")
#     visa_count = fields.Integer(compute='_compute_visa_count')

#     # for record rule 
#     project_ids = fields.One2many('project.project', 'lead_id', string="Projects")
#     lead_task_ids = fields.One2many('project.task', 'lead_id', string="Tasks")
#     sub_assignee_ids = fields.Many2many(
#         'res.users',
#         'crm_lead_sub_assignee_rel',
#         'lead_id', 'user_id',
#         string="Sub Assignees",
#     )



#     # spreadsheet ------------------------------------------------- 
#     spreadsheet_ids = fields.One2many(
#     'spreadsheet.spreadsheet',
#     'lead_id',
#     string="Spreadsheets",
# )
#     spreadsheet_count = fields.Integer(
#         compute='_compute_spreadsheet_count',
#         string="Spreadsheets",
#     )

#     @api.depends('spreadsheet_ids')
#     def _compute_spreadsheet_count(self):
#         for rec in self:
#             rec.spreadsheet_count = len(rec.spreadsheet_ids)

#     def action_view_spreadsheets(self):
#         self.ensure_one()
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Quotations',
#             'res_model': 'spreadsheet.spreadsheet',
#             'view_mode': 'list,form',
#             'domain': [('lead_id', '=', self.id)],
#             'context': {
#                 'default_lead_id': self.id,
#                 'default_owner_id': self.env.user.id,
#             },
#         }


#     def action_new_spreadsheet(self):
#         self.ensure_one()
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Quotations',
#             'res_model': 'spreadsheet.spreadsheet',
#             'view_mode': 'list,form',
#             'domain': [('lead_id', '=', self.id)],
#             'context': {
#                 'default_lead_id': self.id,
#                 'default_owner_id': self.env.user.id,
#             },
#         }



# #  spreadsheet over --------------------------------------------------------


    document_count = fields.Integer(compute="_compute_document_count")
    allowed_user_ids = fields.Many2many('res.users', compute='_compute_allowed_user_ids', compute_sudo=True)
    billing_ids = fields.One2many('travel.billing', 'lead_id', string="Billing Forms")
    billing_count = fields.Integer(compute="_compute_billing_count", string="Billings")
    is_in_process = fields.Boolean(compute="_compute_is_in_process", string="Is In Process")
    visa_application_ids = fields.One2many('travel.visa.application', 'lead_id', string="Visa Applications")
    visa_count = fields.Integer(compute='_compute_visa_count')
    sub_assignee_ids = fields.Many2many(
        'res.users',
        'crm_lead_sub_assignee_rel',
        'lead_id', 'user_id',
        string="Sub Assignees",
    )
    external_link_ids = fields.One2many('crm.lead.external.link', 'lead_id', string="External Links")
    external_link_count = fields.Integer(compute='_compute_external_link_count', string="External Links")

    @api.depends('external_link_ids')
    def _compute_external_link_count(self):
        for rec in self:
            rec.external_link_count = len(rec.external_link_ids)

    def action_view_external_links(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'External Links',
            'res_model': 'crm.lead.external.link',
            'view_mode': 'list',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }
    
    # def _compute_visa_count(self):
    #     for rec in self:
    #         count = self.env['travel.visa.application'].search_count([
    #             '|', 
    #             ('lead_id', '=', rec.id), 
    #             ('task_id.lead_id', '=', rec.id)
    #         ])
    #         rec.visa_count = count

    def _compute_visa_count(self):
        for rec in self:
            count = self.env['travel.visa.application'].search_count([
                ('lead_id', '=', rec.id)
            ])
            rec.visa_count = count

    def _get_team_for_lead_type(self, lead_type):
        if not lead_type:
            return self.env['travel.team']
        return lead_type.mapped('team_ids')
 


    def _get_partner_ids_for_teams(self, team):
        if not team:
            return []
        partner_ids = []
        for t in team.sudo():
            users = t.team_leader_id + t.member_ids
            partner_ids.extend(users.mapped('partner_id').ids)
        return list(set(partner_ids))
    


    @api.depends('billing_ids')
    def _compute_billing_count(self):
        for rec in self:
            rec.billing_count = len(rec.billing_ids)

    @api.depends('stage_id')
    def _compute_is_in_process(self):
        in_process_stage = self.env['crm.stage'].search(
            [('name', '=', 'In Process')], limit=1
        )
        for rec in self:
            if in_process_stage:
                rec.is_in_process = rec.stage_id.sequence >= in_process_stage.sequence
            else:
                rec.is_in_process = rec.stage_id.name == 'In Process'

    # def _check_quotation_requirement(self):
    #     for rec in self:
    #         if rec.is_project_type:
    #             if rec.quotation_count == 0:
    #                 raise UserError("There's no travel quotation created for this project lead. Please create at least one quotation before marking as Won.")
    #         else:
    #             actual_billing_count = self.env['travel.billing'].search_count([('lead_id', '=', rec.id)])
    #             if actual_billing_count == 0:
    #                 raise UserError("There's no billing form created for this lead. Please create one before marking as Won.")


    def action_create_billing(self):
        self.ensure_one()
        billing = self.env['travel.billing'].create({
            'lead_id': self.id,
            'passenger_name': self.contact_name or (self.partner_id.name if self.partner_id else ''),
            'billing_type_name': self.lead_type_id.name or '',
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
        return {
            'type': 'ir.actions.act_window',
            'name': 'Billing Forms',
            'res_model': 'travel.billing',
            'view_mode': 'list,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }
    
    def action_create_visa_application(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Visa Application',
            'res_model': 'travel.visa.application',
            'view_mode': 'form',
            'context': {
            'default_lead_id': self.id,
            'default_assignee_id': self.user_id.id,
            'default_applicant_id': self.partner_id.id if self.partner_id else False,
            'default_destination': self.destination,
            'default_number_of_passengers': self.number_of_passengers,
        },
            'target': 'current',
        }

    # def action_view_visa_applications(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Visa Applications',
    #         'res_model': 'travel.visa.application',
    #         'view_mode': 'list,form',
    #         'domain': ['|', ('lead_id', '=', self.id), ('task_id.lead_id', '=', self.id)],
    #         'context': {'default_lead_id': self.id},
    #     }

    def action_view_visa_applications(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Visa Applications',
            'res_model': 'travel.visa.application',
            'view_mode': 'list,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }



    # @api.depends('quotation_ids')
    # def _compute_quotation_count(self):
    #     for rec in self:
    #         rec.quotation_count = len(rec.quotation_ids)

    # def action_open_travel_quotations(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Travel Quotations',
    #         'res_model': 'travel.quotation',
    #         'view_mode': 'list,form',
    #         'domain': [('lead_id', '=', self.id)],
    #         'context': {'default_lead_id': self.id},
    #     }
    


    @api.depends('lead_type_id', 'lead_type_id.team_ids')
    def _compute_allowed_user_ids(self):
        admin_group = self.env.ref('base.group_system', raise_if_not_found=False)
        admin_user_ids = admin_group.sudo().user_ids.ids if admin_group else []
        
        for rec in self:
            allowed_ids = set(admin_user_ids)
            lead_type = rec.lead_type_id
            if lead_type and lead_type.team_ids:
                for team in lead_type.team_ids.sudo():
                    allowed_ids.update(team.member_ids.ids)
                    if team.team_leader_id:
                        allowed_ids.add(team.team_leader_id.id)
            
            rec.allowed_user_ids = [(6, 0, list(allowed_ids))]




    @api.constrains('user_id', 'lead_type_id')
    def _check_lead_type_before_owner(self):
        for rec in self:
            if rec.user_id and not rec.lead_type_id:
                raise UserError("Please choose a Lead Type first before assigning an Assigned Owner.")
        
    
    # def action_assign_teams_to_tasks(self):
    #     for rec in self:
    #         all_tasks = rec.quotation_ids.mapped('task_ids') | rec.billing_ids.mapped('task_ids') | rec.task_ids
            
    #         for task in all_tasks:
    #             teams = task.lead_type_id.team_ids
    #             if teams:
    #                 team_users = self.env['res.users']
    #                 for team in teams.sudo():
    #                     team_users |= team.team_leader_id | team.member_ids
    #                 if team_users:
    #                     task.user_ids = [(6, 0, team_users.ids)]
  

    # @api.model
    # def _read_group(self, domain, groupby=(), aggregates=(), having=(), offset=0, limit=None, order=None):
    #     if not groupby or order:
    #         return super()._read_group(domain, groupby, aggregates, having=having, offset=offset, limit=limit, order=order)

    #     aggregates = tuple(aggregates)
    #     added = 'create_date:max' not in aggregates
    #     if added:
    #         aggregates = aggregates + ('create_date:max',)

    #     result = super()._read_group(domain, groupby, aggregates, having=having, offset=offset, limit=limit, order='create_date:max desc')

    #     if added:
    #         result = [row[:-1] for row in result]

    #     return result

    # @api.model
    # def web_read_group(self, domain, groupby, aggregates, *args, **kwargs):
    #     if groupby:
    #         aggregates = list(aggregates)
    #         if 'create_date:max' not in aggregates:
    #             aggregates.append('create_date:max')
    #         kwargs['order'] = 'create_date:max desc'
    #     return super().web_read_group(domain, groupby, aggregates, *args, **kwargs)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.is_project_type and not rec.proj_ref:
                rec.proj_ref = self.env['ir.sequence'].sudo().next_by_code('crm.lead.proj.ref.seq') or False

            if rec.lead_type_id and not rec.tag_ids:
                tag_ids = rec._get_tags_for_lead_type(rec.lead_type_id)
                if tag_ids:
                    rec.tag_ids = [(6, 0, tag_ids)]
            
            if rec.lead_type_id and rec.lead_type_id.team_ids:
                partner_ids = []
                for team in rec.lead_type_id.team_ids.sudo():
                    partner_ids += team.member_ids.mapped('partner_id').ids
                    if team.team_leader_id:
                        partner_ids.append(team.team_leader_id.partner_id.id)
                if partner_ids:
                    rec.message_subscribe(partner_ids=list(set(partner_ids)))
        return records



    @api.onchange('stage_id', 'probability')
    def _onchange_stage_and_probability(self):
        if self.is_project_type:
            return
        
        if (self.stage_id and self.stage_id.is_won) or self.probability == 100:
            lead_id = self._origin.id if getattr(self, '_origin', False) else self.id
            if lead_id:
                count = self.env['travel.billing'].search_count([('lead_id', '=', lead_id)])
                if count == 0:
                    if getattr(self, '_origin', False):
                        self.stage_id = self._origin.stage_id
                        self.probability = self._origin.probability
                    
                    return {
                        'warning': {
                            'title': 'Missing Billing Form',
                            'message': "There's no billing form created for this lead. Please create one before marking as Won."
                        }
                    }
                


    def action_set_won(self):
        for rec in self:
            if rec.is_project_type:
                continue
            actual_billing_count = self.env['travel.billing'].search_count([('lead_id', '=', rec.id)])
            if actual_billing_count == 0:
                raise UserError("There's no billing form created for this lead. Please create one before marking as Won.")
        return super(CrmLead, self).action_set_won()
    
    

    def action_set_won_rainbowman(self):
        for rec in self:
            if rec.is_project_type:
                continue
            actual_billing_count = self.env['travel.billing'].search_count([('lead_id', '=', rec.id)])
            if actual_billing_count == 0:
                raise UserError("There's no billing form created for this lead. Please create one before marking as Won.")
        return super(CrmLead, self).action_set_won_rainbowman()

    
    def write(self, vals):
        if 'lead_type_id' in vals:
            for rec in self:
                new_lead_type = self.env['lead.type'].browse(vals['lead_type_id'])
                if new_lead_type.is_project_type and not rec.proj_ref:
                    rec.proj_ref = self.env['ir.sequence'].sudo().next_by_code('crm.lead.proj.ref.seq') or False

        if 'stage_id' in vals or vals.get('probability') == 100:
            check_won = False
            if 'stage_id' in vals:
                check_won = self.env['crm.stage'].browse(vals['stage_id']).is_won
            else:
                check_won = True

            if check_won:
                for rec in self:
                    if rec.is_project_type:
                        continue
                    if self.env['travel.billing'].search_count([('lead_id', '=', rec.id)]) == 0:
                        raise UserError("There's no billing form created for this lead. Please create one before marking as Won.")

        old_teams = {rec.id: rec.lead_type_id.team_ids for rec in self} if 'lead_type_id' in vals else {}
        old_sub_assignees = {rec.id: set(rec.sub_assignee_ids.ids) for rec in self} if 'sub_assignee_ids' in vals else {}
        result = super().write(vals)

        if 'lead_type_id' in vals:
            for rec in self:
                old_team_set = old_teams.get(rec.id, self.env['travel.team'])
                new_team_set = rec.lead_type_id.team_ids

                if old_team_set != new_team_set:
                    partners_to_remove = set()
                    partners_to_add = set()

                    for team in old_team_set.sudo():
                        partners_to_remove.update(team.member_ids.mapped('partner_id').ids)
                        if team.team_leader_id:
                            partners_to_remove.add(team.team_leader_id.partner_id.id)

                    for team in new_team_set.sudo():
                        partners_to_add.update(team.member_ids.mapped('partner_id').ids)
                        if team.team_leader_id:
                            partners_to_add.add(team.team_leader_id.partner_id.id)

                    rec_s = rec.sudo()
                    protected = {rec_s.create_uid.partner_id.id, rec_s.user_id.partner_id.id, self.env.user.partner_id.id}
                    protected.discard(False)

                    to_remove = list((partners_to_remove - partners_to_add) - protected)
                    to_add = list(partners_to_add)

                    if to_remove:
                        rec.message_unsubscribe(partner_ids=to_remove)
                    if to_add:
                        rec.message_subscribe(partner_ids=to_add)

        if 'sub_assignee_ids' in vals:
            for rec in self:
                old_ids = old_sub_assignees.get(rec.id, set())
                newly_added = set(rec.sub_assignee_ids.ids) - old_ids
                if newly_added:
                    new_users = self.env['res.users'].browse(list(newly_added))
                    partner_ids = new_users.mapped('partner_id').ids
                    if partner_ids:
                        self.env['mail.message'].sudo().create({
                            'message_type': 'user_notification',
                            'subtype_id': self.env.ref('mail.mt_note').id,
                            'subject': f"You have been assigned to a Lead: {rec.name or 'N/A'}",
                            'body': f"You have been added as a sub-assignee in lead: {rec.name or 'N/A'}",
                            'partner_ids': [(6, 0, partner_ids)],
                            'res_id': rec.id,
                            'model': rec._name,
                            'author_id': self.env.user.partner_id.id,
                            'notification_ids': [(0, 0, {
                                'res_partner_id': pid,
                                'notification_type': 'inbox',
                            }) for pid in partner_ids],
                        })

        return result
        

    # def _compute_document_count(self):
    #     for rec in self:
    #         project_ids = self.env['project.project'].search([('lead_id', '=', rec.id)]).ids
    #         task_ids = self.env['project.task'].search([('project_id', 'in', project_ids)]).ids
    #         billing_ids = self.env['travel.billing'].search([('lead_id', '=', rec.id)]).ids
    #         quotation_ids = self.env['travel.quotation'].search([('lead_id', '=', rec.id)]).ids

    #         task_docs = self.env['ir.attachment'].search_count([('res_model', '=', 'project.task'),('res_id', 'in', task_ids),])
    #         project_docs = self.env['ir.attachment'].search_count([('res_model', '=', 'project.project'),('res_id', 'in', project_ids),])
    #         lead_docs = self.env['ir.attachment'].search_count([('res_model', '=', 'crm.lead'),('res_id', '=', rec.id),])
    #         billing_docs = self.env['ir.attachment'].search_count([('res_model', '=', 'travel.billing'), ('res_id', 'in', billing_ids),])
    #         quotation_docs = self.env['ir.attachment'].search_count([('res_model', '=', 'travel.quotation'), ('res_id', 'in', quotation_ids),])
    #         rec.document_count = task_docs + project_docs + lead_docs + billing_docs + quotation_docs



    # def action_view_lead_documents(self):
    #     self.ensure_one()
    #     project_ids = self.env['project.project'].search([('lead_id', '=', self.id)]).ids
    #     task_ids = self.env['project.task'].search([('project_id', 'in', project_ids)]).ids
    #     billing_ids = self.env['travel.billing'].search([('lead_id', '=', self.id)]).ids
    #     quotation_ids = self.env['travel.quotation'].search([('lead_id', '=', self.id)]).ids

    #     domain = [
    #         '|', '|', '|', '|',
    #         '&', ('res_model', '=', 'project.task'), ('res_id', 'in', task_ids),
    #         '&', ('res_model', '=', 'project.project'), ('res_id', 'in', project_ids),
    #         '&', ('res_model', '=', 'crm.lead'), ('res_id', '=', self.id),
    #         '&', ('res_model', '=', 'travel.billing'), ('res_id', 'in', billing_ids),
    #         '&', ('res_model', '=', 'travel.quotation'), ('res_id', 'in', quotation_ids),
    #     ]

    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Documents',
    #         'res_model': 'ir.attachment',
    #         'view_mode': 'kanban,list,form',
    #         'domain': domain,
    #         'context': {
    #             'default_res_id': self.id,
    #             'default_res_model': self._name,
    #             'search_default_my_documents_filter': 0, 
    #         },
    #         'help': """<p class="o_view_nocontent_smiling_face">No documents found</p>""",
    #     }



    def _compute_document_count(self):
        for rec in self:
            billing_ids = self.env['travel.billing'].search([('lead_id', '=', rec.id)]).ids

            lead_docs = self.env['ir.attachment'].search_count([('res_model', '=', 'crm.lead'),('res_id', '=', rec.id),])
            billing_docs = self.env['ir.attachment'].search_count([('res_model', '=', 'travel.billing'), ('res_id', 'in', billing_ids),])
            rec.document_count = lead_docs + billing_docs



    def action_view_lead_documents(self):
        self.ensure_one()
        billing_ids = self.env['travel.billing'].search([('lead_id', '=', self.id)]).ids

        domain = [
            '|',
            '&', ('res_model', '=', 'crm.lead'), ('res_id', '=', self.id),
            '&', ('res_model', '=', 'travel.billing'), ('res_id', 'in', billing_ids),
        ]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': domain,
            'context': {
                'default_res_id': self.id,
                'default_res_model': self._name,
                'search_default_my_documents_filter': 0, 
            },
            'help': """<p class="o_view_nocontent_smiling_face">No documents found</p>""",
        }


    

    # def _compute_counts(self):
    #     for rec in self:
    #         direct_task_ids = self.env['project.task'].search([
    #             ('lead_id', '=', rec.id)
    #         ]).ids
 
    #         project_task_ids = self.env['project.task'].search([
    #             ('project_id.lead_id', '=', rec.id)
    #         ]).ids
 
    #         all_task_ids = set(direct_task_ids) | set(project_task_ids)
    #         rec.task_count = len(all_task_ids)
 
    #         rec.project_count = self.env['project.project'].search_count([
    #             ('lead_id', '=', rec.id)
    #         ])
    #         rec.is_project_created = rec.project_count > 0


    # def action_view_tasks(self):
    #     self.ensure_one()

    #     direct_task_ids = self.env['project.task'].search([
    #         ('lead_id', '=', self.id)
    #     ]).ids
    #     project_task_ids = self.env['project.task'].search([
    #         ('project_id.lead_id', '=', self.id)
    #     ]).ids

    #     all_task_ids = list(set(direct_task_ids) | set(project_task_ids))

    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Tasks',
    #         'res_model': 'project.task',
    #         'view_mode': 'kanban,list,form',
    #         'domain': [('id', 'in', all_task_ids)],
    #         'context': {'default_lead_id': self.id}
    #     }


    # def action_view_projects(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Projects',
    #         'res_model': 'project.project',
    #         'view_mode': 'list,form',
    #         'domain': [('lead_id', '=', self.id)],
    #         'context': {'default_lead_id': self.id}
    #     }



    @api.depends('lead_type_id', 'lead_type_id.is_project_type')
    def _compute_lead_type_flags(self):
        for rec in self:
            is_project = bool(rec.lead_type_id and rec.lead_type_id.is_project_type)
            rec.is_project_type = is_project
            rec.is_holiday_type = is_project 
            rec.is_not_holiday_type = not is_project



    # def action_open_project_wizard(self):
    #     self.ensure_one()
    #     return {
    #         'name': 'Create a Project',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'project.project',
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('project.project_project_view_form_simplified_footer').id,
    #         'target': 'new',
    #         'context': {
    #             'default_name': self.name,
    #             'default_lead_id': self.id,
    #             'active_id': self.id,
    #             'active_model': self._name,
    #             'default_package_name': self.name,
    #             'default_number_of_passengers': self.number_of_passengers,
    #             'default_destination': self.destination,
    #             'default_travel_date_from': self.travel_date_from,
    #             'default_travel_date_to': self.travel_date_to,
    #             'default_lead_currency_id': self.lead_currency_id.id,
    #         }
    #     }



    @api.onchange('lead_type_id')
    def _onchange_lead_type_id(self):
        if not self.lead_type_id:
            self.tag_ids = [(5, 0, 0)]
            return
        tag_ids = self._get_tags_for_lead_type(self.lead_type_id)
        self.tag_ids = [(6, 0, tag_ids)]
 


    def _get_tags_for_lead_type(self, lead_type):
        if not lead_type:
            return []
        return lead_type.tag_ids.ids


    # def action_sale_quotations_new(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Travel Quotation',
    #         'res_model': 'travel.quotation',  
    #         'view_mode': 'form',
    #         'views': [(self.env.ref('jt_travel.view_travel_quotation_form').id, 'form')],
    #         'target': 'current',
    #         'context': {
    #             'default_lead_id': self.id,
    #             'default_destination': self.destination,
    #             'default_travel_date_from': self.travel_date_from,
    #             'default_travel_date_to': self.travel_date_to,
    #             'default_number_of_passengers': self.number_of_passengers,
    #             'default_lead_type_id': self.lead_type_id.id,
    #             'default_tag_ids': [(6, 0, self.tag_ids.ids)],
    #         }
    #     }
    
    # @api.constrains('lead_type_id')
    # def _check_lead_type_change(self):
    #     visa_type = self.env.ref('jt_travel.lead_type_visa_assistance', raise_if_not_found=False)
    #     for rec in self:
    #         if not visa_type:
    #             continue
    #         if rec.lead_type_id != visa_type:
    #             visa_exists = self.env['travel.visa.application'].search_count([
    #                 ('lead_id', '=', rec.id),
    #                 ('task_id', '=', False),
    #             ])
    #             if visa_exists:
    #                 raise ValidationError(
    #                     "You cannot change the Lead Type because visa applications exist on this lead."
    #                 )
                

    @api.constrains('lead_type_id')
    def _check_lead_type_change(self):
        visa_type = self.env.ref('jt_travel.lead_type_visa_assistance', raise_if_not_found=False)
        for rec in self:
            if not visa_type:
                continue
            if rec.lead_type_id != visa_type:
                visa_exists = self.env['travel.visa.application'].search_count([
                    ('lead_id', '=', rec.id),
                ])
                if visa_exists:
                    raise ValidationError(
                        "You cannot change the Lead Type because visa applications exist on this lead."
                    )


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    is_visa_lead = fields.Boolean(compute='_compute_is_visa_lead')

    @api.depends('res_model', 'res_id')
    def _compute_is_visa_lead(self):
        visa_type = self.env.ref('jt_travel.lead_type_visa_assistance', raise_if_not_found=False)
        for rec in self:
            rec.is_visa_lead = False
            if visa_type and rec.res_model == 'crm.lead' and rec.res_id:
                lead = self.env['crm.lead'].browse(rec.res_id).exists()
                if lead and lead.lead_type_id.id == visa_type.id:
                    rec.is_visa_lead = True

    def _to_store_defaults(self, target):
        return super()._to_store_defaults(target) + ['is_visa_lead']