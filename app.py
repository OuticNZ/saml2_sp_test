from flask import Flask, request, redirect, render_template_string
from onelogin.saml2.auth import OneLogin_Saml2_Auth
import os

app = Flask(__name__)

def init_saml_auth(req):
    auth = OneLogin_Saml2_Auth(req, custom_base_path=os.path.join(os.getcwd(), 'saml'))
    return auth

def prepare_flask_request(request):
    url_data = request.url.split('?')
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'script_name': request.path,
        'server_port': request.environ.get('SERVER_PORT'),
        'get_data': request.args.copy(),
        'post_data': request.form.copy()
    }


@app.route('/')
def index():
    # Landing page with a login button
    return render_template_string("""
        <html>
        <head><title>SAML Test App</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>Welcome to the SAML Test App</h1>
            <p>Click below to authenticate via Entra ID:</p>
            <a href="/login/">
  	            <button>Click me</button>
            </a>
        </body>
        </html>
    """)

@app.route('/login/')
def login():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    return redirect(auth.login())

@app.route('/acs/', methods=['POST'])
def acs():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    auth.process_response()
    errors = auth.get_errors()

    if not errors:
        attributes = auth.get_attributes()  # Dictionary of all claims
        name_id = auth.get_nameid()

        # Build HTML to display all claims
        html = '<h1>SAML Response</h1>'
        html += '<p><strong>NameID:</strong> '+name_id+'</p>'
        html += '<h2>Attributes:</h2>'
        html += '<table border="1" cellpadding="8" style="border-collapse: collapse;">'
        html += '<tr><th>Claim Name</th><th>Value(s)</th></tr>'

        for key, values in attributes.items():
            html += "<tr><td>{}</td><td>{}</td></tr>".format(key, ", ".join(values))

        html += "</table><br>/Back to Home</a>"
        return html
    else:
        return f"Errors: {errors}"

@app.route('/metadata/')
def metadata():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    return auth.get_settings().get_sp_metadata()

if __name__ == '__main__':
    app.run(debug=True)
