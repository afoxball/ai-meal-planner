# AI Meal Planner

A Flask web application that uses Google Gemini AI to create personalized weekly meal plans based on user preferences. Built with Bootstrap, PostgreSQL, and designed for deployment on Render.

## Features

- **User Authentication**: Secure registration and login system
- **Personalized Preferences**: Set dietary restrictions, allergies, favorite foods, and cuisine preferences
- **Goal-Based Planning**: Optimize meals for pleasure, fitness, macro tracking, variety, or budget
- **AI-Powered Generation**: Uses Google Gemini AI to create customized 7-day meal plans
- **Ingredient Optimization**: AI maximizes ingredient reuse across meals to reduce waste and shopping
- **Shopping Lists**: Consolidated shopping lists organized by category
- **Nutritional Information**: Calorie and macro tracking for each meal
- **Recipe Details**: Complete recipes with ingredients and cooking instructions
- **Plan History**: Save and review past meal plans

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: Bootstrap 5 with Bootstrap Icons
- **AI**: Google Gemini 1.5 Flash
- **Deployment**: Render

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (optional for local development)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/afoxball/ai-meal-planner.git
   cd ai-meal-planner
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

5. Run the application:
   ```bash
   python run.py
   ```

6. Open http://localhost:5000 in your browser

### Deploy to Render

1. Fork or push this repository to your GitHub account

2. Go to [Render Dashboard](https://dashboard.render.com/)

3. Click "New" → "Blueprint"

4. Connect your GitHub repository

5. Render will automatically detect the `render.yaml` and create:
   - A PostgreSQL database
   - A web service running your Flask app

6. After deployment, add your Gemini API key:
   - Go to your web service in Render
   - Navigate to "Environment"
   - Add `GEMINI_API_KEY` with your API key

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key for sessions | Yes (auto-generated on Render) |
| `DATABASE_URL` | PostgreSQL connection string | Yes (auto-configured on Render) |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |

## Usage

1. **Register**: Create an account to start using the app
2. **Set Preferences**: Fill out your food preferences, dietary restrictions, and goals
3. **Generate Plan**: Click "Generate Meal Plan" to create a personalized weekly menu
4. **View & Shop**: Browse your meals by day and use the shopping list feature
5. **History**: Access past meal plans anytime from your dashboard

## Project Structure

```
ai-meal-planner/
├── app/
│   ├── __init__.py      # Flask app factory
│   ├── models.py        # Database models
│   ├── forms.py         # WTForms forms
│   ├── routes.py        # Main routes
│   ├── auth.py          # Authentication routes
│   ├── meals.py         # Meal planning routes & AI integration
│   └── templates/       # Jinja2 templates
├── tests/               # Test files
├── config.py            # Configuration
├── run.py               # Application entry point
├── render.yaml          # Render deployment config
├── requirements.txt     # Python dependencies
└── README.md
```

## License

MIT License