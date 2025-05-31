from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'crm_secret_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- Models ---
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    company = db.Column(db.String(100))
    source = db.Column(db.String(50), default='Unknown')
    industry = db.Column(db.String(50), default='General')
    stage = db.Column(db.String(20), default='Lead')
    score = db.Column(db.Integer, default=0)
    owner = db.Column(db.String(20), default='Marketing')
    last_engaged = db.Column(db.DateTime, default=datetime.utcnow)
    deal_size = db.Column(db.Integer, default=0)
    objections = db.Column(db.Text)
    decision_date = db.Column(db.String(20))
    champion = db.Column(db.Boolean, default=False)
    contract_signed = db.Column(db.Boolean, default=False)
    demo_booked = db.Column(db.Boolean, default=False)
    resource_downloaded = db.Column(db.Boolean, default=False)

    def update_stage(self):
        if self.stage == 'Lead' and self.score >= 10:
            self.stage = 'MQL'
            self.owner = 'Marketing'
        elif self.stage == 'MQL' and self.score >= 20:
            self.stage = 'SQL'
            self.owner = 'Sales'
        elif self.stage == 'SQL' and self.champion:
            self.stage = 'Champion'
            self.owner = 'Sales'
        if self.contract_signed:
            self.stage = 'Customer'
            self.owner = 'CS'
        db.session.commit()

# --- Visualization Helpers ---
def plot_to_base64(plt):
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_base64

def create_funnel_plot(stages, counts):
    plt.figure(figsize=(8,6))
    plt.barh(stages, counts, color='skyblue')
    plt.xlabel('Number of Leads')
    plt.title('Sales Funnel Stages')
    return plot_to_base64(plt)

def create_cac_plot(data):
    plt.figure(figsize=(8,4))
    plt.bar(data['Channel'], data['Cost per Conversion'], color='salmon')
    plt.ylabel('Cost per Conversion (₹)')
    plt.title('Customer Acquisition Cost (CAC) by Channel')
    return plot_to_base64(plt)

def create_ltv_plot(data):
    plt.figure(figsize=(8,4))
    plt.bar(data['Channel'], data['LTV:CAC'], color='lightgreen')
    plt.ylabel('LTV:CAC Ratio')
    plt.title('LTV to CAC Ratio by Channel')
    return plot_to_base64(plt)

def get_funnel_img():
    # Demo values from assignment
    stages = ['Lead', 'MQL', 'SQL', 'Customer']
    counts = [4500, 900, 450, 65]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    plt.figure(figsize=(8,5))
    bars = plt.bar(stages, counts, color=colors)
    plt.title('Sales Funnel Stages (Demo Values)')
    plt.ylabel('Number of Leads')
    plt.xlabel('Funnel Stage')

    # Add count labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height, '%d' % int(height),
                 ha='center', va='bottom', fontsize=12, fontweight='bold')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_base64

# --- Routes ---
@app.route('/')
def index():
    leads = Lead.query.order_by(Lead.last_engaged.desc()).all()
    return render_template('index.html', leads=leads)

@app.route('/dashboard')
def dashboard():
    # --- Use demo values for funnel stages as per assignment ---
    funnel_stages = ['Lead', 'MQL', 'SQL', 'Customer']
    funnel_counts = [4500, 900, 450, 65]
    funnel_img = create_funnel_plot(funnel_stages, funnel_counts)

    # --- CAC and LTV:CAC using assignment mock data ---
    mock_data = {
        'Channel': ['Facebook Ads', 'Email Campaign', 'LinkedIn DMs'],
        'Leads': [3000, 1000, 500],
        'Cost': [90000, 10000, 25000],
        'Conversions': [30, 25, 10]
    }
    df = pd.DataFrame(mock_data)
    df['Cost per Conversion'] = df['Cost'] / df['Conversions']
    df['LTV'] = [7500, 12000, 9000]  # Assumed LTV values
    df['LTV:CAC'] = df['LTV'] / df['Cost per Conversion']

    cac_img = create_cac_plot(df)
    ltv_img = create_ltv_plot(df)

    # Identify underperforming channel
    underperforming = df.loc[df['Cost per Conversion'].idxmax()]
    experiments = [
        "Test new ad creatives focusing on enterprise pain points",
        "Implement dynamic landing pages with case study recommendations"
    ]
    
    # Convert underperforming series to dict
    underperforming = df.loc[df['Cost per Conversion'].idxmax()].to_dict()

    return render_template('dashboard.html',
                         funnel_img=funnel_img,
                         cac_img=cac_img,
                         ltv_img=ltv_img,
                         underperforming=underperforming,
                         experiments=experiments)

    return render_template('dashboard.html',
                         funnel_img=funnel_img,
                         cac_img=cac_img,
                         ltv_img=ltv_img,
                         underperforming=underperforming,
                         experiments=experiments)

# --- Lead Management Routes --- 
@app.route('/add', methods=['GET', 'POST'])
def add_lead():
    if request.method == 'POST':
        new_lead = Lead(
            name=request.form['name'],
            email=request.form['email'],
            company=request.form['company'],
            source=request.form.get('source', 'Unknown'),
            industry=request.form.get('industry', 'General'),
            score=int(request.form.get('score', 0)),
            deal_size=int(request.form.get('deal_size', 0)),
            objections=request.form.get('objections', ''),
            demo_booked='demo_booked' in request.form,
            resource_downloaded='resource_downloaded' in request.form,
            champion='champion' in request.form,
            contract_signed='contract_signed' in request.form
        )
        new_lead.update_stage()
        db.session.add(new_lead)
        db.session.commit()
        flash('New lead added!')
        return redirect(url_for('index'))
    return render_template('add_lead.html')

@app.route('/delete/<int:id>', methods=['POST'])
def delete_lead(id):
    lead = Lead.query.get_or_404(id)
    db.session.delete(lead)
    db.session.commit()
    flash('Lead deleted!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
