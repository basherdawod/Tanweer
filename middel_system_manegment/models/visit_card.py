from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError, UserError
from odoo.addons.phone_validation.tools import phone_validation
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import base64
from odoo.fields import Command
from odoo.osv import expression
import re
import logging

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime , timedelta

class VisitCard(models.Model):
    _name = "visit.card"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Visit NO",  readonly=True, default=lambda self: _('New'), copy=False)
    date = fields.Date(string="Date")
    building_type = fields.Char(string="Building Type G+")
    project_name = fields.Char(string="Project Name")
    makani_no = fields.Char(string="Makani No")
    area = fields.Many2one('res.country.state', string="Area")
    hdd = fields.Char(string="HDD")
    hdd1 = fields.Char(string="HDD1")
    bullet_n = fields.Char(string="Bullet N")
    bullet_v = fields.Char(string="Bullet V")
    bullet_wdr_vf = fields.Char(string="Bullet WDR VF")
    dome_n = fields.Char(string="Dome N")
    dome_vf = fields.Char(string="Dome VF")
    dome_wdr_vf = fields.Char(string="Dome WDR VF")
    notes_before_visiting = fields.Html(string='Note Before Visiting')
    notes_after_visiting = fields.Html(string='Note After Visiting')
    full_system_working = fields.Boolean(string="Full System Working")
    full_system_cleaning = fields.Boolean(string="Full System Cleaning")
    dvr_nvr_recording_30_days = fields.Boolean(string="DVR/NVR Recording 30 Days")
    technician_name = fields.Char(string="Technician Name")
    watch_man = fields.Char(string="Watch Man")
    watch_no = fields.Integer(string="Watch NO")
    middel_contract_id = fields.Many2one('middel.contract', string='Middel Contract', required=False)
    status = fields.Selection(
        [('draft', "Draft"),('complete', "Complete")],string="Status", default='draft')
    sequence = fields.Integer(string='Sequence', default=0)

    partner_id = fields.Many2one('res.partner', string='Customer Name', required=True)


    def set_to_draft(self):
        self.status = 'draft'

    def set_to_compleat(self):
        self.status = 'complete'

    # @api.model
    # def create(self, vals):
    #     vals['sequence'] = self.env['ir.sequence'].next_by_code('visit.card.sequence')

    #     today = datetime.today()
    #     year = today.year
    #     month = today.month
    #     day = today.day

    #     vals['visit_no'] = f"VC/{year}/{month}/{day}/{str(vals['sequence'])}"
        
    #     return super(VisitCard, self).create(vals)

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if vals.get('visit_no', _('New')) == _('New'):
    #             vals['visit_no'] = self.env['ir.sequence'].next_by_code('visit.card.sequence') or _('New')
    #     return super(VisitCard, self).create(vals)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('visit.card') or _('New')
        res = super(VisitCard, self).create(vals_list)
        return res


        # Date Filters
    def _get_today_filter(self):
        return [('date', '>=', fields.Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))]

    def _get_this_week_filter(self):
        return [('date', '>=', fields.Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=fields.Datetime.now().weekday()))]

    def _get_this_month_filter(self):
        return [('date', '>=', fields.Datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0))]

    def _get_this_year_filter(self):
        return [('date', '>=', fields.Datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0))]