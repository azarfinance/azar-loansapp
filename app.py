from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = "azarsecret"

# --------------------------
# Users dictionary
# --------------------------
users = {
    "admin": {"role": "admin", "pin": "1234"},
    "collector1": {"role": "collector", "pin": "0000"},
    "client1": {"role": "client", "pin": "0000", "full_name": "Client One", "email": "client1@mail.com", "phone": "0700000000", "id_number": "A1234567"}
}

# --------------------------
# Sample loan data
# --------------------------
loans = [
    {"id": 1, "client": "client1", "amount": 50000, "interest": 3000, "penalty": 0, "date": "2025-12-24", "status": "pending"},
    {"id": 2, "client": "client1", "amount": 40000, "interest": 2400, "penalty": 0, "date": "2025-12-22", "status": "approved"}
]

loan_id_counter = 3

# --------------------------
# Login route
# --------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        pin = request.form.get("pin")
        user = users.get(username)
        if user and user["pin"] == pin:
            session["username"] = username
            session["role"] = user["role"]
            flash("Login successful!")

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user["role"] == "collector":
                return redirect(url_for("collector_dashboard"))
            else:
                return redirect(url_for("client_dashboard"))
        else:
            flash("Invalid username or PIN")
            return redirect(url_for("login"))

    return render_template("login.html")

# --------------------------
# Signup route
# --------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    global users
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        id_number = request.form.get("id_number")
        username = request.form.get("username")
        pin = request.form.get("pin")

        if username in users:
            flash("Username already exists. Choose another.")
            return redirect(url_for("signup"))

        users[username] = {
            "role": "client",
            "pin": pin,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "id_number": id_number
        }

        flash("Signup successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")

# --------------------------
# Logout
# --------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect(url_for("login"))

# --------------------------
# Admin Dashboard
# --------------------------
@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        flash("Unauthorized")
        return redirect(url_for("login"))
    return render_template("admin/dashboard.html", loans=loans)

# --------------------------
# Collector Dashboard
# --------------------------
@app.route("/collector/dashboard")
def collector_dashboard():
    if session.get("role") != "collector":
        flash("Unauthorized")
        return redirect(url_for("login"))
    collector_loans = [loan for loan in loans if loan["status"] == "approved"]
    return render_template("collector/dashboard.html", loans=collector_loans)

# --------------------------
# Client Dashboard
# --------------------------
@app.route("/client/dashboard")
def client_dashboard():
    if session.get("role") != "client":
        flash("Unauthorized")
        return redirect(url_for("login"))
    client_loans = [loan for loan in loans if loan["client"] == session["username"]]
    return render_template("client/dashboard.html", loans=client_loans)

# --------------------------
# Create loan (Admin)
# --------------------------
@app.route("/create_loan", methods=["POST"])
def create_loan():
    global loan_id_counter
    if session.get("role") != "admin":
        flash("Unauthorized")
        return redirect(url_for("login"))

    client_name = request.form.get("client")
    amount = int(request.form.get("amount"))
    interest = int(request.form.get("interest"))
    loans.append({
        "id": loan_id_counter,
        "client": client_name,
        "amount": amount,
        "interest": interest,
        "penalty": 0,
        "date": "2025-12-24",
        "status": "pending"
    })
    loan_id_counter += 1
    flash("Loan created successfully!")
    return redirect(url_for("admin_dashboard"))

# --------------------------
# Approve loan (Admin)
# --------------------------
@app.route("/approve_loan/<int:id>", methods=["POST"])
def approve_loan(id):
    if session.get("role") != "admin":
        flash("Unauthorized")
        return redirect(url_for("login"))
    for loan in loans:
        if loan["id"] == id:
            loan["status"] = "approved"
            flash(f"Loan {id} approved!")
            break
    return redirect(url_for("admin_dashboard"))

# --------------------------
# Collect loan (Collector)
# --------------------------
@app.route("/collect_loan/<int:id>", methods=["POST"])
def collect_loan(id):
    if session.get("role") != "collector":
        flash("Unauthorized")
        return redirect(url_for("login"))
    for loan in loans:
        if loan["id"] == id and loan["status"] == "approved":
            loan["status"] = "collected"
            flash(f"Loan {id} collected!")
            break
    return redirect(url_for("collector_dashboard"))

# --------------------------
# USSD loan request (Client)
# --------------------------
@app.route("/ussd_request", methods=["POST"])
def ussd_request():
    global loan_id_counter
    if session.get("role") != "client":
        flash("Unauthorized")
        return redirect(url_for("login"))

    amount = int(request.form.get("amount"))
    loans.append({
        "id": loan_id_counter,
        "client": session["username"],
        "amount": amount,
        "interest": int(amount*0.06),
        "penalty": 0,
        "date": "2025-12-24",
        "status": "pending"
    })
    loan_id_counter += 1
    flash("USSD loan request submitted!")
    return redirect(url_for("client_dashboard"))

# --------------------------
# WhatsApp reminder (simulate)
# --------------------------
@app.route("/send_whatsapp/<int:id>")
def send_whatsapp(id):
    if session.get("role") != "admin":
        flash("Unauthorized")
        return redirect(url_for("login"))
    flash(f"WhatsApp reminder sent for loan {id} (simulated)!")
    return redirect(url_for("admin_dashboard"))

# --------------------------
# Export CSV (Admin)
# --------------------------
@app.route("/export_csv")
def export_csv():
    if session.get("role") != "admin":
        flash("Unauthorized")
        return redirect(url_for("login"))

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["ID","Client","Amount","Interest","Penalty","Date","Status"])
    for loan in loans:
        cw.writerow([loan["id"],loan["client"],loan["amount"],loan["interest"],loan["penalty"],loan["date"],loan["status"]])
    output = si.getvalue()
    return send_file(StringIO(output), mimetype="text/csv", as_attachment=True, download_name="loans.csv")

# --------------------------
# Run App
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)
