# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Odoo Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from . import models
from openerp import SUPERUSER_ID
import imghdr
import base64
import unicodedata
import re
try:
    import slugify as slugify_lib
except ImportError:
    slugify_lib = None

def get_slug(name):
    if slugify_lib:
        try:
            return slugify_lib.slugify(name)
        except TypeError:
            pass
    uni = unicodedata.normalize('NFKD', name).encode(
        'ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[\W_]', ' ', uni).strip().lower()
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug

def get_from_product_medium(cr):
#    product_template_obj = registry['product.template']
#    products_ids = product_template_obj.search(
#        cr, SUPERUSER_ID, [('product_images', '=', False),
#                           ('image_medium', '!=', False)])
    cr.execute("SELECT id, image_medium, name "
               "FROM product_template "
               "WHERE image_medium is not null and"
               " ID not in (SELECT product_tmpl_id"
               " FROM product_images)")
    products = cr.fetchall()
    for product in products:
        extension = imghdr.what('', base64.b64decode(
                    product[1]))
        extension = '.{}'.format(extension or 'jpe')
        cr.execute("INSERT INTO product_images(file_db_store,name,extension,"
                   "product_tmpl_id,link)"
                   "VALUES('{}','{}','{}',{},False)".format(
            product[1], get_slug(product[2]), extension,
            product[0]))


def get_from_product_images(cr, registry):
    old_images_obj = registry['product.images']
    old_images_ids = old_images_obj.search(cr, SUPERUSER_ID, [])
    products_list = []
    for o in old_images_obj.browse(cr, SUPERUSER_ID, old_images_ids):
        products_list.append(o.product_tmpl_id.id)
        image_type = 'url' if o.link else 'db'
        cr.execute("INSERT INTO product_image(file_db_store, "
                   "name,extension,url,comments,product_id,type)"
                   "VALUES('{}','{}','{}','{}','{}',{},'{}')".format(
            o.file_db_store, get_slug(o.name), o.extension, o.url,
            o.comments, o.product_tmpl_id.id, image_type))

