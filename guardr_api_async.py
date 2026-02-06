#!/usr/bin/env python3
"""
Guardr API Server with Async Job Processing
Provides REST API endpoints with background job processing for long-running OSINT operations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json
import uuid
import threading
from datetime import datetime, timedelta

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

# In-memory job store (for simplicity - in production use Redis)
jobs = {}
jobs_lock = threading.Lock()

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


def run_osint_analysis(job_id, name, location, username, email):
    """Background worker function to perform OSINT analysis"""
    try:
        logger.info(f"[Job {job_id}] Starting OSINT analysis for: {name}")

        # Update job status
        with jobs_lock:
            jobs[job_id]['status'] = 'processing'
            jobs[job_id]['updated_at'] = datetime.utcnow().isoformat()

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
            logger.info(f"[Job {job_id}] Running person lookup for: {name}")
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
                logger.error(f"[Job {job_id}] Person lookup failed: {e}")
                result['person_verification'] = f"Person lookup error: {str(e)}"

        # Username search using Kallisto
        if username:
            logger.info(f"[Job {job_id}] Running username search for: {username}")
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
                logger.error(f"[Job {job_id}] Username search failed: {e}")
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

        # Update job with results
        with jobs_lock:
            jobs[job_id]['status'] = 'completed'
            jobs[job_id]['result'] = result
            jobs[job_id]['updated_at'] = datetime.utcnow().isoformat()
            jobs[job_id]['completed_at'] = datetime.utcnow().isoformat()

        logger.info(f"[Job {job_id}] Analysis completed - risk level: {result['risk_level']}")

    except Exception as e:
        logger.error(f"[Job {job_id}] Analysis failed with error: {e}", exc_info=True)
        with jobs_lock:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['error'] = str(e)
            jobs[job_id]['updated_at'] = datetime.utcnow().isoformat()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Guardr API (Async)',
        'version': '1.0.0'
    })


@app.route('/api/check-async', methods=['POST'])
def check_profile_async():
    """
    Submit an async OSINT check job

    Returns immediately with a job_id that can be polled for results
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

        # Create job
        job_id = str(uuid.uuid4())
        job = {
            'id': job_id,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'input': {
                'email': email if email else None,
                'name': name if name else None,
                'location': location if location else None,
                'username': username if username else None
            },
            'result': None,
            'error': None
        }

        with jobs_lock:
            jobs[job_id] = job

        # Start background thread
        thread = threading.Thread(
            target=run_osint_analysis,
            args=(job_id, name, location, username, email)
        )
        thread.daemon = True
        thread.start()

        logger.info(f"[Job {job_id}] Created async job for: {name or username or email}")

        return jsonify({
            'job_id': job_id,
            'status': 'pending',
            'message': 'OSINT analysis started. Poll /api/job/{job_id} for results.',
            'estimated_time': '2-5 minutes'
        }), 202

    except Exception as e:
        logger.error(f"Job creation error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/job/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """
    Get job status and results

    Returns:
    - pending: Job is queued
    - processing: Job is running
    - completed: Job finished successfully (includes result)
    - failed: Job encountered an error
    """
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    response = {
        'job_id': job['id'],
        'status': job['status'],
        'created_at': job['created_at'],
        'updated_at': job['updated_at']
    }

    if job['status'] == 'completed':
        response['result'] = job['result']
        response['completed_at'] = job.get('completed_at')
    elif job['status'] == 'failed':
        response['error'] = job.get('error')

    return jsonify(response)


@app.route('/api/check', methods=['POST'])
def check_profile_sync():
    """
    Legacy synchronous endpoint (not recommended for production)

    Use /api/check-async instead for better user experience
    """
    return jsonify({
        'error': 'This endpoint takes 2-5 minutes. Use /api/check-async instead.',
        'message': 'Please use the async endpoint: POST /api/check-async, then poll GET /api/job/{job_id}',
        'async_endpoint': '/api/check-async'
    }), 400


if __name__ == '__main__':
    logger.info("Starting Guardr API Server (Async Mode)...")
    logger.info("Endpoints:")
    logger.info("  GET  /api/health         - Health check")
    logger.info("  POST /api/check-async    - Submit async OSINT job")
    logger.info("  GET  /api/job/<job_id>   - Poll job status and results")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
