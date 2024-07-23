# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api, exceptions


class delivery(models.Model):
    _name = 'delivery'  # psql database name is database_sync_up
    _description = 'database sync up'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    fserialid = fields.Integer(string='Serial ID')
    mFNUMBER = fields.Char(string='Model Number')
    FSN = fields.Char(string='Serial Number')
    F_WISY_ZBTIME = fields.Integer(string='ZB Time')
    ob_FNAME = fields.Char(string='OB Name')
    org_FNAME = fields.Char(string='Organization Name')
    FSTATE = fields.Integer(string='State')
    FBILLNO = fields.Char(string='Bill Number')
    FBILLDATE = fields.Date(string='Bill Date')
    FORDERNO = fields.Char(string='Order Number')
    FINPUTDATE = fields.Date(string='Input Date')
    su_FNAME = fields.Char(string='Supplier Name')
    cu_FNAME = fields.Char(string='Customer Name')
    FLOT = fields.Char(string='Lot')
    st_FNAME = fields.Char(string='ST Name')
    FCREATEDATE = fields.Date(string='Create Date')
    FPRODUCEDATE = fields.Date(string='Produce Date')
    FSTARTDATE = fields.Date(string='Start Date')
    FENDDATE = fields.Date(string='End Date')
    FSALEDATE = fields.Date(string='Sale Date')
    FLAG = fields.Integer(string='Flag')
    detail_ids = fields.One2many('custom_sync.product_detail', 'product_id', string='Product Details')