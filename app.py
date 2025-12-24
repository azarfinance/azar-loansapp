from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
import csv, os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# --- In-memory demo storage ---
users = [
    {'username':'admin','role':'admin','pin':'1234'},
    {'username':'collector1','role':'collector','pin':'0000'},
    {'username':'client1','role':'client','pin':'0000'}
]
loans = []

# --- Login ---
@app.route('/', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        pin=request.form.get('pin')
        user=next((u for u in users if u['username']==username and u['pin']==pin), None)
        if user:
            session['user']=user
            role=user['role']
            if role=='admin': return redirect(url_for('admin_dashboard'))
            if role=='collector': return redirect(url_for('collector_dashboard'))
            if role=='client': return redirect(url_for('client_dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

# --- Admin routes ---
@app.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html', loans=loans)

@app.route('/create_loan', methods=['POST'])
def create_loan():
    client=request.form.get('client')
    amount=float(request.form.get('amount'))
    loan={'id':len(loans)+1,'client':client,'amount':amount,'date':datetime.now(),'status':'pending','interest':amount*0.1,'penalty':0}
    loans.append(loan)
    flash('Loan created')
    return redirect(url_for('admin_dashboard'))

@app.route('/approve_loan/<int:id>', methods=['POST'])
def approve_loan(id):
    pin=request.form.get('pin')
    if session.get('user',{}).get('pin')!=pin:
        flash('Invalid PIN')
        return redirect(url_for('admin_dashboard'))
    loan=next((l for l in loans if l['id']==id), None)
    if loan: loan['status']='approved'
    flash('Loan approved')
    return redirect(url_for('admin_dashboard'))

# --- Collector routes ---
@app.route('/collector')
def collector_dashboard():
    return render_template('collector/dashboard.html', loans=loans)

@app.route('/collect_loan/<int:id>', methods=['POST'])
def collect_loan(id):
    loan=next((l for l in loans if l['id']==id), None)
    if loan: loan['status']='collected'
    flash('Loan collected')
    return redirect(url_for('collector_dashboard'))

# --- Client routes ---
@app.route('/client')
def client_dashboard():
    user=session.get('user', {})
    user_loans=[l for l in loans if l.get('client')==user.get('username')]
    return render_template('client/dashboard.html', loans=user_loans)

@app.route('/ussd_request', methods=['POST'])
def ussd_request():
    client=session.get('user',{}).get('username')
    amount=float(request.form.get('amount'))
    loan={'id':len(loans)+1,'client':client,'amount':amount,'date':datetime.now(),'status':'pending','interest':amount*0.1,'penalty':0}
    loans.append(loan)
    flash(f'USSD loan request of {amount} submitted!')
    return redirect(url_for('client_dashboard'))

# --- WhatsApp reminder simulation ---
@app.route('/send_whatsapp/<int:id>')
def send_whatsapp(id):
    loan=next((l for l in loans if l['id']==id), None)
    if loan:
        template_file=os.path.join('whatsapp_templates','reminder.txt')
        if os.path.exists(template_file):
            with open(template_file,'r') as f:
                template=f.read()
            message=template.replace('{client}',loan['client']).replace('{amount}',str(loan['amount'])).replace('{due_date}',str(loan['date']+timedelta(days=7)))
        else:
            message=f"Reminder to {loan['client']}: Pay {loan['amount']} by {loan['date']+timedelta(days=7)}"
        print('WhatsApp message simulated:', message)
        flash('WhatsApp reminder sent (simulated)')
    return redirect(url_for('admin_dashboard'))

# --- Export CSV ---
@app.route('/export_csv')
def export_csv():
    path='loans_export.csv'
    with open(path,'w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['ID','Client','Amount','Interest','Penalty','Date','Status'])
        for l in loans:
            w.writerow([l['id'],l['client'],l['amount'],l['interest'],l['penalty'],l['date'],l['status']])
    flash('CSV exported')
    return redirect(url_for('admin_dashboard'))

# --- Run server ---
if __name__=='__main__':
    # Use PORT environment variable if present (Render requirement)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
