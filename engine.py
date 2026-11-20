"""ClearLogic Engine Phase I. Experimental, deterministic, in-memory orchestration."""
import re
from classifier import classify_state
from interventions import INTERVENTIONS
from safety import assess_safety, safety_response

GREETING = 'Describe a situation you would like help working through. You may skip distress ratings or end the session at any time.'

def initialize_session():
    return dict(phase='situation', situation=None, emotion=None, initial_distress=None,
                current_distress=None, thought=None, reframe=None, final_distress=None,
                current_state=None, safety={'status':'none','category':None}, skill=None)

def reset_session(session_state):
    session_state.clear()
    session_state.update(initialize_session())

def extract_distress_rating(text):
    m = re.fullmatch(r'\s*(10|[0-9])\s*(?:/\s*10)?\s*', text)
    return int(m.group(1)) if m else None

def get_phase(session_state):
    return {'situation':1,'emotion':2,'distress':3,'regulation':4,'thought':4,
            'action':5,'final_distress':6,'complete':7}.get(session_state['phase'],1)

def phase_label(session_state):
    return session_state['phase'].replace('_',' ').title()

def get_interventions(pattern_name=None, distress_level=None, intervention_need=None):
    if intervention_need == 'regulation_first' or (distress_level is not None and distress_level >= 7):
        # Non-breath-focused grounding is the default regulation option.
        return [INTERVENTIONS['High Distress'][2]]
    key = {'problem_solving':'Problem Solving','behavioral_structure':'Behavioral Structure'}.get(intervention_need, pattern_name)
    return INTERVENTIONS.get(key, INTERVENTIONS['Problem Solving'])[:1]

def _state(s, text):
    state = classify_state(text, s['current_distress'])
    context = classify_state(s['situation'] or '')['context_constraint']
    if context == 'reported_external_constraint':
        state['context_constraint'] = context
        if state['intervention_need'] != 'regulation_first':
            state['intervention_need'] = 'problem_solving'
    state['safety_flag'] = s['safety']['status']
    s['current_state'] = state
    return state

def _skill(s, state):
    patterns = state['patterns']
    key = patterns[0]['intervention_key'] if patterns else None
    skill = get_interventions(key, s['current_distress'], state['intervention_need'])[0]
    s['skill'] = skill.copy()
    return f"**{skill['name']}** — {skill['desc']}"

def process_turn(user_text, session_state):
    """Return JSON-serializable response metadata; mutate only supplied session."""
    s = session_state
    for k,v in initialize_session().items():
        s.setdefault(k,v)
    text = str(user_text).strip()
    def result(message):
        return dict(message=message, phase=s['phase'], safety=s['safety'].copy(),
                    state=s['current_state'], skill=s['skill'], initial_distress=s['initial_distress'],
                    final_distress=s['final_distress'])
    # Safety always precedes commands, scoring and coaching.
    s['safety'] = assess_safety(text, s['safety'])
    if s['safety']['status'] != 'none':
        if s['current_state'] is not None:
            s['current_state']['safety_flag'] = s['safety']['status']
        s['skill'] = None
        return result(safety_response(s['safety']))
    if not text:
        return result('Enter a response when you are ready.')
    if text.casefold() in {'reset','restart','new session','start new'}:
        reset_session(s)
        return result(GREETING)
    if text.casefold() in {'end session','stop session'}:
        reset_session(s)
        s['phase']='complete'
        return result('Session ended. You can start a new session whenever you choose.')
    phase = s['phase']
    if phase == 'situation':
        s['situation']=text
        _state(s,text)
        s['phase']='emotion'
        return result('What emotion are you experiencing most strongly right now?')
    if phase == 'emotion':
        s['emotion']=text
        _state(s,text)
        s['phase']='distress'
        return result('How distressed are you right now, from 0 (calm) to 10 (extremely distressed)? You may also type skip.')
    if phase in {'distress','regulation','final_distress'}:
        rating=extract_distress_rating(text)
        if rating is None and text.casefold()!='skip':
            return result('Please enter a number from 0 to 10, or type skip.')
        if phase=='final_distress':
            s['final_distress']=rating
            s['phase']='complete'
            initial=s['initial_distress']
            if initial is None or rating is None:
                return result('Session complete. No distress comparison is available because a rating was skipped.')
            return result(f'Session complete. Starting distress: {initial}/10. Ending distress: {rating}/10. Change (ending minus starting): {rating-initial:+d}. This is a self-reported change, not a measure of treatment efficacy.')
        if phase=='distress':
            s['initial_distress']=rating
        s['current_distress']=rating
        state=_state(s, s['emotion'] or '')
        if phase=='distress' and state['intervention_need']=='regulation_first':
            s['phase']='regulation'
            return result(_skill(s,state)+'\n\nIf comfortable, try this skill. Then enter your current distress rating or skip.')
        if phase=='regulation' and rating is not None and rating>=7:
            return result('You can continue grounding, seek support from someone you trust, or end the session. Return a new rating when you are ready, or type skip.')
        s['phase']='thought'
        return result('What thought or practical concern would you like to work on?')
    if phase=='thought':
        s['thought']=text
        state=_state(s,text)
        if state['intervention_need']=='regulation_first':
            s['phase']='regulation'
            return result(_skill(s,state)+'\n\nEnter your current distress rating when ready, or skip.')
        skill=_skill(s,state)
        s['phase']='action'
        if state['intervention_need'] in {'problem_solving','behavioral_structure','exploration'} or not state['patterns']:
            prompt='What is one practical next step you can choose?'
        else:
            prompt='If this skill fits your situation, what interpretation or next action would be useful? You do not need to change your view of what happened.'
        return result(skill+'\n\n'+prompt)
    if phase=='action':
        s['reframe']=text
        s['phase']='final_distress'
        return result('What is your distress level now, from 0 to 10? You may type skip.')
    return result('This session is complete. Type new session to begin again.')

def generate_response(user_text, session_state):
    """Text-only compatibility interface for the future Gradio UI."""
    return process_turn(user_text, session_state)['message']
