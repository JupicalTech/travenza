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
from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    lead_type_id = fields.Many2one('lead.type', string="Lead Type")

    # --- Holiday Package Fields ---
    holiday_source_loc = fields.Char('Source')
    holiday_destination_loc = fields.Char('Destination')
    holiday_duration = fields.Integer('Duration (Nights)')
    holiday_pas_count = fields.Integer('No. of Travelers')
    holiday_budget = fields.Float('Budget per Person')

    # --- Air Only Fields ---
    air_departure_city = fields.Char('Departure City')
    air_arrival_city = fields.Char('Arrival City')
    air_travel_date = fields.Date('Travel Date')
    air_class = fields.Selection([
        ('eco', 'Economy'), ('prem_eco', 'Premium Eco'), ('biz', 'Business')], string='Class')
    air_trip_type = fields.Selection([('one', 'One Way'), ('round', 'Round Trip')], string='Trip Type')

    # --- Visa Only Fields ---
    visa_country_id = fields.Many2one('res.country', string='Visa Country')
    visa_type_id = fields.Many2one('visa.type', string='Visa Type')
    visa_appointment_date = fields.Date('Appointment Date')
    passport_no = fields.Char('Passport Number')
    visa_submission_date = fields.Date('Passport Expiry')
    visa_tracking_number = fields.Char(string='Tracking Number')
    visa_validity_period = fields.Char(string='Validity Period')

    # --- Combo (Air + Visa or Hotel) Fields ---
    combo_services = fields.Char('Services Included (e.g. Air+Visa)')
    combo_total_pax = fields.Integer('Total Pax')
    combo_start_date = fields.Date('Start Date')
    combo_end_date = fields.Date('End Date')
    combo_special_reqs = fields.Text('Special Requirements')

    # --- Corporate Fields ---
    corp_company_name = fields.Char('Company Name')
    corp_employee_id = fields.Char('Employee ID/Code')
    corp_billing_entity = fields.Char('Billing Entity')
    corp_travel_policy = fields.Selection([('standard', 'Standard'), ('premium', 'Premium')], string='Policy')
    corp_department = fields.Char('Department')

    # --- Cruise Fields ---
    cruise_line = fields.Char('Cruise Line/Ship')
    cruise_cabin_type = fields.Selection([('inside', 'Inside'), ('ocean', 'Ocean View'), ('balcony', 'Balcony')], string='Cabin')
    cruise_itinerary = fields.Char('Itinerary/Route')
    cruise_departure_port = fields.Char('Departure Port')
    cruise_sailing_date = fields.Date('Sailing Date')

    # --- Forex/Insurance Fields ---
    forex_currency = fields.Many2one('res.currency', string='Required Currency')
    forex_amount = fields.Float('Forex Amount')
    ins_policy_type = fields.Selection([('single', 'Single Trip'), ('annual', 'Annual Multi')], string='Insurance Type')
    ins_coverage_area = fields.Char('Coverage Area')
    ins_start_date = fields.Date('Insurance Start Date')

    def action_create_visa_application(self):
        self.ensure_one()
        ctx = {
            'default_customer_id': self.partner_id.id,
            'default_country_id': self.visa_country_id.id,
            'default_visa_type_id': self.visa_type_id.id,
            'default_appointment_date': self.visa_appointment_date,
            'default_submission_date': self.visa_submission_date,
            'default_tracking_number': self.visa_tracking_number,
            'default_validity_period': self.visa_validity_period,
            'default_passport_number' : self.passport_no,
        }
        return {
            'name': 'Create Visa Application',
            'type': 'ir.actions.act_window',
            'res_model': 'customer.visa.application',
            'view_mode': 'form',
            'target': 'current',
            'context': ctx
        }
    
    def action_create_customer_booking(self):
        self.ensure_one()
        ctx = {
            'default_customer_id': self.partner_id.id,
            'default_source' : self.holiday_source_loc,
            'default_destination' : self.holiday_destination_loc
        }
        return {
            'name': 'Create Customer Booking',
            'type': 'ir.actions.act_window',
            'res_model': 'customer.booking',
            'view_mode': 'form',
            'target': 'current',
            'context': ctx,
        }