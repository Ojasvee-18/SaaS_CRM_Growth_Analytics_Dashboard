from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
db = SQLAlchemy(app)


def create_funnel_chart(stage_counts, stages):
    fig, ax = plt.subplots()
    ax.barh(stages, stage_counts, color='skyblue')
    ax.set_xlabel('Number of Leads')
    ax.set_title('Sales Funnel')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

def create_cac_chart(cac_df):
    fig, ax = plt.subplots()
    ax.bar(cac_df['Channel'], cac_df['Cost per Conversion'], color='coral')
    ax.set_ylabel('Cost per Conversion')
    ax.set_title('CAC by Channel')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64





# --- Models ---
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    company = db.Column(db.String(120))
    source = db.Column(db.String(64))
    industry = db.Column(db.String(64))
    stage = db.Column(db.String(32), default='Unknown')
    score = db.Column(db.Integer, default=0)
    owner = db.Column(db.String(32), default='Marketing')
    last_engaged = db.Column(db.DateTime, default=datetime.utcnow)
    deal_size = db.Column(db.Integer, default=0)
    objections = db.Column(db.Text)
    decision_timeline = db.Column(db.String(64))
    champion = db.Column(db.Boolean, default=False)
    contract_signed = db.Column(db.Boolean, default=False)

    def update_stage(self):
        if self.stage == 'Lead' and self.score >= 10:
            self.stage = 'MQL'
            self.owner = 'Marketing'
        if self.stage == 'MQL' and self.score >= 20:
            self.stage = 'SQL'
            self.owner = 'Sales'
        if self.stage == 'SQL' and self.champion:
            self.stage = 'Champion Identified'
            self.owner = 'Sales'
        if self.contract_signed:
            self.stage = 'Customer'
            self.owner = 'CS'

# --- Routes ---
@app.route('/')
def index():
    leads = Lead.query.all()
    return render_template('index.html', leads=leads)

@app.route('/add-lead', methods=['GET', 'POST'])
def add_lead():
    if request.method == 'POST':
        lead = Lead(
            name=request.form['name'],
            email=request.form['email'],
            company=request.form['company'],
            source=request.form['source'],
            industry=request.form['industry'],
            score=int(request.form.get('score', 0)),
            deal_size=int(request.form.get('deal_size', 0)),
            objections=request.form.get('objections', ''),
            decision_timeline=request.form.get('decision_timeline', '')
        )
        db.session.add(lead)
        db.session.commit()
        flash('Lead added!')
        return redirect(url_for('index'))
    return render_template('lead_form.html')

@app.route('/update-lead/<int:lead_id>', methods=['POST'])
def update_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    lead.score = int(request.form.get('score', lead.score))
    lead.champion = 'champion' in request.form
    lead.contract_signed = 'contract_signed' in request.form
    lead.update_stage()
    lead.last_engaged = datetime.utcnow()
    db.session.commit()
    flash('Lead updated!')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    # Funnel data
    stages = ['Lead', 'MQL', 'SQL', 'Champion', 'Customer']
    stage_counts = [Lead.query.filter_by(stage=stage).count() for stage in stages]

    # CAC data (using your assignment's mock data)
    cac_data = {
        'Channel': ['Facebook Ads', 'Email Campaign', 'LinkedIn DMs'],
        'Cost': [90000, 10000, 25000],
        'Conversions': [30, 25, 10]
    }
    import pandas as pd
    cac_df = pd.DataFrame(cac_data)
    cac_df['Cost per Conversion'] = cac_df['Cost'] / cac_df['Conversions']

    # Generate charts
    funnel_img = create_funnel_chart(stage_counts, stages)
    cac_img = create_cac_chart(cac_df)

    return render_template('dashboard.html', funnel_img=funnel_img, cac_img=cac_img)



# --- Nurturing Logic (simplified) ---
def assign_nurture_track(lead):
    if lead.stage == 'SQL' and not lead.contract_signed:
        return 'high_intent'
    elif lead.stage == 'MQL':
        return 'mid_intent'
    else:
        return 'low_intent'

def get_nurture_content(track):
    if track == 'high_intent':
        return ['Founder note', 'Discount offer', 'Case study']
    if track == 'mid_intent':
        return ['Customer story', 'ROI calculator']
    return ['Industry report', 'Product tips']

# --- Analytics Example ---
@app.route('/analytics')
def analytics():
    # Mock data for CAC
    data = {
        'Channel': ['Facebook Ads', 'Email Campaign', 'LinkedIn DMs'],
        'Leads': [3000, 1000, 500],
        'Cost': [90000, 10000, 25000],
        'Conversions': [30, 25, 10]
    }
    df = pd.DataFrame(data)
    df['Conversion Rate'] = df['Conversions'] / df['Leads']
    df['Cost per Conversion'] = df['Cost'] / df['Conversions']
    underperforming = df.sort_values('Cost per Conversion', ascending=False).iloc[0]['Channel']
    return f"Underperforming Channel: {underperforming}<br><br>{df.to_html()}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


