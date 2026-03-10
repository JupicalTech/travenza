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

class CustomerVisaApplication(models.Model):
    _name = 'customer.visa.application'
    _description = 'Customer Visa Applications'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'visa_sequence'

    visa_sequence = fields.Char(string='Sr. No', default=lambda self: 'New', copy=False)
    customer_id = fields.Many2one('res.partner', string='Applicant')

    country_id = fields.Many2one('res.country', string='Country')
    visa_type_id = fields.Many2one('visa.type', string='Visa Type')
    passport_number = fields.Char(string='Passport Number')
    
    checklist_id = fields.Many2one('country.specific.checklist', 
        compute='_compute_checklist_id', 
        store=True
    )

    show_aadhar = fields.Boolean(related='checklist_id.has_aadhar')
    show_pan = fields.Boolean(related='checklist_id.has_pan')
    show_passport = fields.Boolean(related='checklist_id.has_passport')
    show_photo = fields.Boolean(related='checklist_id.has_photo')
    show_bank_statement = fields.Boolean(related='checklist_id.has_bank_statement')
    show_voter_id = fields.Boolean(related='checklist_id.has_voter_id')

    has_aadhar = fields.Boolean(string='Aadhar Card Provided')
    has_pan = fields.Boolean(string='PAN Card Provided')
    has_passport = fields.Boolean(string='Passport Provided')
    has_photo = fields.Boolean(string='Photo Provided')
    has_bank_statement = fields.Boolean(string='Bank Statement Provided')
    has_voter_id = fields.Boolean(string='Voter ID Provided')

    appointment_date = fields.Date(string='Appointment Date')
    is_biometric_required = fields.Boolean(string='Biometric Required?')
    biometric_file = fields.Binary(
    string="Upload Biometric Document", 
    inverse="_inverse_biometric_file"
    )
    biometric_filename = fields.Char(string="Biometric Filename")
    biometrics_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved')
    ], string='Biometrics Status', default='pending')
    submission_date = fields.Date(string='Application Submission Date')
    tracking_number = fields.Char(string='Tracking Number')
    result = fields.Selection([
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('delayed', 'Delayed')
    ], string='Status', default='in_progress', tracking=True)
    validity_period = fields.Char(string='Validity Period')


    def action_approve(self):
        for rec in self:
            rec.result = 'approved'

    def action_reject(self):
        for rec in self:
            rec.result = 'rejected'

    def action_delay(self):
        for rec in self:
            rec.result = 'delayed'



    def action_approve_biometrics(self):
        for rec in self:
            rec.biometrics_status = 'approved'

    def _inverse_biometric_file(self):
        for rec in self:
            if rec.biometric_file:
                rec.biometrics_status = 'approved'
                rec.is_biometric_required = False 
                
                attachment = self.env['ir.attachment'].create({
                    'name': rec.biometric_filename or 'Biometric_Document',
                    'datas': rec.biometric_file,
                    'res_model': 'customer.visa.application',
                    'res_id': rec.id,
                })
                
                rec.message_post(
                    body=f"Biometric document updated: {rec.biometric_filename}",
                    attachment_ids=[attachment.id]
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('visa_sequence', 'New') == 'New':
                vals['visa_sequence'] = self.env['ir.sequence'].next_by_code('customer.visa.application') or 'New'
        return super(CustomerVisaApplication, self).create(vals_list)

    @api.depends('country_id')
    def _compute_checklist_id(self):
        for rec in self:
            if rec.country_id:
                checklist = self.env['country.specific.checklist'].search([
                    ('country_id', '=', rec.country_id.id)
                ], limit=1)
                rec.checklist_id = checklist
            else:
                rec.checklist_id = False