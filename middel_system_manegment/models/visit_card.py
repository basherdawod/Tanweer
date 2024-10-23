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

class VisitCard(models.Model):
    _name = "visit.card" #model_visit_card
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'visit_no'

    visit_no = fields.Char(string="Visit NO")
    date = fields.Date(string="Date")
    bullding_type = fields.Char(string="Bullding Type G+",requierd="True")
    project_name = fields.Char(string="Project Name")
    makani_no = fields.Integer(string="Makani No")
    area = fields.Many2one('res.country.state',string="Area")
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
    technican_name = fields.Char(string="Technican Name")
    watch_man = fields.Char(string="Watch Man")
    watch_no = fields.Integer(string="Watch NO")
    middel_contract_id = fields.Many2one('middel.contract',string=' Middel Contract',required=False)