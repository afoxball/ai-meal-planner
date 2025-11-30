from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, TextAreaField,
                     SelectField, IntegerField, SelectMultipleField, BooleanField)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange


class RegistrationForm(FlaskForm):
    """User registration form."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """User login form."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class MealPreferencesForm(FlaskForm):
    """Form for collecting user meal preferences."""
    # Dietary restrictions
    dietary_restrictions = SelectMultipleField('Dietary Restrictions', choices=[
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pescatarian'),
        ('gluten_free', 'Gluten-Free'),
        ('dairy_free', 'Dairy-Free'),
        ('keto', 'Keto'),
        ('paleo', 'Paleo'),
        ('halal', 'Halal'),
        ('kosher', 'Kosher'),
    ])

    allergies = TextAreaField('Food Allergies (comma-separated)', validators=[Optional()])

    favorite_foods = TextAreaField('Favorite Foods (comma-separated)', validators=[
        DataRequired(message='Please enter at least a few favorite foods')
    ])

    disliked_foods = TextAreaField('Foods You Dislike (comma-separated)', validators=[Optional()])

    # Goals
    primary_goal = SelectField('Primary Meal Goal', choices=[
        ('pleasure', 'Pleasure & Enjoyment'),
        ('fitness', 'Fitness & Performance'),
        ('macro_awareness', 'Macro/Calorie Tracking'),
        ('variety', 'Culinary Variety'),
        ('budget', 'Budget-Friendly'),
        ('quick', 'Quick & Easy Meals'),
    ], validators=[DataRequired()])

    calorie_target = IntegerField('Daily Calorie Target', validators=[
        Optional(),
        NumberRange(min=1000, max=5000, message='Calories should be between 1000-5000')
    ])

    protein_target = IntegerField('Daily Protein Target (g)', validators=[
        Optional(),
        NumberRange(min=30, max=300, message='Protein should be between 30-300g')
    ])

    carb_target = IntegerField('Daily Carb Target (g)', validators=[
        Optional(),
        NumberRange(min=20, max=500, message='Carbs should be between 20-500g')
    ])

    fat_target = IntegerField('Daily Fat Target (g)', validators=[
        Optional(),
        NumberRange(min=20, max=200, message='Fat should be between 20-200g')
    ])

    # Cuisine preferences
    preferred_cuisines = SelectMultipleField('Preferred Cuisines', choices=[
        ('american', 'American'),
        ('italian', 'Italian'),
        ('mexican', 'Mexican'),
        ('chinese', 'Chinese'),
        ('japanese', 'Japanese'),
        ('indian', 'Indian'),
        ('thai', 'Thai'),
        ('mediterranean', 'Mediterranean'),
        ('french', 'French'),
        ('korean', 'Korean'),
        ('vietnamese', 'Vietnamese'),
        ('middle_eastern', 'Middle Eastern'),
        ('greek', 'Greek'),
        ('spanish', 'Spanish'),
    ])

    # Planning preferences
    meals_per_day = SelectField('Meals Per Day', choices=[
        ('2', '2 meals'),
        ('3', '3 meals'),
        ('4', '3 meals + snack'),
        ('5', '3 meals + 2 snacks'),
    ], default='3')

    cooking_skill = SelectField('Cooking Skill Level', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='intermediate')

    prep_time_preference = SelectField('Preferred Prep Time', choices=[
        ('quick', 'Quick (under 30 min)'),
        ('moderate', 'Moderate (30-60 min)'),
        ('elaborate', 'Elaborate (60+ min)'),
    ], default='moderate')

    budget = SelectField('Budget Level', choices=[
        ('budget', 'Budget-Friendly'),
        ('moderate', 'Moderate'),
        ('premium', 'Premium Ingredients'),
    ], default='moderate')

    submit = SubmitField('Save Preferences')


class GenerateMealPlanForm(FlaskForm):
    """Form for generating a new meal plan."""
    additional_notes = TextAreaField('Additional Notes for This Week', validators=[Optional()])
    submit = SubmitField('Generate Meal Plan')
