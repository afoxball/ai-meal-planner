from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import MealPlan

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with recent meal plans."""
    recent_plans = MealPlan.query.filter_by(user_id=current_user.id)\
        .order_by(MealPlan.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', recent_plans=recent_plans)
