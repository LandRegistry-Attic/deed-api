from datetime import datetime

from flask import render_template
import weasyprint

from application.deed.address_utils import format_address_string


def create_deed_pdf(deed_dict):
    deed_html = create_deed_html(deed_dict)
    return weasyprint.HTML(string=deed_html).write_pdf()


def create_deed_html(deed_dict):
    # return render_template(a template)
    if 'effective_date' in deed_dict:
        temp = datetime.datetime.strptime(deed_dict['effective_date'], "%Y-%m-%d %H:%M:%S")
        deed_dict["effective_date"] = temp.strftime("%d/%m/%Y")

    # FIXME reintroduce borrower frontend's address forrmatter here
    # deed_dict["property_address"] = format_address_string(','.join(deed_dict["property_address"]))
    deed_dict["property_address"] = format_address_string(deed_dict["property_address"])
    deed_data = {'deed': deed_dict}
    template = 'viewdeed.html'
    return render_template(template, deed_data=deed_data, signed=True)


