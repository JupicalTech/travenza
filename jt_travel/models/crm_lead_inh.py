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
from odoo.exceptions import UserError, ValidationError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    lead_type_id = fields.Many2one('lead.type', string="Lead Type")

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
    lead_currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')], limit=1))
    task_count = fields.Integer(compute="_compute_counts")
    project_count = fields.Integer(compute="_compute_counts")
    number_of_passengers = fields.Integer('Number of Passengers')
    client_category = fields.Selection([
    ('silver', 'Silver'),
    ('gold', 'Gold'),
    ('platinum', 'Platinum'),
    ], string='Client Category', default='silver')
    document_count = fields.Integer(compute="_compute_document_count")
    allowed_user_ids = fields.Many2many('res.users', compute='_compute_allowed_user_ids', compute_sudo=True)
    quotation_ids = fields.One2many('travel.quotation', 'lead_id', string="Travel Quotations")
    quotation_count = fields.Integer(string="Quotations", compute='_compute_quotation_count')
    billing_ids = fields.One2many('travel.billing', 'lead_id', string="Billing Forms")
    billing_count = fields.Integer(compute="_compute_billing_count", string="Billings")
    is_in_process = fields.Boolean(compute="_compute_is_in_process", string="Is In Process")
    is_project_created = fields.Boolean(compute="_compute_counts", string="Project Created")
    visa_application_ids = fields.One2many('travel.visa.application', 'lead_id', string="Visa Applications")
    visa_count = fields.Integer(compute='_compute_visa_count')

    # for record rule 
    project_ids = fields.One2many('project.project', 'lead_id', string="Projects")
    lead_task_ids = fields.One2many('project.task', 'lead_id', string="Tasks")
    
    def _compute_visa_count(self):
        for rec in self:
            count = self.env['travel.visa.application'].search_count([
                '|', 
                ('lead_id', '=', rec.id), 
                ('task_id.lead_id', '=', rec.id)
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

    def _check_quotation_requirement(self):
        for rec in self:
            if rec.is_project_type:
                if rec.quotation_count == 0:
                    raise UserError("There's no travel quotation created for this project lead. Please create at least one quotation before marking as Won.")
            else:
                actual_billing_count = self.env['travel.billing'].search_count([('lead_id', '=', rec.id)])
                if actual_billing_count == 0:
                    raise UserError("There's no billing form created for this lead. Please create one before marking as Won.")


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
            'context': {'default_lead_id': self.id, 'default_assignee_id': self.user_id.id,},
            'target': 'current',
        }

    def action_view_visa_applications(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Visa Applications',
            'res_model': 'travel.visa.application',
            'view_mode': 'list,form',
            'domain': ['|', ('lead_id', '=', self.id), ('task_id.lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }


    @api.constrains('travel_date_from', 'travel_date_to')
    def _check_travel_dates(self):
        for record in self:
            if record.travel_date_to and not record.travel_date_from:
                raise ValidationError("Please fill Travel Date From.")
            
            elif record.travel_date_from and not record.travel_date_to:
                raise ValidationError("Please fill Travel Date To.")

    @api.depends('quotation_ids')
    def _compute_quotation_count(self):
        for rec in self:
            rec.quotation_count = len(rec.quotation_ids)

    def action_open_travel_quotations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Travel Quotations',
            'res_model': 'travel.quotation',
            'view_mode': 'list,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }
    


    # @api.depends('lead_type_id')
    # def _compute_allowed_user_ids(self):
    #     admin_group = self.env.ref('base.group_system', raise_if_not_found=False)
    #     admin_user_ids = admin_group.user_ids.ids if admin_group else []

    #     for rec in self:
    #         allowed_ids = list(admin_user_ids)

    #         if rec.lead_type_id:
    #             team_type_key = rec._get_team_type_for_lead_type(rec.lead_type_id)
                
    #             if team_type_key:
    #                 teams = self.env['travel.team'].search([('team_type', '=', team_type_key)])
                    
    #                 team_user_ids = teams.mapped('member_ids').ids + teams.mapped('team_leader_id').ids
    #                 allowed_ids.extend(team_user_ids)
            
    #         rec.allowed_user_ids = [(6, 0, list(set(allowed_ids)))]


    # @api.depends('lead_type_id', 'lead_type_id.team_id')
    # def _compute_allowed_user_ids(self):
    #     admin_group = self.env.ref('base.group_system', raise_if_not_found=False)
    #     admin_user_ids = admin_group.sudo().user_ids.ids if admin_group else []
    #     for rec in self:
    #         allowed_ids = list(admin_user_ids)
    #         if rec.lead_type_id and rec.lead_type_id.team_id:
    #             team = rec.lead_type_id.team_id.sudo()
    #             team_member_ids = team.member_ids.ids
    #             leader_id = [team.team_leader_id.id] if team.team_leader_id else []
    #             allowed_ids.extend(team_member_ids + leader_id)
    #         rec.sudo().allowed_user_ids = [(6, 0, list(set(allowed_ids)))]


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
            # if lead_type and lead_type.team_id:
            #     team = lead_type.team_id.sudo()
            #     if team.member_ids:
            #         allowed_ids.update(team.member_ids.ids)
            #     if team.team_leader_id:
            #         allowed_ids.add(team.team_leader_id.id)
            
            rec.allowed_user_ids = [(6, 0, list(allowed_ids))]




    @api.constrains('user_id', 'lead_type_id')
    def _check_lead_type_before_owner(self):
        for rec in self:
            if rec.user_id and not rec.lead_type_id:
                raise UserError("Please choose a Lead Type first before assigning an Assigned Owner.")
        
    
    
    # def _get_team_type_for_lead_type(self, lead_type):
    #     if not lead_type:
    #         return False
        
    #     TEAM_MAP = {
    #         'jt_travel.lead_type_air_tickets': 'ticketing',
    #         'jt_travel.lead_type_visa_assistance': 'visa',
    #         'jt_travel.lead_type_hotels': 'operations',
    #         'jt_travel.lead_type_transfers_tours': 'operations',
    #         'jt_travel.lead_type_cruise': 'sales',
    #         'jt_travel.lead_type_insurance': 'operations', 
    #         'jt_travel.lead_type_forex': 'accounts',
    #         'jt_travel.lead_type_passport_renewal': 'visa',
    #         'jt_travel.lead_type_holiday_package': 'sales',
    #         'jt_travel.lead_type_corporate_group': 'sales',
    #         'jt_travel.lead_type_miscellaneous': 'operations',
    #     }
        
    #     for xml_id, team_key in TEAM_MAP.items():
    #         mapped_type = self.env.ref(xml_id, raise_if_not_found=False)
    #         if mapped_type and lead_type == mapped_type:
    #             return team_key
    #     return 'operations'


    # def _get_partner_ids_for_team_types(self, team_types):
    #     if not team_types:
    #         return []
            
    #     teams = self.env['travel.team'].search([
    #         ('team_type', 'in', team_types)
    #     ])
        
    #     users = teams.mapped('team_leader_id') + teams.mapped('member_ids')
    #     return users.mapped('partner_id').ids
 

    # def action_assign_teams_to_tasks(self):
    #     for rec in self:
    #         for task in rec.quotation_ids.mapped('task_ids') | rec.billing_ids.mapped('task_ids') | rec.task_ids:

    #             team_type_key = rec._get_team_type_for_lead_type(task.lead_type_id)
                
    #             if team_type_key:
    #                 team = self.env['travel.team'].search([('team_type', '=', team_type_key)], limit=1)
    #                 if team:
    #                     team_users = team.team_leader_id | team.member_ids
    #                     if team_users:
    #                         task.user_ids = [(6, 0, team_users.ids)]



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

# team many2many 
    def action_assign_teams_to_tasks(self):
        for rec in self:
            all_tasks = rec.quotation_ids.mapped('task_ids') | rec.billing_ids.mapped('task_ids') | rec.task_ids
            
            for task in all_tasks:
                teams = task.lead_type_id.team_ids
                if teams:
                    team_users = self.env['res.users']
                    for team in teams.sudo():
                        team_users |= team.team_leader_id | team.member_ids
                    if team_users:
                        task.user_ids = [(6, 0, team_users.ids)]
  
    # @api.model_create_multi
    # def create(self, vals_list):
    #     records = super().create(vals_list)
    #     for rec in records:
            
    #         if rec.lead_type_id and not rec.tag_ids:
    #             tag_ids = rec._get_tags_for_lead_type(rec.lead_type_id)
    #             if tag_ids:
    #                 rec.tag_ids = [(6, 0, tag_ids)]
            
            
    #         if rec.lead_type_id:
    #             team_type_key = rec._get_team_type_for_lead_type(rec.lead_type_id)
    #             if team_type_key:
    #                 partner_ids = rec._get_partner_ids_for_team_types([team_type_key])
    #                 if partner_ids:
    #                     rec.message_subscribe(partner_ids=partner_ids)
    #     return records
    



    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.lead_type_id and not rec.tag_ids:
                tag_ids = rec._get_tags_for_lead_type(rec.lead_type_id)
                if tag_ids:
                    rec.tag_ids = [(6, 0, tag_ids)]
            
            # if rec.lead_type_id and rec.lead_type_id.team_id:
            #     team = rec.lead_type_id.team_id.sudo()
            #     partner_ids = (team.member_ids.mapped('partner_id').ids + 
            #                 ([team.team_leader_id.partner_id.id] if team.team_leader_id else []))
            #     if partner_ids:
            #         rec.message_subscribe(partner_ids=list(set(partner_ids)))
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

    
   
    # def write(self, vals):
    #     if 'stage_id' in vals:
    #         stage = self.env['crm.stage'].browse(vals['stage_id'])
    #         if stage.is_won:
    #             for rec in self:
    #                 if rec.is_project_type:
    #                     continue
    #                 actual_billing_count = self.env['travel.billing'].search_count([('lead_id', '=', rec.id)])
    #                 if actual_billing_count == 0:
    #                     raise UserError("There's no billing form created for this lead. Please create one before marking as Won.")

    #     elif vals.get('probability') == 100:
    #         for rec in self:
    #             if rec.is_project_type:
    #                 continue
    #             actual_billing_count = self.env['travel.billing'].search_count([('lead_id', '=', rec.id)])
    #             if actual_billing_count == 0:
    #                 raise UserError("There's no billing form created for this lead. Please create one before marking as Won.")
                        
    #     old_lead_types_map = {rec.id: rec.lead_type_id for rec in self} if 'lead_type_id' in vals else {}

    #     result = super().write(vals)

    #     if 'lead_type_id' in vals:
    #         for rec in self:
    #             old_lead_type = old_lead_types_map.get(rec.id)
    #             new_lead_type = rec.lead_type_id

    #             if old_lead_type != new_lead_type:
    #                 old_team_type_key = rec._get_team_type_for_lead_type(old_lead_type)
    #                 new_team_type_key = rec._get_team_type_for_lead_type(new_lead_type)

    #                 if old_team_type_key != new_team_type_key:
    #                     partners_to_remove = set()
    #                     partners_to_add = set()

    #                     if old_team_type_key:
    #                         partners_to_remove = set(rec._get_partner_ids_for_team_types([old_team_type_key]))
                        
    #                     if new_team_type_key:
    #                         partners_to_add = set(rec._get_partner_ids_for_team_types([new_team_type_key]))

    #                     protected_partners = set()
    #                     if rec.create_uid and rec.create_uid.partner_id:
    #                         protected_partners.add(rec.create_uid.partner_id.id)
    #                     if rec.user_id and rec.user_id.partner_id:
    #                         protected_partners.add(rec.user_id.partner_id.id)
    #                     if self.env.user and self.env.user.partner_id:
    #                         protected_partners.add(self.env.user.partner_id.id)

    #                     actual_to_remove = list((partners_to_remove - partners_to_add) - protected_partners)
    #                     actual_to_add = list(partners_to_add)

    #                     if actual_to_remove:
    #                         rec.message_unsubscribe(partner_ids=actual_to_remove)

    #                     if actual_to_add:
    #                         rec.message_subscribe(partner_ids=actual_to_add)

    #     return result

    def write(self, vals):
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
 
        # old_teams = {rec.id: rec.lead_type_id.team_id for rec in self} if 'lead_type_id' in vals else {}
        # result = super().write(vals)
        # if 'lead_type_id' in vals:
        #     for rec in self:
        #         old_team = old_teams.get(rec.id)
        #         new_team = rec.lead_type_id.team_id
 
        #         if old_team != new_team:
        #             partners_to_remove = set()
        #             partners_to_add = set()
 
        #             if old_team:
        #                 old_team_s = old_team.sudo()
        #                 partners_to_remove = set(old_team_s.member_ids.mapped('partner_id').ids + 
        #                                         ([old_team_s.team_leader_id.partner_id.id] if old_team_s.team_leader_id else []))
        #             if new_team:
        #                 new_team_s = new_team.sudo()
        #                 partners_to_add = set(new_team_s.member_ids.mapped('partner_id').ids + 
        #                                     ([new_team_s.team_leader_id.partner_id.id] if new_team_s.team_leader_id else []))
        old_teams = {rec.id: rec.lead_type_id.team_ids for rec in self} if 'lead_type_id' in vals else {}
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
 
        return result



        

    def _compute_document_count(self):
        for rec in self:
            project_ids = self.env['project.project'].search([('lead_id', '=', rec.id)]).ids
            task_ids = self.env['project.task'].search([('project_id', 'in', project_ids)]).ids
            billing_ids = self.env['travel.billing'].search([('lead_id', '=', rec.id)]).ids

            task_docs = self.env['ir.attachment'].search_count([('res_model', '=', 'project.task'),('res_id', 'in', task_ids),])
            project_docs = self.env['ir.attachment'].search_count([('res_model', '=', 'project.project'),('res_id', 'in', project_ids),])
            lead_docs = self.env['ir.attachment'].search_count([('res_model', '=', 'crm.lead'),('res_id', '=', rec.id),])
            billing_docs = self.env['ir.attachment'].search_count([('res_model', '=', 'travel.billing'), ('res_id', 'in', billing_ids),])
            rec.document_count = task_docs + project_docs + lead_docs + billing_docs



    # def action_view_lead_documents(self):
    #     self.ensure_one()
    #     project_ids = self.env['project.project'].search([('lead_id', '=', self.id)]).ids
    #     task_ids = self.env['project.task'].search([('project_id', 'in', project_ids)]).ids
    #     billing_ids = self.env['travel.billing'].search([('lead_id', '=', self.id)]).ids
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Documents',
    #         'res_model': 'ir.attachment',
    #         'view_mode': 'kanban,list,form',
    #         'domain': ['|', '|',
    #             '&', ('res_model', '=', 'project.task'), ('res_id', 'in', task_ids),
    #             '&', ('res_model', '=', 'project.project'), ('res_id', 'in', project_ids),
    #             '&', ('res_model', '=', 'crm.lead'), ('res_id', '=', self.id),
    #             '&', ('res_model', '=', 'travel.billing'), ('res_id', 'in', billing_ids),
    #         ],
    #         'context': {'create': False},
    #     }

    def action_view_lead_documents(self):
        self.ensure_one()
        project_ids = self.env['project.project'].search([('lead_id', '=', self.id)]).ids
        task_ids = self.env['project.task'].search([('project_id', 'in', project_ids)]).ids
        billing_ids = self.env['travel.billing'].search([('lead_id', '=', self.id)]).ids

        domain = [
            '|', '|', '|',
            '&', ('res_model', '=', 'project.task'), ('res_id', 'in', task_ids),
            '&', ('res_model', '=', 'project.project'), ('res_id', 'in', project_ids),
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

    def _compute_counts(self):
        for rec in self:
            direct_task_ids = self.env['project.task'].search([
                ('lead_id', '=', rec.id)
            ]).ids
 
            project_task_ids = self.env['project.task'].search([
                ('project_id.lead_id', '=', rec.id)
            ]).ids
 
            all_task_ids = set(direct_task_ids) | set(project_task_ids)
            rec.task_count = len(all_task_ids)
 
            rec.project_count = self.env['project.project'].search_count([
                ('lead_id', '=', rec.id)
            ])
            rec.is_project_created = rec.project_count > 0


    def action_view_tasks(self):
        self.ensure_one()

        direct_task_ids = self.env['project.task'].search([
            ('lead_id', '=', self.id)
        ]).ids
        project_task_ids = self.env['project.task'].search([
            ('project_id.lead_id', '=', self.id)
        ]).ids

        all_task_ids = list(set(direct_task_ids) | set(project_task_ids))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('id', 'in', all_task_ids)],
            'context': {'default_lead_id': self.id}
        }


    def action_view_projects(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Projects',
            'res_model': 'project.project',
            'view_mode': 'list,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id}
        }

  
  
    # @api.depends('lead_type_id')
    # def _compute_lead_type_flags(self):
    #     holiday_type = self.env.ref('jt_travel.lead_type_holiday_package', raise_if_not_found=False)
    #     corporate_type = self.env.ref('jt_travel.lead_type_corporate_group', raise_if_not_found=False)
    #     for rec in self:
    #         is_holiday = bool(holiday_type and rec.lead_type_id == holiday_type)
    #         is_corporate = bool(corporate_type and rec.lead_type_id == corporate_type)
    #         rec.is_holiday_type = is_holiday
    #         rec.is_not_holiday_type = not is_holiday
    #         rec.is_project_type = is_holiday or is_corporate 
    


    @api.depends('lead_type_id', 'lead_type_id.is_project_type')
    def _compute_lead_type_flags(self):
        for rec in self:
            # Treats holiday type as project type by using the single dynamic boolean
            is_project = bool(rec.lead_type_id and rec.lead_type_id.is_project_type)
            rec.is_project_type = is_project
            rec.is_holiday_type = is_project # Unified as requested
            rec.is_not_holiday_type = not is_project



    def action_open_project_wizard(self):
        self.ensure_one()
        return {
            'name': 'Create a Project',
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'form',
            'view_id': self.env.ref('project.project_project_view_form_simplified_footer').id,
            'target': 'new',
            'context': {
                'default_name': self.name,
                'default_lead_id': self.id,
                'active_id': self.id,
                'active_model': self._name,
                'default_package_name': self.name,
                'default_number_of_passengers': self.number_of_passengers,
                'default_destination': self.destination,
                'default_travel_date_from': self.travel_date_from,
                'default_travel_date_to': self.travel_date_to,
                'default_lead_currency_id': self.lead_currency_id.id,
            }
        }



    @api.onchange('lead_type_id')
    def _onchange_lead_type_id(self):
        if not self.lead_type_id:
            self.tag_ids = [(5, 0, 0)]
            return
        tag_ids = self._get_tags_for_lead_type(self.lead_type_id)
        self.tag_ids = [(6, 0, tag_ids)]
 


    # def action_sale_quotations_new(self):
    #     action = super().action_sale_quotations_new()
 
    #     order_lines = self._get_order_lines_for_lead_type()
 
    #     ctx = action.get('context', {})
    #     if isinstance(ctx, str):
    #         import ast
    #         ctx = ast.literal_eval(ctx) if ctx else {}
 
    #     ctx.update({
    #         'default_travel_destination':self.destination,
    #         'default_travel_date_from':self.travel_date_from,
    #         'default_travel_date_to':self.travel_date_to,
    #         'default_travel_number_of_passengers': self.number_of_passengers,
    #         'default_travel_client_category':self.client_category,
    #         'default_travel_lead_type_id':self.lead_type_id.id if self.lead_type_id else False,
    #         'default_travel_tag_ids':[(6, 0, self.tag_ids.ids)],
    #         'default_order_line':order_lines,
    #     })
    #     action['context'] = ctx
    #     return action
    



    def _get_tags_for_lead_type(self, lead_type):
        if not lead_type:
            return []
        return lead_type.tag_ids.ids



    # def action_sale_quotations_new(self):
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
    #         }
    #     }


    def action_sale_quotations_new(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Travel Quotation',
            'res_model': 'travel.quotation',  
            'view_mode': 'form',
            'views': [(self.env.ref('jt_travel.view_travel_quotation_form').id, 'form')],
            'target': 'current',
            'context': {
                'default_lead_id': self.id,
                'default_destination': self.destination,
                'default_travel_date_from': self.travel_date_from,
                'default_travel_date_to': self.travel_date_to,
                'default_number_of_passengers': self.number_of_passengers,
                'default_lead_type_id': self.lead_type_id.id,
                'default_tag_ids': [(6, 0, self.tag_ids.ids)],
            }
        }
    
    @api.constrains('lead_type_id')
    def _check_lead_type_change(self):
        visa_type = self.env.ref('jt_travel.lead_type_visa_assistance', raise_if_not_found=False)
        for rec in self:
            if not visa_type:
                continue
            if rec.lead_type_id != visa_type:
                visa_exists = self.env['travel.visa.application'].search_count([
                    ('lead_id', '=', rec.id),
                    ('task_id', '=', False),
                ])
                if visa_exists:
                    raise ValidationError(
                        "You cannot change the Lead Type because visa applications exist on this lead."
                    )