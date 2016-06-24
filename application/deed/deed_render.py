'''
Want to run this as a standalone module? Set the PYTHONPATH and run the module,
the pdf will be generated wherever this is run from.
'''


from flask import render_template, Flask
import weasyprint


def create_deed_pdf(deed_dict):
    deed_html = create_deed_html(deed_dict)
    return weasyprint.HTML(string=deed_html).write_pdf()


def create_deed_html(deed_dict):
    deed_data = {'deed': deed_dict}
    template = 'viewdeed.html'
    return render_template(template, deed_data=deed_data, signed=True)


if __name__ == "__main__":
    import jinja2
    from unit_tests.deed_dict import DEED
    app = Flask(__name__)
    app.jinja_loader = jinja2.FileSystemLoader('../../application/templates')
    with app.app_context():
        pdf = create_deed_pdf(DEED)
        open('mock_deed_model.pdf', 'wb').write(pdf)


