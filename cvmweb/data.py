
import io
import textparser as tp
from datetime import date, datetime
import json
from json import JSONEncoder
import csv
from lxml import etree


class CVMWEBTextParser(tp.PortugueseRulesParser, tp.NumberParser):
    def parseDate(self, text, match):
        r'^(\d\d\d\d-\d\d-\d\d)$'
        return datetime.strptime(text, '%Y-%m-%d').date()


FIELD_PARSER = CVMWEBTextParser()


class AppJSONEncoder(JSONEncoder):
    def default(self, obj):
        return obj.isoformat() if isinstance(obj, datetime) or isinstance(obj, date) else json.JSONEncoder.default(self, obj)


dumps = lambda obj: json.dumps(obj, cls=AppJSONEncoder)


def format_field(value):
    value = value if value else ""
    value = value.strip()
    value = FIELD_PARSER.parse(value)
    if type(value) is bool:
        value = str(value).upper()
    elif type(value) is date:
        value = value.isoformat()
    return str(value)


class CVMWebData(object):
    def __init__(self, xml_content):
        self.xml_content = xml_content
        
        self.doc = etree.fromstring(self.xml_content)
        self.refdate = FIELD_PARSER.parse(self.doc.xpath('//CABECALHO/DT_REFER')[0].text)
        self.reftype = self.doc.xpath('//CABECALHO/TP_REFER')[0].text
        n = self.doc.xpath('(//INFORMES/*)[1]')
        self.code = n[0].tag if len(n) else None
    
    @property
    def xml(self):
        return self.xml_content
    
    @property
    def list(self):
        if self.code is None:
            return []
        docx = self.doc.xpath("//{}".format(self.code))
        content = [{ch.tag: FIELD_PARSER.parse(ch.text if ch.text else "") for ch in rec.getchildren()} for rec in docx]
        for rec in content:
            rec.update(DT_REFER=self.refdate)
        return content
    
    @property
    def json(self):
        return dumps(self.list)
    
    @property
    def csv(self):
        if self.code is None:
            return ''
        dd = self.doc.xpath("//{}".format(self.code))
        header = [ch.tag for ch in dd[0].getchildren()]
        header.insert(0, "DT_REFER")
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(header)
        for rec in dd:
            row = [format_field(ch.text) for ch in rec.getchildren()]
            row.insert(0, format_field(self.refdate.isoformat()))
            writer.writerow(row)
        content = buf.getvalue()
        buf.close()
        return content
    
    def save_xml(self, file):
        with open(file, "w", encoding="utf-8") as fp:
            fp.write(self.xml)
    
    def save_json(self, file):
        with open(file, "w", encoding="utf-8") as fp:
            fp.write(self.json)

    def save_csv(self, file):
        with open(file, "w", encoding="utf-8") as fp:
            fp.write(self.csv)


def read_xml(file=None, text=None):
    if file:
        with open(file) as fp:
            data = fp.read()
    elif text:
        data = text
    else:
        raise TypeError("Invalid file")
    return CVMWebData(data)
    

