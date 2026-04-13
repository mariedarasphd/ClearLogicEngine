import streamlit as st
import pandas as pd
import numpy as np
import re
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ClearLogic Engine", 
    page_icon="🧠", 
    layout="wide"
)

# --- STYLING ---
st.markdown("""
<style>
    .stApp { 
        background-color: #0a192f; 
        color: #ffffff !important; 
    }
    h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
    p, span, div, li, label, button { color: #ffffff !important; }
    
    /* Chat Messages */
    .stChatMessage { 
        background-color: #112240 !important; 
        color: #ffffff !important; 
        border-radius: 10px; 
        padding: 15px; 
        margin-bottom: 10px;
    }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1d3557 !important;
    }
    
    /* Buttons */
    .stButton>button { 
        background-color: #64ffda !important; 
        color: #0a192f !important; 
        font-weight: bold; 
        font-size: 16px; 
    }
    .stButton>button:hover { 
        background-color: #4cc9ac !important; 
    }
    
    /* Input */
    .stTextInput input, .stTextArea textarea { 
        color: #ffffff !important; 
        background-color: #112240 !important; 
        border: 1px solid #64ffda !important;
    }
    
    /* Intervention Cards */
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
</style>
""", unsafe_allow_html=True)

# --- LOGO ---
LOGO_PATH = "logo.png"
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=200)
else:
    st.warning("⚠️ Logo 'logo.png' not found.")

# --- ENHANCED DATA DEFINITIONS ---

# Expanded Intervention Library
INTERVENTIONS = {
    "High Distress (General)": [
        {
            "name": "🫁 Box Breathing",
            "desc": "Inhale 4s, Hold 4s, Exhale 4s, Hold 4s. Repeat 3x.",
            "type": "physiological"
        },
        {
            "name": "🌬️ Physiological Sigh",
            "desc": "Two sharp inhales through the nose, one long exhale through the mouth. Repeat 3x.",
            "type": "physiological"
        },
        {
            "name": "🌍 5-4-3-2-1 Grounding",
            "desc": "Name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste.",
            "type": "grounding"
        }
    ],
    "Filtering": [
        {
            "name": "✨ The 3 Good Things",
            "desc": "List 3 small positive things that happened today, no matter how tiny.",
            "type": "cognitive"
        },
        {
            "name": "⚖️ Evidence Balance Sheet",
            "desc": "Draw a line. Left: Bad evidence. Right: Good evidence. Count them.",
            "type": "cognitive"
        }
    ],
    "Polarized Thinking": [
        {
            "name": "📊 The Continuum Scale",
            "desc": "Instead of 'Pass/Fail', rate the situation 0-100. Where does it actually fall?",
            "type": "cognitive"
        },
        {
            "name": "🌈 The Gray Area",
            "desc": "Find one example where 'not perfect' is still 'good enough'.",
            "type": "cognitive"
        }
    ],
    "Overgeneralization": [
        {
            "name": "🔍 The Exception Hunt",
            "desc": "Find ONE time in the past when this 'always' statement was false.",
            "type": "cognitive"
        },
        {
            "name": "🗣️ The 'Sometimes' Swap",
            "desc": "Replace 'Always/Never' with 'Sometimes' or 'This time'.",
            "type": "linguistic"
        }
    ],
    "Jumping to Conclusions": [
        {
            "name": "⚖️ The Courtroom Test",
            "desc": "If this were a court case, would the evidence hold up 'beyond reasonable doubt'?",
            "type": "cognitive"
        },
        {
            "name": "🕵️ Alternative Explanations",
            "desc": "List 3 other reasons why this might have happened (that aren't about you).",
            "type": "cognitive"
        }
    ],
    "Catastrophizing": [
        {
            "name": "📉 Decatastrophizing",
            "desc": "If the worst happens, what is your Plan B? You have survived before.",
            "type": "cognitive"
        },
        {
            "name": "📅 The 5-Year Test",
            "desc": "Will this matter in 5 years? 5 months? 5 weeks?",
            "type": "perspective"
        }
    ],
    "Personalization": [
        {
            "name": "🥧 The Pie Chart",
            "desc": "Draw a pie chart of all factors. How much is actually your fault?",
            "type": "visual"
        },
        {
            "name": "🛡️ The Shield",
            "desc": "Visualize a shield deflecting blame that isn't yours.",
            "type": "visualization"
        }
    ],
    "Control Fallacies": [
        {
            "name": "⭕ Circle of Control",
            "desc": "Draw a circle. Inside: What you control. Outside: What you don't. Focus on Inside.",
            "type": "visual"
        },
        {
            "name": "🤝 Influence vs. Control",
            "desc": "You can't control others, but you can control your reaction to them.",
            "type": "cognitive"
        }
    ],
    "Fallacy of Fairness": [
        {
            "name": "⚖️ Reality Check",
            "desc": "Life isn't a courtroom. It's messy. Accept the messiness to reduce anger.",
            "type": "acceptance"
        },
        {
            "name": "🎁 The Gift of Choice",
            "desc": "Choose to let go of the expectation of fairness to free yourself.",
            "type": "acceptance"
        }
    ],
    "Blaming": [
        {
            "name": "🔄 Ownership Shift",
            "desc": "Change 'You made me feel...' to 'I felt... when you...' ",
            "type": "linguistic"
        },
        {
            "name": "🪞 The Mirror",
            "desc": "What part of this situation did YOU contribute to? (Even 1%)",
            "type": "cognitive"
        }
    ],
    "Shoulds": [
        {
            "name": "💭 The 'Prefer' Swap",
            "desc": "Replace 'I should' with 'I prefer' or 'It would be nice if'.",
            "type": "linguistic"
        },
        {
            "name": "🧱 The Rule Book",
            "desc": "Who wrote this rule? Is it actually useful, or just rigid?",
            "type": "cognitive"
        }
    ],
    "Emotional Reasoning": [
        {
            "name": "🧠 Fact vs. Feeling",
            "desc": "Write: 'I feel X' (True). Write: 'Therefore X is true' (Questionable).",
            "type": "cognitive"
        },
        {
            "name": "🔍 The Detective",
            "desc": "What objective evidence contradicts this feeling?",
            "type": "cognitive"
        }
    ],
    "Fallacy of Change": [
        {
            "name": "🚪 Boundaries",
            "desc": "Focus on your boundaries, not changing them. You can't force change.",
            "type": "behavioral"
        },
        {
            "name": "🌱 Acceptance",
            "desc": "Accept them as they are. Change only comes from within them.",
            "type": "acceptance"
        }
    ],
    "Global Labeling": [
        {
            "name": "🏷️ Specificity",
            "desc": "Describe the BEHAVIOR, not the person. 'I made a mistake' vs 'I am a loser'.",
            "type": "linguistic"
        },
        {
            "name": "🌟 The Whole Picture",
            "desc": "List 3 good qualities you have that contradict this label.",
            "type": "cognitive"
        }
    ],
    "Always Being Right": [
        {
            "name": "🤝 Connection > Correction",
            "desc": "Ask: 'Do I want to be right, or do I want to connect?'",
            "type": "perspective"
        },
        {
            "name": "🤷 The 'So What?'",
            "desc": "If I'm wrong, so what? Does it actually matter?",
            "type": "perspective"
        }
    ],
    "Heaven's Reward Fallacy": [
        {
            "name": "❤️ Intrinsic Value",
            "desc": "Why did you do this task? Find value in the act itself, not the reward.",
            "type": "cognitive"
        },
        {
            "name": "🎁 Self-Reward",
            "desc": "Reward yourself immediately for the effort, regardless of external validation.",
            "type": "behavioral"
        }
    ]
}

# Enhanced Distortion Definitions with Subtle Patterns
COGNITIVE_DISTORTIONS = {
    "Filtering": {
        "keywords": ["only", "but", "ignoring", "positive", "negative", "focus on", "nothing good", "all bad"],
        "negators": ["not only", "not just", "didn't ignore"],
        "explanation": "Focusing only on the bad parts and ignoring the good ones.",
        "reframe_prompt": "Can you list 3 positive aspects you might be overlooking?",
        "intervention_key": "Filtering"
    },
    "Polarized Thinking": {
        "keywords": ["perfect", "failure", "all or nothing", "either or", "total", "complete", "zero", "100%", "always", "never"],
        "negators": ["not perfect", "not total", "somewhat"],
        "explanation": "Seeing things as all good or all bad, with no middle ground.",
        "reframe_prompt": "Where is the middle ground? What's a more realistic standard?",
        "intervention_key": "Polarized Thinking"
    },
    "Overgeneralization": {
        "keywords": ["always", "never", "every time", "everyone", "no one", "all", "none", "again", "forever"],
        "negators": ["not always", "not never", "sometimes", "rarely", "once"],
        "explanation": "Assuming one bad event means it will always happen.",
        "reframe_prompt": "Is this truly 'always', or is there an exception?",
        "intervention_key": "Overgeneralization"
    },
    "Jumping to Conclusions": {
        "keywords": ["they think", "they feel", "they know", "they want", "they don't", "surely", "obviously", "clearly", "must be", "definitely"],
        "negators": ["maybe", "perhaps", "possibly", "I wonder", "I don't know"],
        "explanation": "Assuming you know what others are thinking without proof.",
        "reframe_prompt": "What evidence do I have? What else could explain this?",
        "intervention_key": "Jumping to Conclusions"
    },
    "Catastrophizing": {
        "keywords": ["worst", "disaster", "terrible", "horrible", "can't stand", "ruined", "gone", "end of the world", "hopeless", "doomed"],
        "negators": ["not the worst", "manageable", "okay", "survivable"],
        "explanation": "Expecting the worst possible outcome to happen.",
        "reframe_prompt": "What's the most realistic outcome? What's the worst that could actually happen?",
        "intervention_key": "Catastrophizing"
    },
    "Personalization": {
        "keywords": ["my fault", "because of me", "I caused", "they're mad at me", "I made", "it's my responsibility"],
        "negators": ["not my fault", "not because of me", "someone else"],
        "explanation": "Blaming yourself for things outside your control.",
        "reframe_prompt": "What factors were outside my control? What else could have caused this?",
        "intervention_key": "Personalization"
    },
    "Control Fallacies": {
        "keywords": ["can't help", "helpless", "victim", "responsible for", "make me", "have to", "forced", "trapped"],
        "negators": ["I can choose", "I have a choice", "I can control"],
        "explanation": "Feeling powerless or feeling responsible for everyone else's feelings.",
        "reframe_prompt": "What is actually within my control right now?",
        "intervention_key": "Control Fallacies"
    },
    "Fallacy of Fairness": {
        "keywords": ["fair", "unfair", "should", "deserve", "right", "wrong", "justice", "owed", "supposed to"],
        "negators": ["life isn't fair", "accepting", "realistic"],
        "explanation": "Getting upset because life doesn't feel fair to you.",
        "reframe_prompt": "Is life always fair? What would help me accept this situation?",
        "intervention_key": "Fallacy of Fairness"
    },
    "Blaming": {
        "keywords": ["you made me", "your fault", "my fault", "blame", "responsible", "caused", "because you"],
        "negators": ["not your fault", "not my fault", "shared"],
        "explanation": "Pointing fingers at others or yourself instead of looking at the whole picture.",
        "reframe_prompt": "Who actually controls my emotions? What part can I influence?",
        "intervention_key": "Blaming"
    },
    "Shoulds": {
        "keywords": ["should", "shouldn't", "must", "ought", "have to", "need to", "got to", "supposed to"],
        "negators": ["don't have to", "optional", "prefer"],
        "explanation": "Having strict rules about how you or others 'must' act.",
        "reframe_prompt": "What would happen if I dropped this rule? Is it flexible?",
        "intervention_key": "Shoulds"
    },
    "Emotional Reasoning": {
        "keywords": ["I feel", "because I feel", "therefore", "must be", "obviously", "clearly", "it feels like"],
        "negators": ["feeling isn't fact", "just a feeling", "maybe not"],
        "explanation": "Thinking your feelings are facts.",
        "reframe_prompt": "Are feelings facts? What evidence contradicts this feeling?",
        "intervention_key": "Emotional Reasoning"
    },
    "Fallacy of Change": {
        "keywords": ["if they would", "if only they", "change them", "make them", "pressure", "force", "convince"],
        "negators": ["accept them", "let go", "boundaries"],
        "explanation": "Thinking you can force someone to change if you push hard enough.",
        "reframe_prompt": "Can I control their change? What can I control about my response?",
        "intervention_key": "Fallacy of Change"
    },
    "Global Labeling": {
        "keywords": ["loser", "jerk", "idiot", "worthless", "useless", "disappointment", "stupid", "bad", "evil"],
        "negators": ["not a loser", "just a mistake", "human"],
        "explanation": "Calling yourself or others a negative label like 'loser' or 'jerk'.",
        "reframe_prompt": "Can I describe this more specifically without the label?",
        "intervention_key": "Global Labeling"
    },
    "Always Being Right": {
        "keywords": ["right", "wrong", "prove", "correct", "argument", "win", "defend", "show them"],
        "negators": ["doesn't matter", "connection", "relationship"],
        "explanation": "Needing to win every argument to feel okay.",
        "reframe_prompt": "Is being right more important than the relationship?",
        "intervention_key": "Always Being Right"
    },
    "Heaven's Reward Fallacy": {
        "keywords": ["deserve", "reward", "sacrifice", "earned", "owed", "after all I've done", "at least"],
        "negators": ["no reward needed", "intrinsic", "enjoy the process"],
        "explanation": "Feeling bitter because your hard work hasn't been recognized yet.",
        "reframe_prompt": "Can I find satisfaction in the action itself, not the reward?",
        "intervention_key": "Heaven's Reward Fallacy"
    }
}

# Safety Phrases
SELF_HARM_PHRASES = [
    "want to kill myself", "want to die", "going to kill myself", "going to die",
    "end my life", "end it all", "suicide", "commit suicide", "take my own life",
    "hurt myself", "hurt myself badly", "cut myself", "overdose", "jump off",
    "shoot myself", "hang myself", "poison myself", "no reason to live",
    "better off dead", "wish I was dead", "can't go on anymore", "give up on life"
]

INTENT_INDICATORS = ["want to", "going to", "planning to", "thinking about", "ready to", "about to"]
DEATH_WORDS = ["kill", "die", "dead", "end it", "suicide", "overdose", "hurt myself"]

# --- HELPER FUNCTIONS ---

def check_safety(text):
    text_lower = text.lower()
    for phrase in SELF_HARM_PHRASES:
        if phrase in text_lower:
            return True
    has_intent = any(ind in text_lower for ind in INTENT_INDICATORS)
    has_harm_word = any(word in text_lower for word in DEATH_WORDS)
    if has_intent and has_harm_word:
        return True
    return False

def detect_distortion_advanced(text):
    """
    Advanced detection with context awareness and negation handling.
    Returns (distortion_name, confidence_score, explanation)
    """
    text_lower = text.lower()
    scores = {}
    
    for dist_name, dist_data in COGNITIVE_DISTORTIONS.items():
        score = 0
        keywords = dist_data["keywords"]
        negators = dist_data.get("negators", [])
        
        # Check for negators first (reduces false positives)
        has_negator = any(neg in text_lower for neg in negators)
        if has_negator:
            continue # Skip this distortion if negated
        
        # Score keywords
        for kw in keywords:
            if kw in text_lower:
                # Boost score for intensity words
                if kw in ["worst", "disaster", "ruined", "hopeless", "doomed"]:
                    score += 2
                else:
                    score += 1
        
        if score > 0:
            scores[dist_name] = score
    
    if not scores:
        return None, 0, None
    
    # Get best match
    best_match = max(scores, key=scores.get)
    confidence = scores[best_match]
    explanation = COGNITIVE_DISTORTIONS[best_match]["explanation"]
    
    return best_match, confidence, explanation

def extract_distress_rating(text):
    """Extract a number 0-10 from user input"""
    text_clean = text.lower()
    import re
    match = re.search(r'\b([0-9]|10)\b', text_clean)
    if match:
        return int(match.group(1))
    return None

def reset_session(session_state):
    """Safely reset all session keys"""
    keys_to_reset = ['situation', 'emotion', 'initial_distress', 'thought', 'distortion', 'reframe', 'final_distress', 'waiting_for_reframe']
    for key in keys_to_reset:
        session_state.pop(key, None)

def get_intervention(distortion_name, distress_level):
    """Select the best intervention based on distortion and distress level"""
    interventions = []
    
    # Always add high distress interventions if needed
    if distress_level >= 7:
        interventions.extend(INTERVENTIONS["High Distress (General)"])
    
    # Add distortion-specific interventions
    if distortion_name and distortion_name in INTERVENTIONS:
        interventions.extend(INTERVENTIONS[distortion_name])
    
    # If no specific intervention, add a general one
    if not interventions:
        interventions = INTERVENTIONS["High Distress (General)"][:1] # Default to breathing
    
    # Return a random selection of 1-2 interventions
    import random
    selected = random.sample(interventions, min(len(interventions), 2))
    return selected

def generate_response(user_text, session_state):
    """
    Agentic Logic: Analyzes input and generates a CBT-guided response.
    """
    response_parts = []
    
    # 1. Safety Check
    if check_safety(user_text):
        return "⚠️ **Safety Alert**: I hear you are in crisis. Please call 988 or go to the ER immediately. I am here to listen, but professional help is needed right now."

    # 2. Check if user wants to start fresh
    if user_text.lower().strip() in ['start new', 'new session', 'restart', 'reset']:
        reset_session(session_state)
        return "Great! Let's start fresh. Tell me about a new situation that's bothering you."

    # PHASE 0: No situation yet
    if not session_state.get('situation'):
        session_state['situation'] = user_text
        response_parts.append(f"Thanks for sharing that. I hear you're dealing with this situation.")
        
        detected_dist, conf, expl = detect_distortion_advanced(user_text)
        if detected_dist and conf >= 2: # Only mention if confident
            response_parts.append(f"I notice you might be experiencing **{detected_dist}** ({expl}).")
        
        response_parts.append("How are you feeling right now about this? (e.g., Anxious, Angry, Sad, Frustrated)")
        return "\n\n".join(response_parts)

    # PHASE 1: Have situation, collect emotion
    if not session_state.get('emotion'):
        session_state['emotion'] = user_text
        response_parts.append(f"Got it. You're feeling **{user_text}**.")
        response_parts.append("On a scale of **0-10**, how distressed are you right now? (0 = calm, 10 = extremely distressed)")
        response_parts.append("(Just reply with a number like '7' or '8')")
        return "\n\n".join(response_parts)

    # PHASE 1.5: Have situation + emotion, collect initial distress
    if not session_state.get('initial_distress'):
        distress_rating = extract_distress_rating(user_text)
        if distress_rating is not None:
            session_state['initial_distress'] = distress_rating
            response_parts.append(f"Got it - distress level: **{distress_rating}/10**.")
            
            if distress_rating >= 7:
                # Suggest immediate grounding
                interventions = get_intervention(None, distress_rating)
                response_parts.append("Your distress seems high. Let's try a quick grounding exercise first:")
                for inter in interventions:
                    response_parts.append(f"🌿 **{inter['name']}**: {inter['desc']}")
                response_parts.append("Take a moment. When ready, what's the **automatic thought** running through your mind?")
            else:
                response_parts.append("Now, what's the **automatic thought** or belief you have about this situation?")
        else:
            response_parts.append("Could you please rate your distress on a scale of 0-10? (Just reply with a number)")
        return "\n\n".join(response_parts)

    # PHASE 2: Have situation + emotion + initial_distress, collect automatic thought
    if not session_state.get('thought'):
        session_state['thought'] = user_text
        detected_dist, conf, expl = detect_distortion_advanced(user_text)
        
        if detected_dist and conf >= 2:
            session_state['distortion'] = detected_dist
            response_parts.append(f"That sounds like **{detected_dist}**.")
            response_parts.append(f"**Why?** {expl}")
            
            # Suggest intervention
            interventions = get_intervention(detected_dist, session_state.get('initial_distress', 5))
            response_parts.append(f"**Try this intervention:**")
            for inter in interventions:
                response_parts.append(f"🛠️ **{inter['name']}**: {inter['desc']}")
            
            response_parts.append(f"**Challenge Question:** {COGNITIVE_DISTORTIONS[detected_dist]['reframe_prompt']}")
        else:
            session_state['distortion'] = "None Identified"
            response_parts.append("That's an interesting thought. Let's examine it more closely.")
            response_parts.append("Is there any evidence that contradicts this thought? Or is there another way to look at it?")
        
        response_parts.append("Now, write a **more balanced thought** that challenges this distortion.")
        session_state['waiting_for_reframe'] = True
        return "\n\n".join(response_parts)

    # PHASE 3: Have situation + emotion + initial_distress + thought + distortion, waiting for reframe
    if session_state.get('waiting_for_reframe') and not session_state.get('reframe'):
        session_state['reframe'] = user_text
        session_state['waiting_for_reframe'] = False
        response_parts.append("Great work! That's a much more balanced perspective.")
        response_parts.append(f"**New Balanced Thought:** '{user_text}'")
        response_parts.append("How does your distress level feel **now** compared to the beginning? (Rate 0-10)")
        return "\n\n".join(response_parts)

    # PHASE 4: Have all data, waiting for final distress rating
    if session_state.get('reframe') and not session_state.get('final_distress'):
        final_distress = extract_distress_rating(user_text)
        if final_distress is None:
            final_distress = 5
        
        session_state['final_distress'] = final_distress
        initial_distress = session_state.get('initial_distress', 5)
        delta = initial_distress - final_distress
        
        response_parts.append("🎉 **Session Complete!**")
        response_parts.append(f"**Summary:**")
        response_parts.append(f"- Situation: {session_state.get('situation', '')[:50]}...")
        response_parts.append(f"- Emotion: {session_state.get('emotion', '')}")
        response_parts.append(f"- Initial Distress: {initial_distress}/10")
        response_parts.append(f"- Automatic Thought: {session_state.get('thought', '')[:50]}...")
        response_parts.append(f"- Distortion: {session_state.get('distortion', 'None')}")
        response_parts.append(f"- Balanced Thought: {session_state.get('reframe', '')[:50]}...")
        response_parts.append(f"- Final Distress: {final_distress}/10")
        response_parts.append(f"- Change: {initial_distress} → {final_distress} ({'Improved!' if delta > 0 else 'Same' if delta == 0 else 'Increased'})")
        response_parts.append("")
        response_parts.append("Would you like to start a **new session**? Just describe a new situation when you're ready.")
        
        reset_session(session_state)
        return "\n\n".join(response_parts)

    # PHASE 5: Session complete, user wants to start fresh
    if session_state.get('final_distress'):
        response_parts.append("Great! Let's start fresh.")
        response_parts.append("Tell me about a new situation that's bothering you.")
        reset_session(session_state)
        return "\n\n".join(response_parts)

    return "I'm here to help. Could you tell me more about what's on your mind?"

# --- SESSION STATE INITIALIZATION ---
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- MAIN APP ---

st.title("🧠 ClearLogic Engine")
st.subheader("Agentic CBT Companion")

# Sidebar
with st.sidebar:
    st.header("Controls")
    if st.button("Reset Session"):
        st.session_state.messages = []
        reset_session(st.session_state)
        st.rerun()
    
    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("1. Describe situation")
    st.markdown("2. Identify emotion")
    st.markdown("3. Rate distress (0-10)")
    st.markdown("4. AI detects patterns")
    st.markdown("5. Try interventions")
    st.markdown("6. Reframe & re-rate")

# Chat Interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = generate_response(prompt, st.session_state)
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Initial Greeting
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("Hello! I'm your ClearLogic CBT companion. 🧠\n\nI can help you identify unhelpful thinking patterns and find more balanced perspectives.\n\n**To start:** Tell me about a situation that's bothering you right now.")
