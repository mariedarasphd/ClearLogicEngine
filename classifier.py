"""ClearLogic Phase I: experimental, non-diagnostic rule classifier.
Candidate signals are not clinical findings or verified facts.
Safety screening is a separate module and must run before this classifier.
"""
import re

COGNITIVE_DISTORTIONS = {'Catastrophizing': {'keywords': ['doomed',
                                  'never recover',
                                  'everything will',
                                  'things will get worse',
                                  'something bad will happen',
                                  'everything is ruined',
                                  'my life is over',
                                  'i will never recover'],
                     'explanation': 'Predicting a highly negative outcome or treating a feared '
                                    'possibility as though it is likely.',
                     'reframe_prompt': 'What is known, what is possible, and what is actually '
                                       'probable?',
                     'intervention_key': 'Catastrophizing'},
 'Mindreading': {'keywords': ['they think',
                              "they'll think",
                              'they will think',
                              "they don't like me",
                              "they won't like me",
                              "they won't want",
                              "they don't want",
                              "people won't",
                              'people will think',
                              "they're going to say",
                              'no one understands',
                              "they don't understand",
                              "they'll say",
                              "they're judging",
                              'people might not like'],
                 'explanation': 'Inferring what another person thinks, feels, or intends without '
                                'sufficient evidence.',
                 'reframe_prompt': 'What do you actually know about what the other person thinks, '
                                   'and what are you predicting?',
                 'intervention_key': 'Mindreading'},
 'Emotional Reasoning': {'keywords': ['because I feel',
                                      'I feel worthless',
                                      'I feel useless',
                                      'I feel inadequate'],
                         'explanation': 'Using the intensity of a feeling as evidence that a '
                                        'conclusion must be true.',
                         'reframe_prompt': 'What is the feeling telling you about your experience, '
                                           'and what evidence establishes the facts?',
                         'intervention_key': 'Emotional Reasoning'},
 'Global Labeling': {'keywords': ['worthless',
                                  'useless',
                                  'loser',
                                  'idiot',
                                  'stupid',
                                  'disappointment',
                                  'inadequate',
                                  'bad person',
                                  'terrible person',
                                  'i am worthless',
                                  "i'm worthless",
                                  'i am a failure',
                                  "i'm a failure",
                                  'i am useless'],
                     'explanation': 'Turning a specific difficulty, behavior, or event into a '
                                    'broad judgment about a person.',
                     'reframe_prompt': 'Can you describe the specific behavior or situation '
                                       'without turning it into a judgment about the whole person?',
                     'intervention_key': 'Global Labeling'},
 'Shoulds': {'keywords': ["shouldn't",
                          'i should never make mistakes',
                          'i must be perfect',
                          'i should always be able to'],
             'explanation': 'Using rigid rules about what you or another person must do.',
             'reframe_prompt': 'Is this an absolute requirement, or is it a preference, goal, or '
                               'expectation?',
             'intervention_key': 'Shoulds'},
 'Polarized Thinking': {'keywords': ['all or nothing',
                                     'if it is not perfect',
                                     "if it isn't perfect",
                                     'either perfect or a failure'],
                        'explanation': 'Evaluating a situation in extremes while overlooking '
                                       'intermediate possibilities.',
                        'reframe_prompt': 'Where is the middle ground between the two extremes?',
                        'intervention_key': 'Polarized Thinking'},
 'Overgeneralization': {'keywords': ['every time',
                                     'nothing ever',
                                     'all the time',
                                     'again and again',
                                     'i always fail',
                                     'i never do anything right',
                                     'nothing ever works',
                                     'everyone hates me'],
                        'explanation': 'Extending a particular experience into a broad rule about '
                                       'what always happens.',
                        'reframe_prompt': 'Is this literally always true, or can you identify an '
                                          'exception?',
                        'intervention_key': 'Overgeneralization'},
 'Jumping to Conclusions': {'keywords': ['must be',
                                         "there's no point",
                                         "won't work",
                                         "can't work",
                                         'no one will',
                                         'nobody will',
                                         'nothing will'],
                            'explanation': 'Arriving at a conclusion before enough evidence is '
                                           'available.',
                            'reframe_prompt': 'What evidence supports the conclusion, and what '
                                              'information is still unknown?',
                            'intervention_key': 'Jumping to Conclusions'},
 'Personalization': {'keywords': ['because of me',
                                  'I made them',
                                  'depends on me',
                                  'all my fault',
                                  'I did this to them',
                                  'everything is my fault',
                                  'it is all my fault'],
                     'explanation': 'Assigning yourself responsibility for outcomes involving '
                                    'multiple factors or factors outside your control.',
                     'reframe_prompt': 'What factors were outside your control, and what portion '
                                       'actually belongs to you?',
                     'intervention_key': 'Personalization'},
 'Control Fallacies': {'keywords': ['I have to',
                                    "I can't help",
                                    'make them',
                                    'control them',
                                    'responsible for their',
                                    "not safe if I don't",
                                    'have to buy',
                                    'have to do'],
                       'explanation': 'Confusing what you can control with what you cannot '
                                      'control.',
                       'reframe_prompt': 'What is actually within your control right now?',
                       'intervention_key': 'Control Fallacies'},
 'Fallacy of Fairness': {'keywords': ["shouldn't happen", 'not fair', "that's wrong"],
                         'explanation': 'Treating fairness as a necessary condition for how events '
                                        'should unfold.',
                         'reframe_prompt': 'What is happening regardless of whether it feels fair, '
                                           'and what response is most useful now?',
                         'intervention_key': 'Fallacy of Fairness'},
 'Blaming': {'keywords': ['your fault', 'you made me'],
             'explanation': 'Reducing a complex situation to a single source of blame.',
             'reframe_prompt': 'What different factors contributed to this situation?',
             'intervention_key': 'Blaming'},
 'Fallacy of Change': {'keywords': ['if they would',
                                    'if only they',
                                    'make them change',
                                    'change them',
                                    'force them',
                                    'convince them',
                                    'if they changed'],
                       'explanation': "Focusing on changing another person's behavior as though "
                                      'their change is within your control.',
                       'reframe_prompt': 'What can you control about your own response, boundary, '
                                         'or next step?',
                       'intervention_key': 'Fallacy of Change'}}


def normalize(text):
    return " ".join(text.casefold().replace("’", "'").split())


def matches(text, phrase):
    return bool(re.search(r"(?<!\w)" + re.escape(normalize(phrase)) + r"(?!\w)", normalize(text)))


def any_match(text, phrases):
    return any(matches(text, p) for p in phrases)


def detect_patterns(text):
    results = []
    for name, data in COGNITIVE_DISTORTIONS.items():
        hits = [k for k in data['keywords'] if matches(text, k)]
        if hits:
            results.append(dict(name=name, score=len(hits), matched_keywords=hits,
                explanation=data['explanation'], reframe_prompt=data['reframe_prompt'],
                intervention_key=data['intervention_key']))
    return sorted(results, key=lambda p: -p['score'])


def detect_best_pattern(text):
    patterns = detect_patterns(text)
    return patterns[0] if patterns else None


def assess_context(text):
    # Reported constraints, not independently verified events.
    if any_match(text, ['lost my job', 'laid off', 'no income', "can't pay", 'rent is due',
        'eviction', 'evicted', 'assaulted', 'abused', 'threatened', 'stalking', 'homeless',
        'lost my housing', 'medical bills', 'food insecurity', 'being followed']):
        return 'reported_external_constraint'
    return 'undetermined'


def classify_state(text, distress=None):
    patterns = detect_patterns(text)
    context = assess_context(text)
    emotion = 'unspecified'
    for label, signals in [
        ('high_activation', ['panic','panicking','overwhelmed','terrified','freaking out']),
        ('agitation', ['angry','furious','irritated']),
        ('low_mood', ['sad','hopeless','empty','worthless']),
        ('anxiety', ['worried','anxious','nervous','concerned','afraid','scared'])]:
        if any_match(text, signals):
            emotion = label
            break
    top = patterns[0]['name'] if patterns else None
    modes = {'Catastrophizing':'threat_prediction','Mindreading':'social_prediction',
        'Global Labeling':'self_evaluation','Personalization':'self_evaluation',
        'Shoulds':'self_evaluation','Overgeneralization':'rigid_interpretation',
        'Polarized Thinking':'rigid_interpretation'}
    mode = modes.get(top, 'neutral')
    if emotion == 'high_activation' or (distress is not None and distress >= 7):
        need = 'regulation_first'
    elif context == 'reported_external_constraint':
        need = 'problem_solving'
    elif any_match(text, ["can't concentrate", "can't get started", 'cannot concentrate', 'putting it off']):
        need = 'behavioral_structure'
    else:
        need = {'Catastrophizing':'probability_reframe','Mindreading':'reality_check',
            'Shoulds':'flexibility_reframe','Overgeneralization':'specificity'}.get(top,
            'pattern_exploration' if top else 'exploration')
    return dict(emotion_state=emotion, cognitive_mode=mode, patterns=patterns,
        context_constraint=context, intervention_need=need, safety_flag='not_assessed')
