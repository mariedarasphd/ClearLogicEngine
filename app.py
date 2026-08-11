import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import random

# ============================================================
# CLEARLOGIC ENGINE
# Phase 1: Deterministic, state-based cognitive support agent
# ============================================================

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------

st.set_page_config(
    page_title="ClearLogic Engine",
    page_icon="🧠",
    layout="wide"
)

# ------------------------------------------------------------
# STYLING
# ------------------------------------------------------------

st.markdown("""
<style>

    /* ---------- APP ---------- */

    .stApp {
        background-color: #0a192f;
        color: #ffffff !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    p, span, div, li, label {
        color: #ffffff;
    }

    /* ---------- CHAT ---------- */

    .stChatMessage {
        background-color: #112240 !important;
        color: #ffffff !important;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }

    .stChatMessage p,
    .stChatMessage span,
    .stChatMessage div {
        color: #ffffff !important;
    }

    /* ---------- CHAT INPUT FIX ---------- */

    /* Main chat input container */
    [data-testid="stChatInput"] {
        background-color: #112240 !important;
        border: 2px solid #64ffda !important;
        border-radius: 12px !important;
    }

    /* Actual typing area */
    [data-testid="stChatInput"] textarea {
        background-color: #112240 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #64ffda !important;
        font-size: 16px !important;
    }

    /* Placeholder */
    [data-testid="stChatInput"] textarea::placeholder {
        color: #b8c7d9 !important;
        opacity: 1 !important;
    }

    /* Input focus */
    [data-testid="stChatInput"] textarea:focus {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border-color: #64ffda !important;
        box-shadow: 0 0 0 1px #64ffda !important;
    }

    /* ---------- BUTTONS ---------- */

    .stButton > button {
        background-color: #64ffda !important;
        color: #0a192f !important;
        font-weight: bold;
        font-size: 15px;
        border-radius: 8px;
        border: none;
    }

    .stButton > button:hover {
        background-color: #4cc9ac !important;
        color: #0a192f !important;
    }

    /* ---------- CARDS ---------- */

    .intervention-card {
        background-color: #112240;
        border: 2px solid #64ffda;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 5px solid #64ffda;
    }

    .grounding-card {
        background-color: #1d3557;
        border: 2px solid #ffd93d;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 5px solid #ffd93d;
    }

    .info-box {
        background-color: #1d3557;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #64ffda;
        margin: 10px 0;
    }

    .progress-box {
        background-color: #112240;
        border: 1px solid #355070;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
    }

    .state-box {
        background-color: #112240;
        border: 1px solid #355070;
        padding: 10px;
        border-radius: 8px;
        margin-top: 10px;
    }

    .small-label {
        color: #9fb3c8 !important;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# LOGO
# ------------------------------------------------------------

LOGO_PATH = "logo.png"

if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=200)
else:
    st.warning("⚠️ Logo 'logo.png' not found.")


# ============================================================
# INTERVENTION LIBRARY
# ============================================================

INTERVENTIONS = {

    "High Distress": [
        {
            "name": "🫁 Box Breathing",
            "desc": "Inhale for 4 seconds, hold for 4, exhale for 4, hold for 4. Repeat 3 times.",
            "type": "physiological"
        },
        {
            "name": "🌬️ Physiological Sigh",
            "desc": "Take two short inhales through the nose followed by one long exhale through the mouth. Repeat 3 times.",
            "type": "physiological"
        },
        {
            "name": "🌍 5-4-3-2-1 Grounding",
            "desc": "Name 5 things you see, 4 you feel, 3 you hear, 2 you smell, and 1 you taste.",
            "type": "grounding"
        }
    ],

    "Catastrophizing": [
        {
            "name": "📉 Probability Reframe",
            "desc": "Separate what is possible from what is probable. What evidence tells you this outcome is likely?",
            "type": "cognitive"
        },
        {
            "name": "🧭 Containment",
            "desc": "Identify the part of the problem that requires attention right now. Set the rest aside temporarily.",
            "type": "cognitive"
        }
    ],

    "Mindreading": [
        {
            "name": "🔍 Evidence Check",
            "desc": "Separate what you know from what you are predicting another person thinks or feels.",
            "type": "cognitive"
        },
        {
            "name": "🔄 Alternative Explanation",
            "desc": "Generate two or three explanations that do not depend on knowing what the other person is thinking.",
            "type": "cognitive"
        }
    ],

    "Emotional Reasoning": [
        {
            "name": "🧠 Feeling vs. Fact",
            "desc": "Write down the feeling as true information about your experience, then separately identify what the evidence establishes as fact.",
            "type": "cognitive"
        },
        {
            "name": "🔎 Reality Check",
            "desc": "What objective evidence supports the conclusion? What evidence leaves room for another interpretation?",
            "type": "cognitive"
        }
    ],

    "Global Labeling": [
        {
            "name": "🏷️ Replace the Label",
            "desc": "Describe the specific behavior or event instead of applying a global label to yourself or someone else.",
            "type": "linguistic"
        },
        {
            "name": "🌐 Whole-Picture Check",
            "desc": "Identify information that does not fit the global label.",
            "type": "cognitive"
        }
    ],

    "Shoulds": [
        {
            "name": "💭 The Prefer Swap",
            "desc": "Replace 'I should' with 'I would prefer,' 'I want,' or 'It would be helpful if.'",
            "type": "linguistic"
        },
        {
            "name": "🧱 Examine the Rule",
            "desc": "Ask who created this rule and whether it is flexible enough to fit the actual situation.",
            "type": "cognitive"
        }
    ],

    "Polarized Thinking": [
        {
            "name": "📊 Continuum Scale",
            "desc": "Instead of all-or-nothing, rate the situation from 0-100. Where does it actually fall?",
            "type": "cognitive"
        },
        {
            "name": "🌈 Find the Middle",
            "desc": "Identify one interpretation between the two extremes.",
            "type": "cognitive"
        }
    ],

    "Overgeneralization": [
        {
            "name": "🔍 Exception Hunt",
            "desc": "Find one example where the 'always,' 'never,' or 'everyone' statement was not completely true.",
            "type": "cognitive"
        },
        {
            "name": "🗣️ Sometimes Swap",
            "desc": "Replace absolute language with more precise language such as 'sometimes,' 'this time,' or 'in this situation.'",
            "type": "linguistic"
        }
    ],

    "Jumping to Conclusions": [
        {
            "name": "⚖️ Evidence Test",
            "desc": "What evidence do you actually have? What part is interpretation or prediction?",
            "type": "cognitive"
        },
        {
            "name": "🕵️ Three Alternatives",
            "desc": "List three possible explanations for what happened before deciding which explanation is most likely.",
            "type": "cognitive"
        }
    ],

    "Personalization": [
        {
            "name": "🥧 Responsibility Pie",
            "desc": "List all factors contributing to the situation. Estimate how much influence each factor actually had.",
            "type": "cognitive"
        },
        {
            "name": "🛡️ Control Boundary",
            "desc": "Separate what belongs to you from what belongs to other people or circumstances.",
            "type": "cognitive"
        }
    ],

    "Control Fallacies": [
        {
            "name": "⭕ Circle of Control",
            "desc": "Separate what you control, what you influence, and what you cannot control.",
            "type": "cognitive"
        },
        {
            "name": "🤝 Influence vs. Control",
            "desc": "Identify one response that is within your control right now.",
            "type": "behavioral"
        }
    ],

    "Fallacy of Fairness": [
        {
            "name": "⚖️ Reality Check",
            "desc": "Separate what you believe should happen from what is actually happening.",
            "type": "cognitive"
        },
        {
            "name": "🎯 Choice Point",
            "desc": "Given the situation as it exists, what response gives you the most useful next step?",
            "type": "behavioral"
        }
    ],

    "Blaming": [
        {
            "name": "🔄 Responsibility Map",
            "desc": "Identify who controlled which parts of the situation without assigning responsibility for things outside anyone's control.",
            "type": "cognitive"
        },
        {
            "name": "🪞 Contribution Check",
            "desc": "Ask what you contributed, what others contributed, and what was caused by circumstances.",
            "type": "cognitive"
        }
    ],

    "Fallacy of Change": [
        {
            "name": "🚪 Boundary Focus",
            "desc": "Shift attention from forcing another person to change toward deciding what you will do.",
            "type": "behavioral"
        },
        {
            "name": "🌱 Acceptance + Action",
            "desc": "Identify what you cannot change and one action you can take in response.",
            "type": "acceptance"
        }
    ],

    "Behavioral Structure": [
        {
            "name": "⏱️ Five-Minute Start",
            "desc": "Reduce the task to five minutes. The objective is starting, not finishing.",
            "type": "behavioral"
        },
        {
            "name": "🎯 One-Step Rule",
            "desc": "Choose the smallest concrete action that moves the task forward.",
            "type": "behavioral"
        }
    ],

    "Problem Solving": [
        {
            "name": "🧩 Problem Breakdown",
            "desc": "Separate the problem into what is known, what is uncertain, and what requires action.",
            "type": "problem-solving"
        },
        {
            "name": "📋 Next Action",
            "desc": "Identify one concrete action that could improve the situation even slightly.",
            "type": "problem-solving"
        }
    ]
}


# ============================================================
# COGNITIVE PATTERN DEFINITIONS
# ============================================================

COGNITIVE_DISTORTIONS = {

    "Catastrophizing": {
        "keywords": [
            "worst", "disaster", "terrible", "horrible",
            "ruined", "doomed", "hopeless", "forever",
            "never recover", "going to jail", "lose my job",
            "no income", "get fired", "everything will",
            "things will get worse", "something bad will happen",
            "can't pay", "won't be able to pay"
        ],
        "explanation": "Predicting a highly negative outcome or treating a feared possibility as though it is likely.",
        "reframe_prompt": "What is known, what is possible, and what is actually probable?",
        "intervention_key": "Catastrophizing"
    },

    "Mindreading": {
        "keywords": [
            "they think", "they'll think", "they will think",
            "they don't like me", "they won't like me",
            "they won't want", "they don't want",
            "people won't", "people will think",
            "they're going to say", "no one understands",
            "they don't understand", "they'll say",
            "they're judging", "judge me", "people might not like",
            "hope they like me"
        ],
        "explanation": "Inferring what another person thinks, feels, or intends without sufficient evidence.",
        "reframe_prompt": "What do you actually know about what the other person thinks, and what are you predicting?",
        "intervention_key": "Mindreading"
    },

    "Emotional Reasoning": {
        "keywords": [
            "I feel like", "because I feel",
            "feels like", "I feel sick", "I feel worthless",
            "I feel useless", "I feel inadequate",
            "I hate it", "why can't I",
            "it feels", "I just feel"
        ],
        "explanation": "Using the intensity of a feeling as evidence that a conclusion must be true.",
        "reframe_prompt": "What is the feeling telling you about your experience, and what evidence establishes the facts?",
        "intervention_key": "Emotional Reasoning"
    },

    "Global Labeling": {
        "keywords": [
            "worthless", "useless", "loser", "idiot",
            "stupid", "failure", "disappointment",
            "inadequate", "bad person", "terrible person",
            "I'm a", "I am a"
        ],
        "explanation": "Turning a specific difficulty, behavior, or event into a broad judgment about a person.",
        "reframe_prompt": "Can you describe the specific behavior or situation without turning it into a judgment about the whole person?",
        "intervention_key": "Global Labeling"
    },

    "Shoulds": {
        "keywords": [
            "should", "shouldn't", "must",
            "ought", "have to", "need to",
            "supposed to", "got to"
        ],
        "explanation": "Using rigid rules about what you or another person must do.",
        "reframe_prompt": "Is this an absolute requirement, or is it a preference, goal, or expectation?",
        "intervention_key": "Shoulds"
    },

    "Polarized Thinking": {
        "keywords": [
            "all or nothing", "perfect", "failure",
            "completely", "totally", "nothing",
            "everything", "zero", "100%",
            "either", "or"
        ],
        "explanation": "Evaluating a situation in extremes while overlooking intermediate possibilities.",
        "reframe_prompt": "Where is the middle ground between the two extremes?",
        "intervention_key": "Polarized Thinking"
    },

    "Overgeneralization": {
        "keywords": [
            "always", "never", "every time",
            "everyone", "no one", "nobody",
            "nothing ever", "all the time",
            "forever", "again and again"
        ],
        "explanation": "Extending a particular experience into a broad rule about what always happens.",
        "reframe_prompt": "Is this literally always true, or can you identify an exception?",
        "intervention_key": "Overgeneralization"
    },

    "Jumping to Conclusions": {
        "keywords": [
            "definitely", "obviously", "clearly",
            "must be", "I know", "there's no point",
            "won't work", "can't work",
            "no one will", "nobody will",
            "nothing will"
        ],
        "explanation": "Arriving at a conclusion before enough evidence is available.",
        "reframe_prompt": "What evidence supports the conclusion, and what information is still unknown?",
        "intervention_key": "Jumping to Conclusions"
    },

    "Personalization": {
        "keywords": [
            "my fault", "because of me",
            "I caused", "I made them",
            "my responsibility", "depends on me",
            "all my fault", "I did this to them"
        ],
        "explanation": "Assigning yourself responsibility for outcomes involving multiple factors or factors outside your control.",
        "reframe_prompt": "What factors were outside your control, and what portion actually belongs to you?",
        "intervention_key": "Personalization"
    },

    "Control Fallacies": {
        "keywords": [
            "I have to", "I can't help",
            "helpless", "forced", "trapped",
            "make them", "control them",
            "responsible for their",
            "not safe if I don't",
            "have to buy", "have to do"
        ],
        "explanation": "Confusing what you can control with what you cannot control.",
        "reframe_prompt": "What is actually within your control right now?",
        "intervention_key": "Control Fallacies"
    },

    "Fallacy of Fairness": {
        "keywords": [
            "fair", "unfair", "deserve",
            "owed", "supposed to",
            "shouldn't happen", "not fair",
            "that's wrong", "justice"
        ],
        "explanation": "Treating fairness as a necessary condition for how events should unfold.",
        "reframe_prompt": "What is happening regardless of whether it feels fair, and what response is most useful now?",
        "intervention_key": "Fallacy of Fairness"
    },

    "Blaming": {
        "keywords": [
            "your fault", "my fault",
            "blame", "because you",
            "you made me", "they caused",
            "I caused"
        ],
        "explanation": "Reducing a complex situation to a single source of blame.",
        "reframe_prompt": "What different factors contributed to this situation?",
        "intervention_key": "Blaming"
    },

    "Fallacy of Change": {
        "keywords": [
            "if they would",
            "if only they",
            "make them change",
            "change them",
            "force them",
            "convince them",
            "if they changed"
        ],
        "explanation": "Focusing on changing another person's behavior as though their change is within your control.",
        "reframe_prompt": "What can you control about your own response, boundary, or next step?",
        "intervention_key": "Fallacy of Change"
    }
}


# ============================================================
# SAFETY
# ============================================================

SELF_HARM_PHRASES = [
    "want to kill myself",
    "want to die",
    "going to kill myself",
    "going to die",
    "end my life",
    "end it all",
    "suicide",
    "commit suicide",
    "take my own life",
    "hurt myself",
    "hurt myself badly",
    "cut myself",
    "overdose",
    "jump off",
    "shoot myself",
    "hang myself",
    "poison myself",
    "no reason to live",
    "better off dead",
    "wish I was dead",
    "can't go on anymore",
    "give up on life"
]

INTENT_INDICATORS = [
    "want to",
    "going to",
    "planning to",
    "thinking about",
    "ready to",
    "about to"
]

DEATH_WORDS = [
    "kill",
    "die",
    "dead",
    "end it",
    "suicide",
    "overdose",
    "hurt myself"
]


def check_safety(text):
    """
    Phase 1 safety gate.
    This is deliberately conservative and rule-based.
    """

    text_lower = text.lower()

    for phrase in SELF_HARM_PHRASES:
        if phrase in text_lower:
            return True

    has_intent = any(
        phrase in text_lower
        for phrase in INTENT_INDICATORS
    )

    has_harm_word = any(
        word in text_lower
        for word in DEATH_WORDS
    )

    return has_intent and has_harm_word


# ============================================================
# DISTRESS EXTRACTION
# ============================================================

def extract_distress_rating(text):
    """
    Extract a standalone number from 0-10.
    """

    match = re.search(r'(?<!\d)(10|[0-9])(?!\d)', text)

    if match:
        value = int(match.group(1))

        if 0 <= value <= 10:
            return value

    return None


# ============================================================
# PATTERN DETECTION
# ============================================================

def detect_patterns(text):
    """
    Returns multiple candidate cognitive patterns.

    This is intentionally different from the original
    single-label detector.

    Output:
        [
            {
                "name": ...,
                "score": ...,
                "explanation": ...,
                "reframe_prompt": ...
            }
        ]
    """

    text_lower = text.lower()

    results = []

    for name, data in COGNITIVE_DISTORTIONS.items():

        score = 0

        for keyword in data["keywords"]:

            if keyword.lower() in text_lower:

                # Stronger signals
                if keyword in [
                    "worthless",
                    "hopeless",
                    "doomed",
                    "forever",
                    "always",
                    "never",
                    "no one",
                    "nobody",
                    "definitely",
                    "clearly"
                ]:
                    score += 2
                else:
                    score += 1

        if score > 0:

            results.append({
                "name": name,
                "score": score,
                "explanation": data["explanation"],
                "reframe_prompt": data["reframe_prompt"],
                "intervention_key": data["intervention_key"]
            })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results


def detect_best_pattern(text):
    patterns = detect_patterns(text)

    if not patterns:
        return None

    return patterns[0]


# ============================================================
# STATE CLASSIFICATION
# ============================================================

def classify_state(text, distress=None):
    """
    Non-diagnostic state classification.

    This is the beginning of the future Phase 2
    adaptive architecture.
    """

    text_lower = text.lower()

    patterns = detect_patterns(text)

    # Emotion / activation signals
    if any(word in text_lower for word in [
        "panic",
        "panicking",
        "overwhelmed",
        "can't breathe",
        "terrified",
        "freaking out"
    ]):
        emotion_state = "high_activation"

    elif any(word in text_lower for word in [
        "angry",
        "furious",
        "mad",
        "irritated"
    ]):
        emotion_state = "agitation"

    elif any(word in text_lower for word in [
        "sad",
        "hopeless",
        "empty",
        "worthless"
    ]):
        emotion_state = "low_mood"

    elif any(word in text_lower for word in [
        "worried",
        "anxious",
        "nervous",
        "concerned",
        "afraid",
        "scared"
    ]):
        emotion_state = "anxiety"

    else:
        emotion_state = "unspecified"

    # Cognitive mode
    if any(
        pattern["name"] == "Catastrophizing"
        for pattern in patterns
    ):
        cognitive_mode = "threat_prediction"

    elif any(
        pattern["name"] == "Mindreading"
        for pattern in patterns
    ):
        cognitive_mode = "social_prediction"

    elif any(
        pattern["name"] in [
            "Global Labeling",
            "Personalization",
            "Shoulds"
        ]
        for pattern in patterns
    ):
        cognitive_mode = "self_evaluation"

    elif any(
        pattern["name"] in [
            "Overgeneralization",
            "Polarized Thinking"
        ]
        for pattern in patterns
    ):
        cognitive_mode = "rigid_interpretation"

    else:
        cognitive_mode = "neutral"

    # Intervention need
    if distress is not None and distress >= 7:
        intervention_need = "regulation_first"

    elif any(
        pattern["name"] == "Catastrophizing"
        for pattern in patterns
    ):
        intervention_need = "probability_reframe"

    elif any(
        pattern["name"] == "Mindreading"
        for pattern in patterns
    ):
        intervention_need = "reality_check"

    elif any(
        pattern["name"] == "Shoulds"
        for pattern in patterns
    ):
        intervention_need = "flexibility_reframe"

    elif any(
        pattern["name"] == "Overgeneralization"
        for pattern in patterns
    ):
        intervention_need = "specificity"

    else:
        intervention_need = "exploration"

    return {
        "emotion_state": emotion_state,
        "cognitive_mode": cognitive_mode,
        "patterns": patterns,
        "intervention_need": intervention_need,
        "safety_flag": "none"
    }


# ============================================================
# INTERVENTION SELECTION
# ============================================================

def get_interventions(pattern_name=None, distress_level=None, intervention_need=None):

    selected = []

    # High activation takes priority
    if distress_level is not None and distress_level >= 7:

        selected.extend(
            INTERVENTIONS["High Distress"]
        )

    # Pattern-specific skills
    if pattern_name in INTERVENTIONS:

        selected.extend(
            INTERVENTIONS[pattern_name]
        )

    # Need-specific fallback
    if intervention_need == "problem_solving":

        selected.extend(
            INTERVENTIONS["Problem Solving"]
        )

    elif intervention_need == "behavioral_structure":

        selected.extend(
            INTERVENTIONS["Behavioral Structure"]
        )

    # Remove duplicates
    unique = {}

    for intervention in selected:
        unique[intervention["name"]] = intervention

    selected = list(unique.values())

    if not selected:
        selected = INTERVENTIONS["High Distress"][:1]

    return random.sample(
        selected,
        min(2, len(selected))
    )


# ============================================================
# SESSION MANAGEMENT
# ============================================================

SESSION_KEYS = [
    "situation",
    "emotion",
    "initial_distress",
    "thought",
    "distortion",
    "patterns",
    "reframe",
    "final_distress",
    "waiting_for_reframe",
    "current_state"
]


def reset_session(session_state):

    for key in SESSION_KEYS:
        session_state.pop(key, None)


def initialize_session():

    defaults = {
        "situation": None,
        "emotion": None,
        "initial_distress": None,
        "thought": None,
        "distortion": None,
        "patterns": [],
        "reframe": None,
        "final_distress": None,
        "waiting_for_reframe": False,
        "current_state": None
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================
# PROGRESS
# ============================================================

def get_phase():

    if not st.session_state.get("situation"):
        return 1

    if not st.session_state.get("emotion"):
        return 2

    if st.session_state.get("initial_distress") is None:
        return 3

    if not st.session_state.get("thought"):
        return 4

    if not st.session_state.get("reframe"):
        return 5

    if st.session_state.get("final_distress") is None:
        return 6

    return 7


def phase_label():

    phase = get_phase()

    labels = {
        1: "Situation",
        2: "Emotion",
        3: "Distress",
        4: "Automatic Thought",
        5: "Reframe",
        6: "Re-rate",
        7: "Complete"
    }

    return labels.get(
        phase,
        "Session"
    )


# ============================================================
# AGENT RESPONSE ENGINE
# ============================================================

def generate_response(user_text, session_state):

    response_parts = []

    # --------------------------------------------------------
    # SAFETY OVERRIDE
    # --------------------------------------------------------

    if check_safety(user_text):

        return (
            "⚠️ **Safety Alert**\n\n"
            "What you described may indicate an immediate safety concern. "
            "ClearLogic is designed for non-emergency cognitive support and "
            "is not a substitute for emergency or crisis care.\n\n"
            "If you may act on these thoughts or cannot keep yourself safe, "
            "please seek immediate professional or emergency assistance."
        )

    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    if user_text.lower().strip() in [
        "start new",
        "new session",
        "restart",
        "reset"
    ]:

        reset_session(session_state)

        return (
            "Absolutely. Let's start fresh.\n\n"
            "Tell me about a situation that is bothering you right now."
        )

    # --------------------------------------------------------
    # PHASE 1 — SITUATION
    # --------------------------------------------------------

    if not session_state.get("situation"):

        session_state["situation"] = user_text

        state = classify_state(user_text)

        session_state["current_state"] = state

        patterns = state["patterns"]

        if patterns:

            top = patterns[0]

            response_parts.append(
                "Thanks for explaining what is happening."
            )

            if top["score"] >= 2:

                response_parts.append(
                    f"I notice a possible **{top['name']}** pattern in the way "
                    f"the situation is being interpreted."
                )

        else:

            response_parts.append(
                "Thanks for explaining the situation."
            )

        response_parts.append(
            "Before we examine the thought itself, what emotion are you "
            "experiencing most strongly right now?"
        )

        return "\n\n".join(response_parts)

    # --------------------------------------------------------
    # PHASE 2 — EMOTION
    # --------------------------------------------------------

    if not session_state.get("emotion"):

        session_state["emotion"] = user_text

        response_parts.append(
            f"Got it. You're experiencing **{user_text}**."
        )

        response_parts.append(
            "Now let's establish a baseline. On a scale from **0–10**, "
            "how distressed are you right now?"
        )

        response_parts.append(
            "**0 = completely calm | 10 = extremely distressed**"
        )

        return "\n\n".join(response_parts)

    # --------------------------------------------------------
    # PHASE 3 — DISTRESS
    # --------------------------------------------------------

    if session_state.get("initial_distress") is None:

        distress = extract_distress_rating(user_text)

        if distress is None:

            return (
                "I'd like to get a baseline distress rating first.\n\n"
                "Please give me a number from **0–10**."
            )

        session_state["initial_distress"] = distress

        # Reclassify with distress information
        state = classify_state(
            session_state["situation"],
            distress
        )

        session_state["current_state"] = state

        response_parts.append(
            f"Baseline distress: **{distress}/10**."
        )

        if distress >= 7:

            interventions = get_interventions(
                distress_level=distress,
                intervention_need="regulation_first"
            )

            response_parts.append(
                "Your distress is elevated, so let's regulate first "
                "before doing deeper cognitive work."
            )

            for intervention in interventions:

                response_parts.append(
                    f"🌿 **{intervention['name']}**\n"
                    f"{intervention['desc']}"
                )

            response_parts.append(
                "When you're ready, tell me the automatic thought that "
                "keeps running through your mind."
            )

        else:

            response_parts.append(
                "Good. We have a baseline. Now let's look at the thought "
                "attached to the situation."
            )

            response_parts.append(
                "What is the automatic thought or belief running through "
                "your mind?"
            )

        return "\n\n".join(response_parts)

    # --------------------------------------------------------
    # PHASE 4 — AUTOMATIC THOUGHT
    # --------------------------------------------------------

    if not session_state.get("thought"):

        session_state["thought"] = user_text

        state = classify_state(
            user_text,
            session_state.get("initial_distress")
        )

        session_state["current_state"] = state

        patterns = state["patterns"]

        session_state["patterns"] = patterns

        if patterns:

            top = patterns[0]

            session_state["distortion"] = top["name"]

            response_parts.append(
                f"Let's examine this as a **{top['name']}** pattern."
            )

            response_parts.append(
                f"**What I'm seeing:** {top['explanation']}"
            )

            # Show secondary pattern if meaningful
            if len(patterns) > 1 and patterns[1]["score"] >= 2:

                response_parts.append(
                    f"There may also be a secondary **{patterns[1]['name']}** "
                    "pattern involved."
                )

            interventions = get_interventions(
                pattern_name=top["intervention_key"],
                distress_level=session_state.get("initial_distress"),
                intervention_need=state["intervention_need"]
            )

            response_parts.append(
                "**Try one of these skills:**"
            )

            for intervention in interventions:

                response_parts.append(
                    f"🛠️ **{intervention['name']}** — "
                    f"{intervention['desc']}"
                )

            response_parts.append(
                f"**Challenge question:** {top['reframe_prompt']}"
            )

        else:

            session_state["distortion"] = "None identified"

            response_parts.append(
                "I don't see a strong cognitive pattern that I can "
                "confidently identify from that statement."
            )

            response_parts.append(
                "Let's examine it without forcing a label."
            )

            response_parts.append(
                "**What evidence supports the thought, and what evidence "
                "might point in another direction?**"
            )

        response_parts.append(
            "Now write a more balanced version of the thought. "
            "It doesn't have to be positive — just more accurate."
        )

        session_state["waiting_for_reframe"] = True

        return "\n\n".join(response_parts)

    # --------------------------------------------------------
    # PHASE 5 — REFRAME
    # --------------------------------------------------------

    if (
        session_state.get("waiting_for_reframe")
        and not session_state.get("reframe")
    ):

        session_state["reframe"] = user_text
        session_state["waiting_for_reframe"] = False

        response_parts.append(
            "Good. The goal here isn't forced positivity. "
            "It's a more balanced interpretation."
        )

        response_parts.append(
            f"**Balanced thought:**\n\n> {user_text}"
        )

        response_parts.append(
            "Now let's see whether changing the interpretation changed "
            "the emotional intensity."
        )

        response_parts.append(
            "What is your distress level **now**, from 0–10?"
        )

        return "\n\n".join(response_parts)

    # --------------------------------------------------------
    # PHASE 6 — FINAL DISTRESS
    # --------------------------------------------------------

    if (
        session_state.get("reframe")
        and session_state.get("final_distress") is None
    ):

        final_distress = extract_distress_rating(user_text)

        if final_distress is None:

            return (
                "Please give me your current distress level from "
                "**0–10** so we can compare it with where you started."
            )

        session_state["final_distress"] = final_distress

        initial = session_state.get(
            "initial_distress",
            0
        )

        delta = initial - final_distress

        if delta > 0:

            outcome = "Distress decreased"

        elif delta < 0:

            outcome = "Distress increased"

        else:

            outcome = "Distress stayed the same"

        response_parts.append(
            "### 🧠 Session Complete"
        )

        response_parts.append(
            f"**Starting distress:** {initial}/10"
        )

        response_parts.append(
            f"**Ending distress:** {final_distress}/10"
        )

        response_parts.append(
            f"**Change:** {initial} → {final_distress} "
            f"({delta:+d})"
        )

        response_parts.append(
            f"**Outcome:** {outcome}"
        )

        response_parts.append(
            f"**Pattern examined:** "
            f"{session_state.get('distortion', 'None identified')}"
        )

        response_parts.append(
            "The purpose of the exercise was not to prove that your "
            "original thought was wrong. It was to create enough distance "
            "to examine whether another interpretation was possible."
        )

        response_parts.append(
            "You can start another session whenever you're ready."
        )

        return "\n\n".join(response_parts)

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return (
        "Let's slow this down and look at what is happening right now. "
        "What part of the situation feels most difficult?"
    )


# ============================================================
# INITIALIZE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []

initialize_session()


# ============================================================
# HEADER
# ============================================================

st.title("🧠 ClearLogic Engine")

st.subheader(
    "Agentic Cognitive Support"
)

st.markdown(
    """
    <div class="info-box">
    ClearLogic helps you slow down a stressful situation, examine the
    thoughts attached to it, and identify a more balanced way to interpret
    what is happening.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Session")

    if st.button(
        "🔄 Reset Session",
        use_container_width=True
    ):

        st.session_state.messages = []

        reset_session(
            st.session_state
        )

        st.rerun()

    st.markdown("---")

    # Progress
    phase = get_phase()

    st.markdown(
        f"""
        <div class="progress-box">
            <div class="small-label">Current Step</div>
            <strong>{phase_label()}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress(
        min((phase - 1) / 6, 1.0)
    )

    st.markdown("---")

    st.markdown("### How it works")

    st.markdown(
        """
        1. Describe the situation  
        2. Identify the emotion  
        3. Rate distress  
        4. Examine the automatic thought  
        5. Identify thinking patterns  
        6. Practice a balanced interpretation  
        7. Re-rate distress
        """
    )

    st.markdown("---")

    # Internal state display
    st.markdown("### Agent State")

    current_state = st.session_state.get(
        "current_state"
    )

    if current_state:

        st.markdown(
            f"""
            <div class="state-box">
            <strong>Emotion State:</strong><br>
            {current_state.get("emotion_state", "—")}
            <br><br>

            <strong>Cognitive Mode:</strong><br>
            {current_state.get("cognitive_mode", "—")}
            <br><br>

            <strong>Intervention Need:</strong><br>
            {current_state.get("intervention_need", "—")}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.caption(
            "Agent state will appear after the first interaction."
        )

    st.markdown("---")

    st.caption(
        "ClearLogic is a cognitive support prototype and is not a "
        "diagnostic or emergency-care system."
    )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# INITIAL GREETING
# ============================================================

if not st.session_state.messages:

    with st.chat_message("assistant"):

        st.markdown(
            """
            Hello. I'm the **ClearLogic Engine**. 🧠

            I can help you slow down a stressful situation, examine the
            thoughts connected to it, and work toward a more balanced
            interpretation.

            This usually takes about **5–10 minutes**.

            **To begin:**  
            Tell me about a situation that is bothering you right now.
            """
        )


# ============================================================
# USER INPUT
# ============================================================

if prompt := st.chat_input(
    "Type your message here..."
):

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)

    # Agent response
    with st.chat_message("assistant"):

        response = generate_response(
            prompt,
            st.session_state
        )

        st.markdown(response)

    # Save response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    st.rerun()
