import os
import json
import uuid
import locale
from app.utils.db_utils import get_db_connection
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session, make_response, send_file
from werkzeug.security import check_password_hash
from functools import wraps
from datetime import datetime
from app.utils.report_utils import generate_report

# Set locale to Greek
locale.setlocale(locale.LC_ALL, 'el_GR.UTF-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
CLIENTS_FILE = os.path.join(DATA_DIR, 'clients.json')

os.makedirs(DATA_DIR, exist_ok=True)

user_bp = Blueprint('user', __name__, url_prefix='/')

@user_bp.route("/save_general", methods=["POST"])
def save_general():
    person = {
        "name": request.form.get("full_name"),
        "dob": request.form.get("dob"),
        "profession": request.form.get("profession"),
    }

    spouse = {
        "name": request.form.get("spouse_full_name"),
        "dob": request.form.get("spouse_dob"),
        "profession": request.form.get("spouse_profession"),
    }

    # Extract lists of children data
    child_names = request.form.getlist("child_name[]")
    child_dobs = request.form.getlist("child_dob[]")
    child_professions = request.form.getlist("child_profession[]")

    # Combine into list of children
    children = []
    for name, dob, profession in zip(child_names, child_dobs, child_professions):
        children.append({
            "name": name,
            "dob": dob,
            "profession": profession
        })

    # Optional notes
    notes = request.form.get("notes", "")

    general_data = {
        "person": person,
        "spouse": spouse,
        "children": children,
        "notes": notes
    }
    session["general"] = general_data
    
    with open(f"{DATA_DIR}/{session['current_client_id']}.json", 'r') as f:
        data = json.load(f)
        data["general"] = general_data
    with open(f"{DATA_DIR}/{session['current_client_id']}.json", 'w') as f:
        json.dump(data, f, indent=2)

    return jsonify(success=True)

@user_bp.route("/save_property", methods=["POST"])
def save_property():
    # Get lists of each investment field
    types = request.form.getlist("type[]")
    values = request.form.getlist("value[]")
    owners = request.form.getlist("owner[]")
    uses = request.form.getlist("use[]")
    sq_meters = request.form.getlist("sq_meters[]")
    postal_codes = request.form.getlist("postal_code[]")
    years_built = request.form.getlist("year_built[]")
    property_insured = request.form.getlist("property_insured[]")
    lights = request.form.getlist("light[]")

    # Optional notes
    notes = request.form.get("notes", "")

    # Build the list of investments
    properties = []
    for i in range(len(types)):
        properties.append({
            "type": types[i],
            "value": values[i],
            "owner": owners[i],
            "use": uses[i],
            "sq_meters": sq_meters[i],
            "postal_code": postal_codes[i],
            "year_built": years_built[i],
            "property_insured": property_insured[i],
            "light": lights[i]
        })

    # Save to session
    properties_data = {
        "properties": properties,
        "notes": notes
    }
    session["properties"] = properties_data
    with open(f"{DATA_DIR}/{session['current_client_id']}.json", 'r') as f:
        data = json.load(f)
        data["properties"] = properties_data
    with open(f"{DATA_DIR}/{session['current_client_id']}.json", 'w') as f:
        json.dump(data, f, indent=2)

    return jsonify(success=True)

@user_bp.route("/save_investment", methods=["POST"])
def save_investment():
    # Get lists of each investment field
    types = request.form.getlist("investment_type[]")
    reasons = request.form.getlist("investment_reason[]")
    values = request.form.getlist("current_value[]")
    holders = request.form.getlist("holder[]")
    start_dates = request.form.getlist("start_date[]")
    end_dates = request.form.getlist("end_date[]")

    # Optional notes
    notes = request.form.get("notes", "")

    # Build the list of investments
    investments = []
    for i in range(len(types)):
        # Optional: skip incomplete rows
        if types[i].strip() == "" and values[i].strip() == "" and holders[i].strip() == "":
            continue
        investments.append({
            "type": types[i],
            "reason": reasons[i],
            "current_value": values[i],
            "holder": holders[i],
            "start_date": start_dates[i],
            "end_date": end_dates[i]
        })

    # Save to session
    investments_data = {
        "investments": investments,
        "notes": notes
    }
    session["investments"] = investments_data
    with open(f"{DATA_DIR}/{session['current_client_id']}.json", 'r') as f:
        data = json.load(f)
        data["investments"] = investments_data
    with open(f"{DATA_DIR}/{session['current_client_id']}.json", 'w') as f:
        json.dump(data, f, indent=2)

    return jsonify(success=True)

@user_bp.route("/save_financials", methods=["POST"])
def save_financials():
    # Fetch data of all incomes
    person_income_amounts = request.form.getlist("person_income_amount[]")
    person_income_sources = request.form.getlist("person_income_source[]")
    person_income_start_dates = request.form.getlist("person_income_start_date[]")
    person_income_end_dates = request.form.getlist("person_income_end_date[]")

    spouse_income_amounts = request.form.getlist("spouse_income_amount[]")
    spouse_income_sources = request.form.getlist("spouse_income_source[]")
    spouse_income_start_dates = request.form.getlist("spouse_income_start_date[]")
    spouse_income_end_dates = request.form.getlist("spouse_income_end_date[]")

    # Build the list of investments
    person_incomes = []
    for i in range(len(person_income_amounts)):
        person_incomes.append({
            "amount": person_income_amounts[i],
            "source": person_income_sources[i],
            "start_date": person_income_start_dates[i],
            "end_date": person_income_end_dates[i]
        })

    spouse_incomes = []
    for i in range(len(spouse_income_amounts)):
        spouse_incomes.append({
            "amount": spouse_income_amounts[i],
            "source": spouse_income_sources[i],
            "start_date": spouse_income_start_dates[i],
            "end_date": spouse_income_end_dates[i]
        })

    # Optional notes
    notes = request.form.get("income-notes", "")

    # Save to session
    incomes_data = {
        "person_incomes": person_incomes,
        "spouse_incomes": spouse_incomes,
        "notes": notes
    }

    # Fetch data of all expenses
    person_expense_amounts = request.form.getlist("person_expense_amount[]")
    person_expense_sectors = request.form.getlist("person_expense_sector[]")
    person_expense_start_dates = request.form.getlist("person_expense_start_date[]")
    person_expense_end_dates = request.form.getlist("person_expense_end_date[]")

    spouse_expense_amounts = request.form.getlist("spouse_expense_amount[]")
    spouse_expense_sectors = request.form.getlist("spouse_expense_sector[]")
    spouse_expense_start_dates = request.form.getlist("spouse_expense_start_date[]")
    spouse_expense_end_dates = request.form.getlist("spouse_expense_end_date[]")

    # Build the list of investments
    person_expenses = []
    for i in range(len(person_expense_amounts)):
        person_expenses.append({
            "amount": person_expense_amounts[i],
            "source": person_expense_sectors[i],
            "start_date": person_expense_start_dates[i],
            "end_date": person_expense_end_dates[i]
        })
        
    spouse_expenses = []
    for i in range(len(spouse_expense_amounts)):
        spouse_expenses.append({
            "amount": spouse_expense_amounts[i],
            "source": spouse_expense_sectors[i],
            "start_date": spouse_expense_start_dates[i],
            "end_date": spouse_expense_end_dates[i]
        })

    # Loan expenses
    expense_loan_type = request.form.get("expense_loan_type")
    expense_loan_capital = request.form.get("expense_loan_capital")
    expense_loan_interest = request.form.get("expense_loan_interest")
    expense_loan_due = request.form.get("expense_loan_due")

    spouse_loan_type = request.form.get("spouse_loan_type")
    spouse_loan_capital = request.form.get("spouse_loan_capital")
    spouse_loan_interest = request.form.get("spouse_loan_interest")
    spouse_loan_due = request.form.get("spouse_loan_due")

    person_loan_expense = {
        "type": expense_loan_type,
        "capital": expense_loan_capital,
        "interest": expense_loan_interest,
        "due": expense_loan_due
    }
    spouse_loan_expense = {
        "type": spouse_loan_type,
        "capital": spouse_loan_capital,
        "interest": spouse_loan_interest,
        "due": spouse_loan_due
    }

    # Optional notes
    notes = request.form.get("expense-notes", "")

    # Save to session
    expenses_data = {
        "person_expenses": person_expenses,
        "spouse_expenses": spouse_expenses,
        "person_loan_expense": person_loan_expense,
        "spouse_loan_expense": spouse_loan_expense,
        "notes": notes
    }

    # Fetch data of all loans
    loan_types = request.form.getlist("loan_type[]")
    loan_capital = request.form.getlist("loan_capital[]")
    loan_interest = request.form.getlist("loan_interest[]")
    loan_monthly = request.form.getlist("loan_monthly[]")
    loan_due_date = request.form.getlist("loan_due_date[]")

    # Build the list of investments
    loans = []
    for i in range(len(loan_types)):
        loans.append({
            "type": loan_types[i],
            "capital": loan_capital[i],
            "interest": loan_interest[i],
            "monthly": loan_monthly[i],
            "due_date": loan_due_date[i]
        })

    # Optional notes
    notes = request.form.get("loan-notes", "")

    # Save to session
    loans_data = {
        "loans": loans,
        "notes": notes
    }

    financials = session.get("financials", {})
    financials["incomes"]  = incomes_data
    financials["expenses"] = expenses_data
    financials["loans"]    = loans_data
    session["financials"]  = financials
    with open(f"{DATA_DIR}/{session['current_client_id']}.json", 'r') as f:
        data = json.load(f)
        data["financials"] = financials
    with open(f"{DATA_DIR}/{session['current_client_id']}.json", 'w') as f:
        json.dump(data, f, indent=2)


    return jsonify(success=True)

@user_bp.route("/save_insurances", methods=["POST"])
def save_insurances():
    print(session)
    # Fetch data of all group insurances
    group_insurance = request.form.getlist("group_insurance[]")
    group_expiry = request.form.getlist("group_expiry[]")
    group_life_loss = request.form.getlist("group_life_loss[]")
    group_sickness_income_coverage = request.form.getlist("group_sickness_income_coverage[]")
    group_sickness_disability = request.form.getlist("group_sickness_disability[]")
    group_accident_income_coverage = request.form.getlist("group_accident_income_coverage[]")
    group_accident_disability = request.form.getlist("group_accident_disability[]")
    group_health_coverage = request.form.getlist("group_health_coverage[]")

    # Build the list of group insurances
    group_insurances = []
    for i in range(len(group_expiry)):
        group_insurances.append({
            "insurance": group_insurance[i],
            "expiry": group_expiry[i],
            "life_loss": group_life_loss[i],
            "sickness_income_coverage": group_sickness_income_coverage[i],
            "sickness_disability": group_sickness_disability[i],
            "accident_income_coverage": group_accident_income_coverage[i],
            "accident_disability": group_accident_disability[i],
            "health_coverage": group_health_coverage[i]
        })

    # Fetch data of all individual insurances
    individual_names = request.form.getlist("individual_name[]")
    individual_insurance = request.form.getlist("individual_insurance[]")
    individual_expiry = request.form.getlist("individual_expiry[]")
    individual_life_loss = request.form.getlist("individual_life_loss[]")
    individual_sickness_income_coverage = request.form.getlist("individual_sickness_income_coverage[]")
    individual_sickness_disability = request.form.getlist("individual_sickness_disability[]")
    individual_accident_income_coverage = request.form.getlist("individual_accident_income_coverage[]")
    individual_accident_disability = request.form.getlist("individual_accident_disability[]")
    individual_health_coverage = request.form.getlist("individual_health_coverage[]")

    # Build the list of individual insurances
    individual_insurances = []
    for i in range(len(individual_names)):
        individual_insurances.append({
            "name": individual_names[i],
            "insurance": individual_insurance[i],
            "expiry": individual_expiry[i],
            "life_loss": individual_life_loss[i],
            "sickness_income_coverage": individual_sickness_income_coverage[i],
            "sickness_disability": individual_sickness_disability[i],
            "accident_income_coverage": individual_accident_income_coverage[i],
            "accident_disability": individual_accident_disability[i],
            "health_coverage": individual_health_coverage[i]
        })
        
    # Fetch data of all savings insurances
    savings_insurance = request.form.getlist("savings_insurance[]")
    savings_expiry = request.form.getlist("savings_expiry[]")
    savings_insured = request.form.getlist("savings_insured[]")
    savings_coverage = request.form.getlist("savings_coverage[]")

    # Build the list of group insurances
    savings_insurances = []
    for i in range(len(savings_expiry)):
        savings_insurances.append({
            "insurance": savings_insurance[i],
            "expiry": savings_expiry[i],
            "insured": savings_insured[i],
            "coverage": savings_coverage[i],
        })

    # Fetch data of all property insurances
    property_insurance = request.form.getlist("property_insurance[]")
    property_expiry = request.form.getlist("property_expiry[]")
    property_insured = request.form.getlist("property_insured[]")
    property_coverage = request.form.getlist("property_coverage[]")

    # Build the list of group insurances
    property_insurances = []
    for i in range(len(property_expiry)):
        property_insurances.append({
            "insurance": property_insurance[i],
            "expiry": property_expiry[i],
            "insured": property_insured[i],
            "coverage": property_coverage[i],
        })

    # Fetch data of all vehicle insurances
    vehicle_insurance = request.form.getlist("vehicle_insurance[]")
    vehicle_expiry = request.form.getlist("vehicle_expiry[]")
    vehicle_type = request.form.getlist("vehicle_type[]")
    vehicle_coverage = request.form.getlist("vehicle_coverage[]")

    # Build the list of group insurances
    vehicle_insurances = []
    for i in range(len(vehicle_expiry)):
        vehicle_insurances.append({
            "insurance": vehicle_insurance[i],
            "expiry": vehicle_expiry[i],
            "type": vehicle_type[i],
            "coverage": vehicle_coverage[i],
        })

    # Fetch data of all boat insurances
    boat_insurance = request.form.getlist("boat_insurance[]")
    boat_expiry = request.form.getlist("boat_expiry[]")
    boat_type = request.form.getlist("boat_type[]")
    boat_coverage = request.form.getlist("boat_coverage[]")

    # Build the list of group insurances
    boat_insurances = []
    for i in range(len(boat_expiry)):
        boat_insurances.append({
            "insurance": boat_insurance[i],
            "expiry": boat_expiry[i],
            "type": boat_type[i],
            "coverage": boat_coverage[i],
        })

    group_notes = request.form.get("group-notes", "")
    individual_notes = request.form.get("individual-notes", "")
    savings_notes = request.form.get("savings-notes", "")
    property_notes = request.form.get("property-notes", "")
    vehicle_notes = request.form.get("vehicle-notes", "")
    boat_notes = request.form.get("boat-notes", "")

    # Save to session
    insurances = session["insurances"]
    insurances["group_insurances"] = group_insurances
    insurances["individual_insurances"] = individual_insurances
    insurances["savings_insurances"] = savings_insurances
    insurances["property_insurances"] = property_insurances
    insurances["vehicle_insurances"] = vehicle_insurances
    insurances["boat_insurances"] = boat_insurances
    insurances["group_notes"] = group_notes
    insurances["individual_notes"] = individual_notes
    insurances["savings_notes"] = savings_notes
    insurances["property_notes"] = property_notes
    insurances["vehicle_notes"] = vehicle_notes
    insurances["boat_notes"] = boat_notes
    session["insurances"] = insurances
    with open(f"{DATA_DIR}/{session['current_client_id']}.json", 'r') as f:
        data = json.load(f)
        data["insurances"] = insurances
    with open(f"{DATA_DIR}/{session['current_client_id']}.json", 'w') as f:
        json.dump(data, f, indent=2)

    return jsonify(success=True)



# Client handling function
def load_clients():
    if not os.path.exists(CLIENTS_FILE):
        return []
    with open(CLIENTS_FILE, 'r') as f:
        return json.load(f)

def save_clients(clients):
    with open(CLIENTS_FILE, 'w') as f:
        json.dump(clients, f, indent=2)

@user_bp.route('/add_client', methods=['POST'])
def add_client():
    data = request.json
    client_id = str(uuid.uuid4())
    client = {
        'id': client_id,
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'data_completed': 'No'
    }
    clients = load_clients()
    clients.append(client)
    save_clients(clients)
    with open(f"{DATA_DIR}/{client_id}.json", 'w') as f:
        data = {
            "general": {},
            "financials": {},
            "investments": {},
            "insurances": {},
            "properties": {},
        }
        json.dump({}, f)
    return jsonify(success=True)

@user_bp.route('/edit_client/<client_id>', methods=['POST'])
def edit_client(client_id):
    data = request.json
    clients = load_clients()
    for c in clients:
        if c['id'] == client_id:
            c['name'] = data['name']
            c['email'] = data['email']
            c['phone'] = data['phone']
            break
    save_clients(clients)
    return jsonify(success=True)

@user_bp.route('/delete_client/<client_id>', methods=['POST'])
def delete_client(client_id):
    clients = load_clients()
    clients = [c for c in clients if c['id'] != client_id]
    save_clients(clients)
    try:
        os.remove(f'{DATA_DIR}/{client_id}.json')
    except FileNotFoundError:
        pass
    return jsonify(success=True)

@user_bp.route('/open-client', methods=['POST'])
def open_client():
    client_id = request.form.get('client_id')
    if not client_id:
        return redirect(url_for('index'))

    session['current_client_id'] = client_id
    return redirect(url_for('user.general'))



# Login Page
@user_bp.route('/', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user'] = user['id']
            session['financials'] = {}
            session['insurances'] = {}
            return redirect(url_for('user.clients'))
        else:
            return render_template('user/index.html', error='Μη έγκυρο όνομα χρήστη ή κωδικός πρόσβασης.')

    return render_template('user/index.html')

# Logout
@user_bp.route('/logout', methods=['POST'])
def logout_user():
    session.clear()
    return redirect(url_for('user.login_user'))


# Authentication check
def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('user.login_user'))
        return func(*args, **kwargs)
    return decorated_function

def nocache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache_view


# Protected User Pages
@user_bp.route('/clients')
@login_required
@nocache
def clients():
    clients = load_clients()
    return render_template('user/pages/clients.html', clients=clients)

@user_bp.route('/general')
@login_required
@nocache
def general():
    return render_template('user/pages/general.html')

@user_bp.route('/financials')
@login_required
@nocache
def financials():
    return render_template('user/pages/financials.html')

@user_bp.route('/investments')
@login_required
@nocache
def investments():
    return render_template('user/pages/investments.html')

@user_bp.route('/properties')
@login_required
@nocache
def properties():
    return render_template('user/pages/properties.html')

@user_bp.route('/insurances')
@login_required
@nocache
def insurances():
    return render_template('user/pages/insurances.html')

@user_bp.route('/study')
@login_required
@nocache
def study():
    income_data = session["financials"].get("incomes", None)
    expense_data = session["financials"].get("expenses", None)
    if income_data is None or expense_data is None:
        return render_template('user/pages/study.html', error="Παρακαλώ, εισαγάγετε πρώτα τα δεδομένα εισοδήματος και εξόδων για να δείτε την ανάλυση.")

    total_income = 0
    income_items = []
    for item in income_data["person_incomes"]:
        formatted_income = locale.currency(float(item["amount"]), symbol=False, grouping=True)  # '74.000,00'
        income_items.append({"source": item["source"], "amount": float(item["amount"]), "formatted_amount": formatted_income})
        total_income += float(item["amount"])

    for item in income_data["spouse_incomes"]:
        formatted_income = locale.currency(float(item["amount"]), symbol=False, grouping=True)  # '74.000,00'
        income_items.append({"source": item["source"] + " Σύζυγος", "amount": float(item["amount"]), "formatted_amount": formatted_income})
        total_income += float(item["amount"])

    total_expenses = 0
    expense_items = []
    for item in expense_data["person_expenses"]:
        formatted_expense = locale.currency(float(item["amount"]), symbol=False, grouping=True)  # '74.000,00'
        expense_items.append({"source": item["source"], "amount": float(item["amount"]), "formatted_amount": formatted_expense})
        total_expenses += float(item["amount"])

    for item in expense_data["spouse_expenses"]:
        formatted_expense = locale.currency(float(item["amount"]), symbol=False, grouping=True)  # '74.000,00'
        expense_items.append({"source": item["source"] + " Σύζυγος", "amount": float(item["amount"]), "formatted_amount": formatted_expense})
        total_expenses += float(item["amount"])

    monthly_income = total_income / 12
    monthly_expenses = total_expenses / 12
    balance = total_income - total_expenses
    monthly_balance = balance / 12

    formatted_total_expenses = locale.currency(total_expenses, symbol=False, grouping=True)  # '74.000,00'
    formatted_total_income = locale.currency(total_income, symbol=False, grouping=True)  # '74.000,00'
    formatted_monthly_income = locale.currency(monthly_income, symbol=False, grouping=True)  # '74.000,00'
    formatted_monthly_expenses = locale.currency(monthly_expenses, symbol=False, grouping=True)  # '74.000,00'
    formatted_balance = locale.currency(balance, symbol=False, grouping=True)  # '74.000,00'
    formatted_monthly_balance = locale.currency(monthly_balance, symbol=False, grouping=True)  # '74.000,00'
    year = str(datetime.now().year)

    return render_template(
        'user/pages/study.html',
        income_items=income_items,
        total_income=formatted_total_income,
        expense_items=expense_items,
        total_expenses=formatted_total_expenses,
        monthly_income=formatted_monthly_income,
        monthly_expenses=formatted_monthly_expenses,
        balance=formatted_balance,
        monthly_balance=formatted_monthly_balance,
        year=year,
        income_labels=["inc1", "inc2asdasd", "inc4", "inc5", "inc6", "inc7", "inc3"],
        income_data=[22, 11, 33, 35, 35, 35, 35],
        expense_labels=["Exp1", "Exp2", "Exp3"],
        expense_data=[10, 20, 30]
    )

@user_bp.route('/generate_pdf', methods=['POST'])
@login_required
@nocache
def generate_pdf():
    income_data = session["financials"].get("incomes", None)
    expense_data = session["financials"].get("expenses", None)
    if income_data is None or expense_data is None:
        return render_template('user/pages/study.html', error="Παρακαλώ, εισαγάγετε πρώτα τα δεδομένα εισοδήματος και εξόδων για να δείτε την ανάλυση.")

    total_income = 0
    income_items = []
    for item in income_data["person_incomes"]:
        formatted_income = locale.currency(float(item["amount"]), symbol=False, grouping=True)  # '74.000,00'
        income_items.append({"source": item["source"], "amount": float(item["amount"]), "formatted_amount": formatted_income})
        total_income += float(item["amount"])

    for item in income_data["spouse_incomes"]:
        formatted_income = locale.currency(float(item["amount"]), symbol=False, grouping=True)  # '74.000,00'
        income_items.append({"source": item["source"] + " Σύζυγος", "amount": float(item["amount"]), "formatted_amount": formatted_income})
        total_income += float(item["amount"])

    total_expenses = 0
    expense_items = []
    for item in expense_data["person_expenses"]:
        formatted_expense = locale.currency(float(item["amount"]), symbol=False, grouping=True)  # '74.000,00'
        expense_items.append({"source": item["source"], "amount": float(item["amount"]), "formatted_amount": formatted_expense})
        total_expenses += float(item["amount"])

    for item in expense_data["spouse_expenses"]:
        formatted_expense = locale.currency(float(item["amount"]), symbol=False, grouping=True)  # '74.000,00'
        expense_items.append({"source": item["source"] + " Σύζυγος", "amount": float(item["amount"]), "formatted_amount": formatted_expense})
        total_expenses += float(item["amount"])

    monthly_income = total_income / 12
    monthly_expenses = total_expenses / 12
    balance = total_income - total_expenses
    monthly_balance = balance / 12

    formatted_total_expenses = locale.currency(total_expenses, symbol=False, grouping=True)  # '74.000,00'
    formatted_total_income = locale.currency(total_income, symbol=False, grouping=True)  # '74.000,00'
    formatted_monthly_income = locale.currency(monthly_income, symbol=False, grouping=True)  # '74.000,00'
    formatted_monthly_expenses = locale.currency(monthly_expenses, symbol=False, grouping=True)  # '74.000,00'
    formatted_balance = locale.currency(balance, symbol=False, grouping=True)  # '74.000,00'
    formatted_monthly_balance = locale.currency(monthly_balance, symbol=False, grouping=True)  # '74.000,00'
    year = str(datetime.now().year)

    data = {
        "year": year,
        "incomes": income_items,
        "expenses": expense_items,
        "total_income": formatted_total_income,
        "total_expenses": formatted_total_expenses,
        "monthly_income": formatted_monthly_income,
        "monthly_expenses": formatted_monthly_expenses,
        "balance": formatted_balance,
        "monthly_balance": formatted_monthly_balance
    }


    # Build PDF
    buffer = generate_report(data)
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='study_report.pdf')


