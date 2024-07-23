# -*- coding: utf-8 -*-
{
    "name": "Delivery Sync",
    "summary": "Delivery Data Sync up",
    "description": """
T
    """,
    "author": "Jiawen Gu",
    "website": "https://www.empower.cn/",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Empower",
    "version": "12.0.0",
    # any module necessary for this one to work correctly
    "depends": [],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/data_tracking_views.xml",
    ],
    # only loaded in demonstration mode
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
