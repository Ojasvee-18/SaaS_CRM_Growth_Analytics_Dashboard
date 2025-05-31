from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.io as pio
import json
from flask_migrate import Migrate
from plotly.utils import PlotlyJSONEncoder

import matplotlib.pyplot as plt
import io
import base64


app = Flask(__name__)
app.secret_key = 'crm_secret_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
db = SQLAlchemy(app)

def plot_to_img_tag(plt):
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return f"data:image/png;base64,{img_base64}"





# --- Models ---
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    company = db.Column(db.String(100))
    source = db.Column(db.String(50))  # Facebook, Email, LinkedIn
    industry = db.Column(db.String(50))
    stage = db.Column(db.String(20), default='Lead')
    score = db.Column(db.Integer, default=0)
    owner = db.Column(db.String(20), default='Marketing')
    last_engaged = db.Column(db.DateTime, default=datetime.utcnow)
    deal_size = db.Column(db.Integer)
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

@app.route('/')
def index():
    leads = Lead.query.order_by(Lead.last_engaged.desc()).all()
    return render_template('index.html', leads=leads)

@app.route('/add', methods=['GET', 'POST'])
def add_lead():
    if request.method == 'POST':
        new_lead = Lead(
            name=request.form['name'],
            email=request.form['email'],
            company=request.form['company'],
            source=request.form['source'],
            industry=request.form['industry'],
            score=int(request.form.get('score', 0)),
            deal_size=int(request.form.get('deal_size', 0)),
            objections=request.form.get('objections'),
            decision_date=request.form.get('decision_date'),
            demo_booked='demo_booked' in request.form,
            resource_downloaded='resource_downloaded' in request.form,
            champion='champion' in request.form,
            contract_signed='contract_signed' in request.form
        )
        db.session.add(new_lead)
        db.session.commit()
        flash('New lead added!')
        return redirect(url_for('index'))
    return render_template('add_lead.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_lead(id):
    lead = Lead.query.get_or_404(id)
    if request.method == 'POST':
        lead.name = request.form['name']
        lead.email = request.form['email']
        lead.company = request.form['company']
        lead.source = request.form['source']
        lead.industry = request.form['industry']
        lead.score = int(request.form['score'])
        lead.deal_size = int(request.form['deal_size'])
        lead.objections = request.form['objections']
        lead.decision_date = request.form['decision_date']
        lead.demo_booked = 'demo_booked' in request.form
        lead.resource_downloaded = 'resource_downloaded' in request.form
        lead.champion = 'champion' in request.form
        lead.contract_signed = 'contract_signed' in request.form
        lead.update_stage()
        db.session.commit()
        flash('Lead updated!')
        return redirect(url_for('index'))
    return render_template('edit_lead.html', lead=lead)

@app.route('/dashboard')
def dashboard():
    # --- Funnel plot ---
    stages = ['Lead', 'MQL', 'SQL', 'Champion', 'Customer']
    # Example: replace with your actual counts from DB
    stage_counts = [Lead.query.filter_by(stage=s).count() for s in stages]
    plt.figure(figsize=(6,4))
    plt.barh(stages, stage_counts, color='skyblue')
    plt.xlabel('Number of Leads')
    plt.title('Sales Funnel')
    funnel_img = plot_to_img_tag(plt)

    # --- CAC plot ---
    cac_data = {
        'Channel': ['Facebook Ads', 'Email Campaign', 'LinkedIn DMs'],
        'Cost per Conversion': [3000, 400, 2500]
    }
    plt.figure(figsize=(6,4))
    plt.bar(cac_data['Channel'], cac_data['Cost per Conversion'], color='salmon')
    plt.ylabel('Cost per Conversion (₹)')
    plt.title('CAC by Channel')
    cac_img = plot_to_img_tag(plt)

    # --- LTV:CAC plot ---
    ltv_data = {
        'Channel': ['Facebook Ads', 'Email Campaign', 'LinkedIn DMs'],
        'LTV:CAC': [5, 30, 4]
    }
    plt.figure(figsize=(6,4))
    plt.bar(ltv_data['Channel'], ltv_data['LTV:CAC'], color='lightgreen')
    plt.ylabel('LTV:CAC Ratio')
    plt.title('LTV:CAC Ratio by Channel')
    ltv_img = plot_to_img_tag(plt)

    return render_template('dashboard.html',
        funnel_img=funnel_img,
        cac_img=cac_img,
        ltv_img=ltv_img
    )



def calculate_cac():
    data = {
        'Channel': ['Facebook Ads', 'Email Campaign', 'LinkedIn DMs'],
        'Leads': [3000, 1000, 500],
        'Cost': [90000, 10000, 25000],
        'Conversions': [30, 25, 10]
    }
    df = pd.DataFrame(data)
    df['Cost per Conversion'] = df['Cost'] / df['Conversions']
    return df

def calculate_ltv():
    df = calculate_cac()
    df['LTV'] = [15000, 18000, 12000]  # Example values
    df['LTV:CAC'] = df['LTV'] / df['Cost per Conversion']
    return df

@app.route('/nurture/<int:id>')
def nurture_lead(id):
    lead = Lead.query.get_or_404(id)
    track = assign_nurture_track(lead)
    content = get_nurture_content(track)
    personalized_content = {
        'email_subject': f"Custom solution for {lead.company}",
        'body': f"Hi {lead.name}, we noticed your interest in our SaaS platform..."
    }
    return render_template('nurture.html', 
                         lead=lead, 
                         track=track,
                         content=content,
                         personalized=personalized_content)
    
@app.route('/seed-mock-data')
def seed_mock_data():
    # Remove all existing leads (optional, for a clean start)
    Lead.query.delete()
    db.session.commit()

    # Facebook Ads: 3000 leads, 30 conversions (Customer)
    for i in range(2970):
        db.session.add(Lead(
            name=f"FB_Lead_{i+1}",
            email=f"fb_lead_{i+1}@example.com",
            company="FB Company",
            source="Facebook Ads",
            industry="SaaS",
            stage="Lead",
            score=5,
            owner="Marketing"
        ))
    for i in range(30):
        db.session.add(Lead(
            name=f"FB_Customer_{i+1}",
            email=f"fb_customer_{i+1}@example.com",
            company="FB Company",
            source="Facebook Ads",
            industry="SaaS",
            stage="Customer",
            score=30,
            owner="CS",
            contract_signed=True
        ))

    # Email Campaign: 1000 leads, 25 conversions
    for i in range(975):
        db.session.add(Lead(
            name=f"Email_Lead_{i+1}",
            email=f"email_lead_{i+1}@example.com",
            company="Email Co",
            source="Email Campaign",
            industry="SaaS",
            stage="Lead",
            score=5,
            owner="Marketing"
        ))
    for i in range(25):
        db.session.add(Lead(
            name=f"Email_Customer_{i+1}",
            email=f"email_customer_{i+1}@example.com",
            company="Email Co",
            source="Email Campaign",
            industry="SaaS",
            stage="Customer",
            score=30,
            owner="CS",
            contract_signed=True
        ))

    # LinkedIn DMs: 500 leads, 10 conversions
    for i in range(490):
        db.session.add(Lead(
            name=f"LI_Lead_{i+1}",
            email=f"li_lead_{i+1}@example.com",
            company="LinkedIn Co",
            source="LinkedIn DMs",
            industry="SaaS",
            stage="Lead",
            score=5,
            owner="Marketing"
        ))
    for i in range(10):
        db.session.add(Lead(
            name=f"LI_Customer_{i+1}",
            email=f"li_customer_{i+1}@example.com",
            company="LinkedIn Co",
            source="LinkedIn DMs",
            industry="SaaS",
            stage="Customer",
            score=30,
            owner="CS",
            contract_signed=True
        ))

    db.session.commit()
    return "Mock data seeded! Go to /dashboard to view."


def assign_nurture_track(lead):
    if lead.demo_booked and not lead.contract_signed:
        return 'high'
    elif lead.resource_downloaded:
        return 'mid'
    return 'low'

def get_nurture_content(track):
    content_map = {
        'high': [
            {'type': 'case_study', 'title': 'Enterprise Success Story'},
            {'type': 'discount', 'value': '15% limited offer'}
        ],
        'mid': [
            {'type': 'webinar', 'title': 'Advanced Features Workshop'},
            {'type': 'checklist', 'title': 'Implementation Guide'}
        ],
        'low': [
            {'type': 'newsletter', 'title': 'Monthly Industry Insights'},
            {'type': 'ebook', 'title': "Beginner's Guide to SaaS"}
        ]
    }
    return content_map.get(track, [])

@app.route('/experiment/facebook-creative')
def facebook_experiment():
    experiment_data = {
        'version': ['Original', 'Variation A', 'Variation B'],
        'conversions': [30, 38, 42],
        'cost': [90000, 85000, 88000]
    }
    fig = px.bar(experiment_data, x='version', y='conversions',
                title='Facebook Ad Creative Test Results')
    graph_json = json.dumps(fig, cls=pio.utils.PlotlyJSONEncoder)
    return render_template('experiment.html', graph_json=graph_json)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
migrate = Migrate(app, db)