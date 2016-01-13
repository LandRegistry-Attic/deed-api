# xmlify


generateDS/process_includes.py is third-party software (see license in generateDS.py) used 
to build Python classes from an input XML schema file definition (XSD). The generated classes
are used to build a matching hiearchy of data which can then be exported to generate a matching
XML document (using the export method).

Generation of a python library classes matching XSD specification:

```
generateDS.py -f -o ../application/deed/generated/deed_xmlify.py ../application/deed/schemas/deed-schema-v0-1.xsd
```

The classes can then be used in your application:-

```
    import application.deed.generated.deed_xmlify as api
    deed_app_xml = api.dmApplicationType()
    deed_app_xml.original_tagname_ = "dm-application"
    operative_deed_xml = api.operativeDeedType()
    deed_data_xml = api.deedDataType()
    .
    .
    .
    deed_app_xml.set_operativeDeed(operative_deed_xml)
    deed_stream = io.StringIO()
    deed_app_xml.export(deed_stream, 0,
                        namespacedef_='xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                                      'xsi:noNamespaceSchemaLocation="http://localhost:9080/schemas/' +
                                      XML_SCHEMA_FILE + '"'
                        )
    deed_xml = deed_stream.getvalue()
```

# E-Security

A change of the deed schema requires that:

1) Update to the swagger json in application/deed/schemas/deed-api.json
2) Consistent updates to deed-schema-v0-1.xsd
3) Update of the changed schema to the ESecurity business gateway test and assurance servers
4) Change into the /xmlify directory and re-generate the python xml creation classes (as above)
5) Matching updates to the XML document generation code in application/deed/utils/convert_json_to_xml.py

