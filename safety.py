"""ClearLogic Phase I: experimental safety routing, not a clinical risk assessment."""
import re

RULES = {
    'imminent_risk': {
        'self_harm': r'\b(?:i (?:am going to|will|plan to|am about to) (?:kill myself|end my life|hurt myself)|i (?:have taken|just took) an overdose)\b',
        'harm_to_others': r'\bi (?:am going to|will|plan to|am about to) (?:kill|shoot|stab|hurt) (?:him|her|them|someone|another person)\b',
        'external_danger': r'\b(?:someone is attacking me|he is attacking me|she is attacking me|someone is trying to kill me|he has a gun pointed at me)\b',
        'medical': r"\b(?:i can(?:not|'t) breathe|i am having a heart attack|i am bleeding heavily)\b",
    },
    'passive_ideation': {'self_harm': r"\b(?:i (?:wish i (?:was|were) dead|want to die)|(?:i am|i'm) better off dead|no reason to live)\b"},
    'needs_clarification': {
        'self_harm': r"\b(?:suicid(?:e|al)|kill myself|hurt myself|end my life|end it all|overdose|self[- ]harm|can(?:not|'t) go on anymore|give up on life)\b",
        'harm_to_others': r'\b(?:hurt someone|kill someone|want to hurt (?:him|her|them))\b',
        'external_danger': r"\b(?:threatened to kill me|threatening me|not safe|in danger|afraid for my life)\b",
    },
}

def assess_safety(text, previous=None):
    """Return a routing signal. Unresolved alerts remain active across turns."""
    normalized = str(text).lower().replace('’', "'")
    normalized = re.sub(r"\bi'm\b", 'i am', normalized)
    for status, categories in RULES.items():
        for category, pattern in categories.items():
            if re.search(pattern, normalized):
                result = {'status': status, 'category': category}
                if previous and previous.get('status') == 'imminent_risk':
                    return previous.copy()
                return result
    if previous and previous.get('status') in RULES:
        return previous.copy()
    return {'status': 'none', 'category': None}

def check_safety(text):
    """Compatibility with the original Boolean interface."""
    return assess_safety(text)['status'] != 'none'

def safety_response(result):
    status, category = result['status'], result['category']
    if status == 'none':
        return None
    if status == 'imminent_risk':
        return ('Your immediate safety takes priority. If you or someone else may be in immediate danger, contact local emergency services now (911 in the US). If possible and safe, reach a trusted person who can help. ClearLogic cannot contact emergency services for you.')
    if category == 'self_harm':
        return ('I want to understand whether this is an immediate safety concern. Are you thinking about harming yourself right now, or describing something else? If you may act on these thoughts or cannot stay safe, contact emergency services. In the US, you can also call or text 988 for crisis support.')
    if category == 'harm_to_others':
        return ('Are you concerned that you might hurt someone right now? If anyone is in immediate danger, contact local emergency services.')
    return ('Are you in immediate physical danger right now? If so, contact local emergency services when it is safe to do so.')
