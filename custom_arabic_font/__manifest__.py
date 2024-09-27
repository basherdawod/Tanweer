 # -*- coding: utf-8 -*-
{
    'name': "custom arabic font",

    'summary': """
        change defult font to nice arabic font""",

    'description': """
        Change the defult arabic font of the all interfaces with a beautiful one preferred by the Arabic user
 ,
    """,
    'author': "abdalkareim",
    'category': 'Localization',
    'version': '17.00',
    'depends': ['web'],
    'qweb': [],

    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'auto_install': True,
    'installable': True,

    'assets': {
        'web.assets_backend': [
            'custom_arabic_font/static/src/scss/almaraifont.scss',
            'custom_arabic_font/static/src/scss/cairofont.scss',
            'custom_arabic_font/static/src/scss/droidfont.scss',
            'custom_arabic_font/static/src/css/web_style.css',
        ],
        'web.report_assets_common': [
            'custom_arabic_font/static/src/scss/almaraifont.scss',
            'custom_arabic_font/static/src/scss/cairofont.scss',
            'custom_arabic_font/static/src/scss/droidfont.scss',
        ],


    },
}