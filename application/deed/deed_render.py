from contextlib import contextmanager

from flask import render_template, Flask
import weasyprint

def create_deed_pdf(deed_dict):
    deed_html = create_deed_html(deed_dict)
    return weasyprint.HTML(string=deed_html).write_pdf()


def create_deed_html(deed_dict):
    deed_data = {'deed': deed_dict}
    template = 'viewdeed.html'
    return render_template(template, deed_data=deed_data, signed=True)


deed_dict = {
    "additional_provisions": [{
                                  "additional_provision_code": "addp001",
                                  "description": "Description"
                              }, {
                                  "additional_provision_code": "addp002",
                                  "description": "Description"
                              }],
    "borrowers": [{
                      "address": "test address with postcode, PL14 3JR",
                      "forename": "lisa",
                      "middle_name": "ann",
                      "surname": "bloggette",
                      "token": "AAAAAA"
                  }, {
                      "address": "Test Address With Postcode, PL14 3JR",
                      "forename": "frank",
                      "middle_name": "ann",
                      "surname": "bloggette",
                      "token": "BBBBBB"
                  }],
    "charge_clause": {
        "cre_code": "CRE001",
        "description": "Description"
    },
    "effective_clause": "Effective clause goes here",
    "identity_checked": "Y",
    "lender": {
        "address": "Test Address, London NW10 7TQ",
        "name": "Bank of England Plc",
        "registration": "Company registration number: 123456"
    },
    "md_ref": "e-MD12344",
    "property_address": [
        "5 The Drive",
        "This Town",
        "This County",
        "PL4 4TH"
    ],
    "title_number": "DN100"
}



if __name__ == "__main__":
    import jinja2
    app = Flask(__name__)
    app.jinja_loader = jinja2.FileSystemLoader('../../application/templates')
    with app.app_context():
        pdf = create_deed_pdf(deed_dict)
        open('mock_deed_model.pdf', 'wb').write(pdf)


