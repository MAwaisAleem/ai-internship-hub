"""Assessment service for skill evaluation and domain recommendation."""
from bson import ObjectId

from app.extensions import mongo

# Domains aligned with DigiSkills courses
DOMAINS = [
    'Graphic Design',
    'Content Writing',
    'Programming',
    'Freelancing',
    'E-Commerce',
    'QuickBooks',
    'AutoCAD',
]


def get_questions() -> list:
    """Get all assessment questions for the MCQ test."""
    questions = list(mongo.db.assessment_questions.find({}))
    for q in questions:
        q['id'] = str(q['_id'])
        del q['_id']
        del q['correct_answer']  # Don't send correct answer to frontend
    return questions


def submit_assessment(user_id, answers):
    """
    Submit assessment answers, calculate scores, determine recommended domain.
    answers: list of { question_id: str, selected_option: int }
    """
    questions = {str(q['_id']): q for q in mongo.db.assessment_questions.find({})}

    scores_by_domain = {d: {'correct': 0, 'total': 0} for d in DOMAINS}
    total_correct = 0
    total_questions = 0

    for ans in answers:
        qid = ans.get('question_id')
        selected = ans.get('selected_option')
        if qid not in questions:
            continue
        q = questions[qid]
        domain = q.get('domain', 'Other')
        if domain not in scores_by_domain:
            scores_by_domain[domain] = {'correct': 0, 'total': 0}

        scores_by_domain[domain]['total'] += 1
        total_questions += 1
        if selected == q.get('correct_answer'):
            scores_by_domain[domain]['correct'] += 1
            total_correct += 1

    # Compute percentage per domain and overall
    domain_scores = []
    for domain, data in scores_by_domain.items():
        if data['total'] > 0:
            pct = round(100 * data['correct'] / data['total'])
            domain_scores.append({
                'domain': domain,
                'score': pct,
                'correct': data['correct'],
                'total': data['total'],
            })

    # Sort by score descending; recommend top domain(s)
    domain_scores.sort(key=lambda x: x['score'], reverse=True)
    recommended_domain = domain_scores[0]['domain'] if domain_scores else 'Freelancing'
    # Include top 3 as recommendations
    recommended_domains = [d['domain'] for d in domain_scores[:3]] if domain_scores else ['Freelancing']

    overall_score = round(100 * total_correct / total_questions) if total_questions else 0

    # Store result
    try:
        uid = ObjectId(user_id)
    except Exception:
        raise ValueError('Invalid user ID')

    assessment_doc = {
        'user_id': uid,
        'answers': answers,
        'scores_by_domain': {d['domain']: d['score'] for d in domain_scores},
        'domain_scores': domain_scores,
        'overall_score': overall_score,
        'recommended_domain': recommended_domain,
        'recommended_domains': recommended_domains,
        'total_correct': total_correct,
        'total_questions': total_questions,
    }
    mongo.db.assessments.insert_one(assessment_doc)

    return {
        'scores_by_domain': domain_scores,
        'overall_score': overall_score,
        'recommended_domain': recommended_domain,
        'recommended_domains': recommended_domains,
        'total_correct': total_correct,
        'total_questions': total_questions,
    }


def get_latest_result(user_id: str) -> dict | None:
    """Get the latest assessment result for a user."""
    doc = mongo.db.assessments.find_one(
        {'user_id': ObjectId(user_id)},
        sort=[('_id', -1)]
    )
    if not doc:
        return None
    doc.pop('_id')
    doc.pop('user_id')
    doc.pop('answers')
    return doc
