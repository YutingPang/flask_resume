import os, time
from flask import Flask, render_template, json, make_response, g
from flask_weasyprint import HTML, render_pdf
from docx import Document

os.environ['TZ'] = 'PDT'
time.tzset()

def import_json():
	f = open("resume.json")
	jdat = f.read()
	json_data = json.loads(jdat)
	f.close()
	return json_data


def json2xml(json_obj, line_padding=""):
	rl = list()
	json_obj_type = type(json_obj)

	if json_obj_type is list:
		for sub_elem in json_obj:
			rl.append(json2xml(sub_elem, line_padding))
		return "\n".join(rl)

	if json_obj_type is dict:
		for tag in json_obj:
			sub_obj = json_obj[tag]
			rl.append("%s<%s>" % (line_padding, tag))
			rl.append(json2xml(sub_obj, "\t" + line_padding))
			rl.append("%s</%s>" % (line_padding, tag))
		return "\n".join(rl)

	return "%s%s" % (line_padding, json_obj)

application = Flask(__name__)

@app.before_request
def before_request():
	g.json_data = import_json()

@app.route('/')
def index():
	return render_template('index.html', json=g.json_data, generated=time.strftime("%a, %d %b %Y %H:%M:%S PST"))

@app.route('/xml')
def xml():
	return render_template('xml.html', xml=json2xml(g.json_data), obj=g.json_data)

@app.route('/json')
def jsonpage():
    return render_template('json.html', json = json.dumps(g.json_data, indent=4, separators=(',', ': ')), obj = g.json_data)

@app.route('/pdf')
def pdf():
    html = render_template('pdf.html', json=g.json_data, generated = time.strftime("%a, %d %b %Y %H:%M:%S AEST"))
    return render_pdf(HTML(string=html))

@app.route('/download/json')
def download_json():
    response = make_response(json.dumps(g.json_data, indent=4, separators=(',', ': ')))
    response.headers["Content-Disposition"] = "attachment; filename=resume.json"
    return response

@app.route('/download/xml')
def download_xml():
    response = make_response(json2xml(g.json_data))
    response.headers["Content-Disposition"] = "attachment; filename=resume.xml"
    return response

@app.route('/docx')
def download_docx():
    generate_docx(g.json_data)
    with open("static/resume.docx", 'r') as f:
        body = f.read()
    response = make_response(body)
    response.headers["Content-Disposition"] = "attachment; filename=resume.docx"
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host='0.0.0.0', port=port)
