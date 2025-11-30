import json
import os
from datetime import date, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import MealPreference, MealPlan, Meal
from app.forms import MealPreferencesForm, GenerateMealPlanForm

meals_bp = Blueprint('meals', __name__)


def get_gemini_client():
    """Initialize Gemini AI client."""
    import google.generativeai as genai
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')


def generate_meal_plan_with_ai(preferences, additional_notes=''):
    """Generate a meal plan using Gemini AI."""
    model = get_gemini_client()
    if not model:
        return None

    # Build the prompt
    prompt = build_meal_plan_prompt(preferences, additional_notes)

    try:
        response = model.generate_content(prompt)
        return parse_meal_plan_response(response.text)
    except Exception as e:
        print(f"Error generating meal plan: {e}")
        return None


def build_meal_plan_prompt(preferences, additional_notes):
    """Build the AI prompt based on user preferences."""
    dietary_restrictions = json.loads(preferences.dietary_restrictions or '[]')
    allergies = json.loads(preferences.allergies or '[]')
    favorite_foods = json.loads(preferences.favorite_foods or '[]')
    disliked_foods = json.loads(preferences.disliked_foods or '[]')
    preferred_cuisines = json.loads(preferences.preferred_cuisines or '[]')

    prompt = f"""You are a professional meal planner. Create a 7-day meal plan based on these preferences:

DIETARY RESTRICTIONS: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}
ALLERGIES: {', '.join(allergies) if allergies else 'None'}
FAVORITE FOODS: {', '.join(favorite_foods) if favorite_foods else 'Not specified'}
DISLIKED FOODS: {', '.join(disliked_foods) if disliked_foods else 'None'}
PREFERRED CUISINES: {', '.join(preferred_cuisines) if preferred_cuisines else 'Any'}

PRIMARY GOAL: {preferences.primary_goal}
DAILY TARGETS: {preferences.calorie_target or 'Not specified'} calories, {preferences.protein_target or 'Not specified'}g protein, {preferences.carb_target or 'Not specified'}g carbs, {preferences.fat_target or 'Not specified'}g fat

MEALS PER DAY: {preferences.meals_per_day}
COOKING SKILL: {preferences.cooking_skill}
PREP TIME: {preferences.prep_time_preference}
BUDGET: {preferences.budget}

{f'ADDITIONAL NOTES: {additional_notes}' if additional_notes else ''}

IMPORTANT: Maximize ingredient reuse across meals to reduce waste and shopping. Group meals that share ingredients on consecutive days.

Return a JSON object with this EXACT structure (no markdown, just raw JSON):
{{
    "meals": [
        {{
            "day": 0,
            "meal_type": "breakfast",
            "name": "Meal Name",
            "description": "Brief description",
            "ingredients": ["ingredient 1", "ingredient 2"],
            "instructions": "Step by step instructions",
            "prep_time": 15,
            "cook_time": 20,
            "calories": 400,
            "protein": 25,
            "carbs": 35,
            "fat": 15
        }}
    ],
    "shopping_list": {{
        "produce": ["item 1", "item 2"],
        "protein": ["item 1"],
        "dairy": ["item 1"],
        "grains": ["item 1"],
        "pantry": ["item 1"],
        "other": ["item 1"]
    }},
    "tips": ["Tip 1 for ingredient reuse", "Tip 2"]
}}

Include all meals for 7 days (day 0 = Monday through day 6 = Sunday).
Include {preferences.meals_per_day} meals per day.
Meal types should be: breakfast, lunch, dinner, snack (as needed).
"""
    return prompt


def parse_meal_plan_response(response_text):
    """Parse the AI response into structured data."""
    try:
        # Clean up the response - remove markdown code blocks if present
        cleaned = response_text.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        if cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]

        return json.loads(cleaned.strip())
    except json.JSONDecodeError as e:
        print(f"Error parsing AI response: {e}")
        print(f"Response: {response_text[:500]}")
        return None


@meals_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """Edit meal preferences."""
    pref = MealPreference.query.filter_by(user_id=current_user.id).first()

    if pref:
        # Pre-populate form with existing preferences
        form = MealPreferencesForm(obj=pref)
        # Handle JSON fields
        if request.method == 'GET':
            form.dietary_restrictions.data = json.loads(pref.dietary_restrictions or '[]')
            form.preferred_cuisines.data = json.loads(pref.preferred_cuisines or '[]')
            allergies = json.loads(pref.allergies or '[]')
            form.allergies.data = ', '.join(allergies) if allergies else ''
            favorites = json.loads(pref.favorite_foods or '[]')
            form.favorite_foods.data = ', '.join(favorites) if favorites else ''
            disliked = json.loads(pref.disliked_foods or '[]')
            form.disliked_foods.data = ', '.join(disliked) if disliked else ''
    else:
        form = MealPreferencesForm()

    if form.validate_on_submit():
        if not pref:
            pref = MealPreference(user_id=current_user.id)
            db.session.add(pref)

        # Update preferences
        pref.dietary_restrictions = json.dumps(form.dietary_restrictions.data)
        pref.allergies = json.dumps([a.strip() for a in form.allergies.data.split(',') if a.strip()])
        pref.favorite_foods = json.dumps([f.strip() for f in form.favorite_foods.data.split(',') if f.strip()])
        pref.disliked_foods = json.dumps([d.strip() for d in form.disliked_foods.data.split(',') if d.strip()])
        pref.primary_goal = form.primary_goal.data
        pref.calorie_target = form.calorie_target.data
        pref.protein_target = form.protein_target.data
        pref.carb_target = form.carb_target.data
        pref.fat_target = form.fat_target.data
        pref.preferred_cuisines = json.dumps(form.preferred_cuisines.data)
        pref.meals_per_day = int(form.meals_per_day.data)
        pref.cooking_skill = form.cooking_skill.data
        pref.prep_time_preference = form.prep_time_preference.data
        pref.budget = form.budget.data

        db.session.commit()
        flash('Preferences saved successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('meals/preferences.html', form=form)


# Import request at the top
from flask import request


@meals_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    """Generate a new meal plan."""
    pref = MealPreference.query.filter_by(user_id=current_user.id).first()

    if not pref:
        flash('Please set your meal preferences first.', 'warning')
        return redirect(url_for('meals.preferences'))

    form = GenerateMealPlanForm()

    if form.validate_on_submit():
        # Generate meal plan with AI
        plan_data = generate_meal_plan_with_ai(pref, form.additional_notes.data)

        if not plan_data:
            flash('Unable to generate meal plan. Please check your API key or try again later.', 'danger')
            return render_template('meals/generate.html', form=form)

        # Calculate week start (next Monday)
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        week_start = today + timedelta(days=days_until_monday)

        # Create meal plan
        meal_plan = MealPlan(
            user_id=current_user.id,
            week_start=week_start,
            plan_data=json.dumps(plan_data),
            shopping_list=json.dumps(plan_data.get('shopping_list', {}))
        )
        db.session.add(meal_plan)
        db.session.flush()  # Get the meal_plan.id

        # Create individual meal records
        for meal_data in plan_data.get('meals', []):
            meal = Meal(
                meal_plan_id=meal_plan.id,
                day_of_week=meal_data.get('day', 0),
                meal_type=meal_data.get('meal_type', 'lunch'),
                name=meal_data.get('name', 'Unnamed Meal'),
                description=meal_data.get('description', ''),
                ingredients=json.dumps(meal_data.get('ingredients', [])),
                instructions=meal_data.get('instructions', ''),
                prep_time=meal_data.get('prep_time'),
                cook_time=meal_data.get('cook_time'),
                calories=meal_data.get('calories'),
                protein=meal_data.get('protein'),
                carbs=meal_data.get('carbs'),
                fat=meal_data.get('fat')
            )
            db.session.add(meal)

        db.session.commit()
        flash('Meal plan generated successfully!', 'success')
        return redirect(url_for('meals.view_plan', plan_id=meal_plan.id))

    return render_template('meals/generate.html', form=form)


@meals_bp.route('/plan/<int:plan_id>')
@login_required
def view_plan(plan_id):
    """View a meal plan."""
    plan = MealPlan.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    plan_data = json.loads(plan.plan_data)
    shopping_list = json.loads(plan.shopping_list) if plan.shopping_list else {}

    # Organize meals by day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    organized_meals = {i: [] for i in range(7)}
    for meal in plan_data.get('meals', []):
        day = meal.get('day', 0)
        if 0 <= day <= 6:
            organized_meals[day].append(meal)

    return render_template('meals/view_plan.html',
                           plan=plan,
                           days=days,
                           organized_meals=organized_meals,
                           shopping_list=shopping_list,
                           tips=plan_data.get('tips', []))


@meals_bp.route('/history')
@login_required
def history():
    """View meal plan history."""
    plans = MealPlan.query.filter_by(user_id=current_user.id)\
        .order_by(MealPlan.created_at.desc()).all()
    return render_template('meals/history.html', plans=plans)
