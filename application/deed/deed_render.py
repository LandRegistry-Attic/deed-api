"""
Want to run this as a standalone module? Set the PYTHONPATH and run the module,
the pdf will be generated wherever this is run from.  However, the CSS links will
fail.  Further needed to determine the correct base_url to give the
test_request_context. See Flask-WeasyPrint documentation if this is required.
"""
from flask import render_template, Flask, current_app
import flask_weasyprint


def create_deed_pdf(deed_dict):
    deed_html = create_deed_html(deed_dict)
    current_app.logger.info('Creating pdf for %s', deed_dict['title_number'])
    return flask_weasyprint.HTML(string=deed_html).write_pdf()


def create_deed_html(deed_dict):
    deed_data = {'deed': deed_dict}
    template = 'viewdeed.html'
    current_app.logger.info('Creating deed html page for %s', deed_dict['title_number'])
    borrower_count = 0
    for borrower in deed_data['deed']['borrowers']:
        borrower_count += 1
    return render_template(template, deed_data=deed_data, signed=True, borrower_count=borrower_count)


# flake8: noqa
if __name__ == "__main__":
    import jinja2
    from unit_tests.deed_dict import DEED
    from application.deed.model import format_address_string
    test_deed = DEED
    property_address = (test_deed["property_address"])
    test_deed["property_address"] = format_address_string(property_address)
    app = Flask(__name__)
    app.jinja_loader = jinja2.FileSystemLoader('../../application/templates')
    with app.test_request_context(''):
        pdf = create_deed_pdf(test_deed)
        open('mock_deed_model.pdf', 'wb').write(pdf)
    print('PDF generated. Check mock_deed_model.pdf file')
