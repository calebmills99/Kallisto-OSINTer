#!/usr/bin/env python3
"""
Guardr API Server - Flask wrapper around Kallisto-OSINTer
Provides REST API endpoints for dating safety checks
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add Kallisto to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.modules.person_lookup import lookup_person
from src.modules.username_search import search_username
from src.config import load_config
from src.utils.logger import get_logger
import random

logger = get_logger(__name__)

app = Flask(__name__)
CORS(app)  # Allow requests from frontend
config = load_config()

# Safety tips for captive audience during loading
SAFETY_TIPS = {
    'smart_habits': [
        "Smart daters verify profiles before meeting",
        "A quick check now can save hours of wasted time",
        "Background verification is becoming standard practice",
        "Smart Habit: Always google someone before meeting",
        "Smart Habit: Ask specific questions about their neighborhood",
        "Smart Habit: Request a video call before meeting in person"
    ],
    'friendly_reminders': [
        "Remember to share your date plans with a friend",
        "Video chat is a great way to verify identity",
        "Trust takes time - there's no rush",
        "Friendly Reminder: Meet in a public place for first dates",
        "Friendly Reminder: Inconsistent details can be a yellow flag",
        "Friendly Reminder: Your safety is more important than being polite"
    ],
    'did_you_know': [
        "Did you know? 73% of dating app users have encountered a fake profile",
        "Did you know? Most catfish use photos stolen from Instagram",
        "Did you know? Video verification reduces catfish encounters by 85%",
        "Did you know? Authentic profiles usually have 3+ social platforms",
        "Did you know? 69% of LGBTQ+ individuals experience harassment in online dating",
        "Did you know? Reverse image search can reveal if profile photos are stolen"
    ],
    'you_decide': [
        "You're in control - we just provide the information",
        "Knowledge is power - make informed choices",
        "You are an adult. You decide.",
        "This is information, not judgment",
        "Trust your instincts - if something feels off, it probably is",
        "No one can make this decision for you - we're here to help you decide"
    ]
}

def get_random_safety_tips(count=5):
    """Get random safety tips from different categories"""
    tips = []
    categories = list(SAFETY_TIPS.keys())

    for _ in range(count):
        category = random.choice(categories)
        tip = random.choice(SAFETY_TIPS[category])
        tips.append({
            'category': category.replace('_', ' ').title(),
            'message': tip
        })

    return tips


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Guardr API',
        'version': '1.0.0'
    })


@app.route('/api/check', methods=['POST'])
def check_profile():
    """
    Main endpoint for profile safety checks

    Request body:
    {
        "email": "optional@example.com",
        "name": "Optional Full Name",
        "location": "Optional City, State",
        "username": "optional_username"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email', '').strip()
        name = data.get('name', '').strip()
        location = data.get('location', '').strip()
        username = data.get('username', '').strip()

        if not any([email, name, username]):
            return jsonify({'error': 'Provide at least one of: email, name, or username'}), 400

        logger.info(f"Profile check requested - email: {email}, name: {name}, location: {location}, username: {username}")

        # Initialize result
        result = {
            'email': email if email else None,
            'name': name if name else None,
            'location': location if location else None,
            'username': username if username else None,
            'risk_level': 'UNKNOWN',
            'risk_score': 0,
            'person_verification': None,
            'username_verification': None,
            'breach_data': None,
            'red_flags': [],
            'recommendations': [],
            'safety_tips': get_random_safety_tips(5)
        }

        # Person lookup using Kallisto
        if name:
            logger.info(f"Running person lookup for: {name}")
            try:
                question = """
                Verify this person's identity and provide a dating safety assessment.

                Check for:
                1. Profile authenticity indicators
                2. Potential catfish red flags
                3. Inconsistent information
                4. Social media presence verification
                5. Any safety concerns for dating

                Provide a clear risk assessment (LOW/MEDIUM/HIGH) and specific findings.
                """
                person_report = lookup_person(name, question, config, location=location)
                result['person_verification'] = person_report

                # Parse risk level from report (simple heuristic)
                report_lower = person_report.lower()
                if any(flag in report_lower for flag in ['high risk', 'dangerous', 'fraud', 'scam', 'fake']):
                    result['risk_level'] = 'HIGH'
                    result['risk_score'] = 85
                elif any(flag in report_lower for flag in ['medium risk', 'suspicious', 'inconsistent', 'verify']):
                    result['risk_level'] = 'MEDIUM'
                    result['risk_score'] = 55
                else:
                    result['risk_level'] = 'LOW'
                    result['risk_score'] = 25

            except Exception as e:
                logger.error(f"Person lookup failed: {e}")
                result['person_verification'] = f"Person lookup error: {str(e)}"

        # Username search using Kallisto
        if username:
            logger.info(f"Running username search for: {username}")
            try:
                # Common dating/social platforms
                platforms = [
                    'https://instagram.com',
                    'https://twitter.com',
                    'https://facebook.com',
                    'https://tinder.com',
                    'https://linkedin.com'
                ]
                username_results = search_username(username, platforms, config)
                result['username_verification'] = username_results

                # Count found profiles
                found_count = sum(1 for r in username_results if r.get('status') == 'found')
                if found_count == 0:
                    result['red_flags'].append(f"Username '{username}' not found on any major platforms")
                elif found_count >= 3:
                    result['recommendations'].append("Profile appears on multiple platforms (good sign)")

            except Exception as e:
                logger.error(f"Username search failed: {e}")
                result['username_verification'] = f"Username search error: {str(e)}"

        # Add general recommendations
        if result['risk_level'] == 'HIGH':
            result['recommendations'].extend([
                "⚠️ Do NOT meet this person alone",
                "Consider video chat verification before meeting",
                "Trust your instincts - if something feels off, it probably is"
            ])
        elif result['risk_level'] == 'MEDIUM':
            result['recommendations'].extend([
                "Request additional verification (video chat, ID)",
                "Meet in a public place",
                "Tell a friend where you're going"
            ])
        else:
            result['recommendations'].extend([
                "Still meet in a public place for first date",
                "Share your location with a trusted friend",
                "Trust your instincts"
            ])

        logger.info(f"Check completed - risk level: {result['risk_level']}")
        return jsonify(result)

    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/breach-check', methods=['POST'])
def breach_check():
    """
    Email breach check endpoint (placeholder for future HIBP integration)

    Request body:
    {
        "email": "user@example.com"
    }
    """
    try:
        data = request.json
        email = data.get('email', '').strip()

        if not email:
            return jsonify({'error': 'Email required'}), 400

        # Placeholder - integrate with HIBP or other breach APIs
        result = {
            'email': email,
            'breach_count': 0,
            'breaches': [],
            'risk_level': 'LOW',
            'note': 'Breach checking not yet implemented - will integrate HIBP API'
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Breach check error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("Starting Guardr API Server...")
    logger.info("Endpoints:")
    logger.info("  GET  /api/health       - Health check")
    logger.info("  POST /api/check        - Full profile check (name, location, username)")
    logger.info("  POST /api/breach-check - Email breach check")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
