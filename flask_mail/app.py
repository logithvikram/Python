from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'logithvikram.krishnamoorthy@vexternal.com'  
app.config['MAIL_PASSWORD'] = 'mixyzpgmfwbfqtnb'  
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

@app.route("/")
def index():
    msg = Message(
        'Hello from Flask-Mail',
        sender='logithvikram.krishnamoorthy@vexternal.com',  
        recipients=['logithvikram2982002@gmail.com']  
    )
    msg.body = 'Hello Flask message sent from Flask-Mail'
    mail.send(msg)
    return 'Sent'

if __name__ == '__main__':
    app.run(debug=True)
