import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import hashlib
import os
import random

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
    
    /* Info Boxes */
    .info-box { 
        background-color: #1d3557; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 4px solid #64ffda; 
        margin: 10px 0; 
    }
    .intervention-card {
        background-color: #112240;
        border: 2px solid #64ffda;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGO ---
LOGO_PATH = "logo.png"
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=200)
else:
    st.warning("⚠️ Logo 'logo.png' not found.")

# --- DATA DEFINITIONS ---
COGNITIVE_DISTORTIONS = {
    "Filtering": {
        "keywords": ["only", "but", "ignoring", "positive", "negative", "focus on"],
        "explanation": "Focusing only on the bad parts and ignoring the good ones.",
        "reframe_prompt": "Can you list 3 positive aspects you might be overlooking?",
        "intervention": "Focus on the evidence: Write down 3 things that went well today."
    },
    "Polarized Thinking": {
        "keywords": ["perfect", "failure", "all or nothing", "either or", "total", "complete"],
        "explanation": "Seeing things as all good or all bad, with no middle ground.",
        "reframe_prompt": "Where is the middle ground? What's a more realistic standard?",
        "intervention": "The Continuum Technique: Rate the situation on a scale of 0-100 instead of pass/fail."
    },
    "Overgeneralization": {
        "keywords": ["always", "never", "every time", "everyone", "no one", "all", "none"],
        "explanation": "Assuming one bad event means it will always happen.",
        "reframe_prompt": "Is this truly 'always', or is there an exception?",
        "intervention": "Evidence Log: Find one counter-example to this 'always' statement."
    },
    "Jumping to Conclusions": {
        "keywords": ["they think", "they feel", "they know", "they want", "they don't", "surely"],
        "explanation": "Assuming you know what others are thinking without proof.",
        "reframe_prompt": "What evidence do I have? What else could explain this?",
        "intervention": "The Courtroom Test: If this were a court case, would the evidence hold up?"
    },
    "Catastrophizing": {
        "keywords": ["worst", "disaster", "terrible", "horrible", "can't stand", "ruined", "gone"],
        "explanation": "Expecting the worst possible outcome to happen.",
        "reframe_prompt": "What's the most realistic outcome? What's the worst that could actually happen?",
        "intervention": "Decatastrophizing: If the worst happened, how would you cope? What resources do you have?"
    },
    "Personalization": {
        "keywords": ["my fault", "because of me", "I caused", "they're mad at me", "I made"],
        "explanation": "Blaming yourself for things outside your control.",
        "reframe_prompt": "What factors were outside my control? What else could have caused this?",
        "intervention": "Pie Chart: Draw a pie chart of all factors contributing to the event."
    },
    "Control Fallacies": {
        "keywords": ["can't help", "helpless", "victim", "responsible for", "make me", "have to"],
        "explanation": "Feeling powerless or feeling responsible for everyone else's feelings.",
        "reframe_prompt": "What is actually within my control right now?",
        "intervention": "Circle of Control: Draw a circle. Inside: things you control. Outside: things you don't."
    },
    "Fallacy of Fairness": {
        "keywords": ["fair", "unfair", "should", "deserve", "right", "wrong", "justice"],
        "explanation": "Getting upset because life doesn't feel fair to you.",
        "reframe_prompt": "Is life always fair? What would help me accept this situation?",
        "intervention": "Acceptance: Acknowledge the unfairness, then focus on your response."
    },
    "Blaming": {
        "keywords": ["you made me", "your fault", "my fault", "blame", "responsible", "caused"],
        "explanation": "Pointing fingers at others or yourself instead of looking at the whole picture.",
        "reframe_prompt": "Who actually controls my emotions? What part can I influence?",
        "intervention": "Ownership Shift: Change 'You made me feel...' to 'I felt... when...'."
    },
    "Shoulds": {
        "keywords": ["should", "shouldn't", "must", "ought", "have to", "need to"],
        "explanation": "Having strict rules about how you or others 'must' act.",
        "reframe_prompt": "What would happen if I dropped this rule? Is it flexible?",
        "intervention": "Flexible Thinking: Replace 'should' with 'prefer' or 'would like'."
    },
    "Emotional Reasoning": {
        "keywords": ["I feel", "because I feel", "therefore", "must be", "obviously", "clearly"],
        "explanation": "Thinking your feelings are facts.",
        "reframe_prompt": "Are feelings facts? What evidence contradicts this feeling?",
        "intervention": "Fact vs. Feeling: Write down the feeling, then list 3 facts that contradict it."
    },
    "Fallacy of Change": {
        "keywords": ["if they would", "if only they", "change them", "make them", "pressure"],
        "explanation": "Thinking you can force someone to change if you push hard enough.",
        "reframe_prompt": "Can I control their change? What can I control about my response?",
        "intervention": "Boundaries: Focus on your boundaries and reactions, not changing others."
    },
    "Global Labeling": {
        "keywords": ["loser", "jerk", "idiot", "worthless", "useless", "disappointment", "stupid"],
        "explanation": "Calling yourself or others a negative label like 'loser' or 'jerk'.",
        "reframe_prompt": "Can I describe this more specifically without the label?",
        "intervention": "Specificity: Describe the behavior, not the person. 'I made a mistake' vs 'I am a loser'."
    },
    "Always Being Right": {
        "keywords": ["right", "wrong", "prove", "correct", "argument", "win", "defend"],
        "explanation": "Needing to win every argument to feel okay.",
        "reframe_prompt": "Is being right more important than the relationship?",
        "intervention": "Connection over Correction: Ask yourself: 'Do I want to be right, or do I want to connect?'."
    },
    "Heaven's Reward Fallacy": {
        "keywords": ["deserve", "reward", "sacrifice", "earned", "owed", "after all I've done"],
        "explanation": "Feeling bitter because your hard work hasn't been recognized yet.",
        "reframe_prompt": "Can I find satisfaction in the action itself, not the reward?",
        "intervention": "Intrinsic Value: List 3 reasons why doing this task was valuable regardless of recognition."
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

def detect_distortion(text):
    text_lower = text.lower()
    scores = {}
    for dist_name, dist_data in COGNITIVE_DISTORTIONS.items():
        matches = sum(1 for kw in dist_data["keywords"] if kw in text_lower)
        if matches > 0:
            scores[dist_name] = matches
    
    if not scores:
        return None, None
    
    best_match = max(scores, key=scores.get)
    return best_match, COGNITIVE_DISTORTIONS[best_match]

def extract_distress_rating(text):
    """Extract a number 0-10 from user input"""
    text_clean = text.lower()
    # Look for patterns like "7", "7/10", "level 7", "rating 7"
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

def generate_response(user_text, session_state):
    """
    Agentic Logic: Analyzes input and generates a CBT-guided response.
    Uses explicit phase tracking to avoid loops and KeyError.
    """
    response_parts = []
    
    # 1. Safety Check (always first)
    if check_safety(user_text):
        return "⚠️ **Safety Alert**: I hear you are in crisis. Please call 988 or go to the ER immediately. I am here to listen, but professional help is needed right now."

    # 2. Check if user wants to start fresh
    if user_text.lower().strip() in ['start new', 'new session', 'restart', 'reset']:
        reset_session(session_state)
        return "Great! Let's start fresh. Tell me about a new situation that's bothering you."

    # 3. Phase-Based Response Logic
    # PHASE 0: No situation yet - collect it
    if not session_state.get('situation'):
        session_state['situation'] = user_text
        response_parts.append(f"Thanks for sharing that. I hear you're dealing with this situation.")
        
        detected_dist, dist_data = detect_distortion(user_text)
        if detected_dist:
            response_parts.append(f"I notice you might be experiencing **{detected_dist}** ({dist_data['explanation']}).")
        
        response_parts.append("How are you feeling right now about this? (e.g., Anxious, Angry, Sad, Frustrated)")
        return "\n\n".join(response_parts)

    # PHASE 1: Have situation, collect emotion
    if not session_state.get('emotion'):
        session_state['emotion'] = user_text
        response_parts.append(f"Got it. You're feeling **{user_text}**.")
        
        # NEW: Ask for initial distress rating
        response_parts.append("On a scale of **0-10**, how distressed are you right now? (0 = calm, 10 = extremely distressed)")
        response_parts.append("(Just reply with a number like '7' or '8')")
        return "\n\n".join(response_parts)

    # PHASE 1.5: Have situation + emotion, collect initial distress rating
    if not session_state.get('initial_distress'):
        distress_rating = extract_distress_rating(user_text)
        if distress_rating is not None:
            session_state['initial_distress'] = distress_rating
            response_parts.append(f"Got it - distress level: **{distress_rating}/10**.")
            
            # High distress intervention
            if distress_rating >= 7:
                response_parts.append(f"Your distress seems high. Before we dive deeper, let's try a quick **Box Breathing** exercise:")
                response_parts.append("🫁 **Box Breathing**: Inhale 4s → Hold 4s → Exhale 4s → Hold 4s. Repeat 3 times.")
                response_parts.append("Take a moment. When ready, what's the **automatic thought** running through your mind about this situation?")
            else:
                response_parts.append("Now, what's the **automatic thought** or belief you have about this situation?")
        else:
            # User didn't provide a number, ask again
            response_parts.append("Could you please rate your distress on a scale of 0-10? (Just reply with a number)")
        return "\n\n".join(response_parts)

    # PHASE 2: Have situation + emotion + initial_distress, collect automatic thought
    if not session_state.get('thought'):
        session_state['thought'] = user_text
        detected_dist, dist_data = detect_distortion(user_text)
        
        if detected_dist:
            session_state['distortion'] = detected_dist
            response_parts.append(f"That sounds like **{detected_dist}**.")
            response_parts.append(f"**Why?** {dist_data['explanation']}")
            response_parts.append(f"**Challenge Question:** {dist_data['reframe_prompt']}")
            response_parts.append(f"**Try this intervention:** {dist_data['intervention']}")
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
            final_distress = 5  # Default if not parsed
        
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
        
        # Reset for next session
        reset_session(session_state)
        return "\n\n".join(response_parts)

    # PHASE 5: Session complete, user wants to start fresh
    if session_state.get('final_distress'):
        response_parts.append("Great! Let's start fresh.")
        response_parts.append("Tell me about a new situation that's bothering you.")
        reset_session(session_state)
        return "\n\n".join(response_parts)

    # Fallback (shouldn't reach here)
    return "I'm here to help. Could you tell me more about what's on your mind?"

# --- SESSION STATE INITIALIZATION ---
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- MAIN APP ---

st.title("🧠 ClearLogic Engine")
st.subheader("Agentic CBT Companion")

# Sidebar for controls
with st.sidebar:
    st.header("Controls")
    if st.button("Reset Session"):
        st.session_state.messages = []
        reset_session(st.session_state)
        st.rerun()
    
    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("1. Describe what's bothering you")
    st.markdown("2. Identify your emotion")
    st.markdown("3. Rate initial distress (0-10)")
    st.markdown("4. AI detects distortions")
    st.markdown("5. Practice reframing")
    st.markdown("6. Rate final distress")

# Chat Interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        response = generate_response(prompt, st.session_state)
        st.markdown(response)
    
    # Add AI message
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Initial Greeting if empty
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("Hello! I'm your ClearLogic CBT companion. 🧠\n\nI can help you identify unhelpful thinking patterns and find more balanced perspectives.\n\n**To start:** Tell me about a situation that's bothering you right now.")
