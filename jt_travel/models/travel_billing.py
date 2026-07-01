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
from odoo.exceptions import ValidationError
from markupsafe import Markup

class TravelBilling(models.Model):
    _name = 'travel.billing'
    _description = 'Travel Billing Form'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'


    name = fields.Char(string="Sr. No", copy=False, default='New')
    lead_id = fields.Many2one('crm.lead', string="Lead", ondelete='cascade')
    lead_type_id = fields.Many2one('lead.type', string="Lead Type", store=True, tracking=True)
    lead_type_name = fields.Char(related='lead_type_id.name', string="Type Name", tracking=True, store=True)
    date_submitted = fields.Datetime(string="Submitted On")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('pending', 'Pending'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)

    accountant_remark = fields.Text(string="Remarks", tracking=True)
    bill_ref_no = fields.Char(string="Bill Reference", tracking=True)
    invoice_number = fields.Char(string="Invoice Number", tracking=True)
    gst_details = fields.Char(string="GST Details", tracking=True)
    reffered_by_name = fields.Char(string="Referred By",tracking=True)

    # --- Common Fields ---
    passenger_name = fields.Char(string="Passenger Name", tracking=True)
    currency_id = fields.Many2one(
        'res.currency', 
        string="Currency", 
        default=lambda self: self.env.company.currency_id,
        tracking=True
    )

    net_cost = fields.Monetary(
        string="Net Cost", 
        currency_field='currency_id', 
        tracking=True
    )
    billing_amount = fields.Char(string="Billing Amount",tracking=True)
    vendor_id = fields.Many2one('res.partner', string="Vendor",tracking=True)
    billing_account = fields.Char(string="Billing Account",tracking=True)
    card_used = fields.Boolean(string="Card Used", tracking=True)
    card_no = fields.Char(string="Card No.", tracking=True)
    # card_amount = fields.Float(string="Card Amount", tracking=True)
    reference_number = fields.Char(string="Reference Number",tracking=True)

    
    # --- Uploads ---
    voucher_upload = fields.Binary(string="Voucher Upload")
    voucher_upload_name = fields.Char(string="Voucher File Name",tracking=True)

    ticket_copy_upload = fields.Binary(string="Ticket Copy")
    ticket_copy_upload_name = fields.Char(string="Ticket File Name",tracking=True)

    # --- Specific Fields ---
    travel_date = fields.Date(string="Travel Date",tracking=True)
    pnr_ref_number = fields.Char(string="PNR Reference Number",tracking=True)

    # Visa Fields
    visa_type_country = fields.Char(string="Visa Type & Country",tracking=True)
    visa_applied_date = fields.Date(string="Visa Applied Date",tracking=True)
    visa_expected_date = fields.Date(string="Visa Expected Date",tracking=True)
    rejection_reason = fields.Text(string="Reason for Rejection (If rejected)",tracking=True)
    vendor_type_card = fields.Many2one('res.partner', string="Vendor Type/Card",tracking=True)
    billing_party = fields.Char(string="Billing Party",tracking=True)
    
    # Hotel Fields
    hotel_name = fields.Char(string="Hotel Name",tracking=True)
    check_in_date = fields.Date(string="Check-in Date",tracking=True)
    
    # Transfer & Tour Fields
    activity_name = fields.Char(string="Activity Name",tracking=True)
    activity_date = fields.Date(string="Activity Date",tracking=True)
    
    # Cruise Fields
    cruise_sailing_date = fields.Date(string="Cruise Sailing Date",tracking=True)
    comments = fields.Text(string="Comments",tracking=True)
    
    # Insurance Fields
    policy_start_date = fields.Date(string="Policy Start Date",tracking=True)
    
    # Forex Fields
    currency_type_id = fields.Many2one('res.currency', string="Currency Type",tracking=True)

    billing_type_name = fields.Char(string="Billing Type")
    is_readonly_for_accountant = fields.Boolean(
        compute='_compute_is_readonly_for_accountant',
        string="Readonly for Accountant"
    )


    @api.onchange('lead_type_id')
    def _onchange_billing_lead_type_id(self):
        if self.lead_type_id:
            self.billing_type_name = self.lead_type_id.name
            
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res.pop('net_cost', None)
        return res

    @api.depends_context('uid')
    def _compute_is_readonly_for_accountant(self):
        is_accountant = self.env.user.has_group('jt_travel.group_travenza_holidays_accountant')
        for rec in self:
            rec.is_readonly_for_accountant = is_accountant


    def action_submit_bill(self):
        self.write({'state': 'submitted', 'date_submitted': fields.Datetime.now()})

    def action_mark_pending(self):
        self.write({'state': 'pending'})

    def action_mark_completed(self):
        for rec in self:
            if not rec.invoice_number:
                raise ValidationError("Invoice Number is required before marking the bill as Completed.")
        self.write({'state': 'completed'})


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].sudo().next_by_code('travel.billing.seq') or 'New'
            if not vals.get('lead_type_id') and vals.get('lead_id'):
                lead = self.env['crm.lead'].browse(vals['lead_id'])
                if lead.lead_type_id:
                    vals['lead_type_id'] = lead.lead_type_id.id
                    vals.setdefault('billing_type_name', lead.lead_type_id.name)

            if vals.get('state', 'draft') != 'draft':
                if not vals.get('net_cost') or vals.get('net_cost', 0) <= 0:
                    raise ValidationError("Net Cost must be greater than zero.")
        records = super(TravelBilling, self).create(vals_list)
        
        for rec in records:
            current_vals = next((v for v in vals_list if v.get('name') == rec.name), {})
            rec._post_attachment_to_chatter(current_vals)
            billing_seq = rec.name
            lead_type = rec.lead_type_name or "Unknown Type"
            creator_name = self.env.user.name
            log_body = Markup("<b>Billing Form Created:</b><ul><li>Reference: {}</li><li>Lead: {}</li><li>Created By: {}</li></ul>").format(
                billing_seq, lead_type, creator_name
            )
            rec.message_post(body=log_body)
        return records




    def write(self, vals):
        incoming_state = vals.get('state')
        if incoming_state and incoming_state != 'draft':
            incoming_net_cost = vals.get('net_cost')
            for rec in self:
                effective_net_cost = incoming_net_cost if incoming_net_cost is not None else rec.net_cost
                if not effective_net_cost or effective_net_cost <= 0:
                    raise ValidationError(
                        "Net Cost must be greater than zero.")
        res = super().write(vals)
        for rec in self:
            rec._post_attachment_to_chatter(vals)
        return res

   
    def _post_attachment_to_chatter(self, vals):
        upload_fields = {
            'ticket_copy_upload': 'ticket_copy_upload_name',
            'voucher_upload': 'voucher_upload_name'
        }
        
        for binary_field, name_field in upload_fields.items():
            if vals.get(binary_field):
                filename = vals.get(name_field) or getattr(self, name_field, False) or 'Uploaded_Document'
                
                attachment = self.env['ir.attachment'].create({
                    'name': filename,
                    'type': 'binary',
                    'datas': vals[binary_field],
                    'res_model': self._name,
                    'res_id': self.id,
                })
                
                self.message_post(
                    body=f"New document uploaded: {filename}",
                    attachment_ids=[attachment.id]
                )