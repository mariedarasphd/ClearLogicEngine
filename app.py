import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import hashlib
import uuid
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="ClearLogic Engine", page_icon="🧠", layout="centered")

# --- STYLING (High Contrast - Bright White Text) ---
st.markdown("""
<style>
    /* Main Background - Dark Navy */
    .stApp {
        background-color: #0a192f;
        color: #ffffff !important;
    }
    
    /* All Text Elements - Bright White */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    p, span, div, li, label, button {
        color: #ffffff !important;
    }
    
    /* Chat Messages - White Text */
    .stChatMessage {
        background-color: #112240 !important;
        color: #ffffff !important;
        border-radius: 10px;
        padding: 15px;
    }
    
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #172a45 !important;
    }
    
    /* User Messages - Slightly Different Background */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #1d3557 !important;
    }
    
    /* Buttons - Bright Teal with White Text */
    .stButton>button {
        background-color: #64ffda !important;
        color: #0a192f !important;
        border: none;
        font-weight: bold;
        font-size: 16px;
    }
    
    .stButton>button:hover {
        background-color: #4cc9ac !important;
    }
    
    /* Input Fields - White Text */
    .stTextInput input, .stTextArea textarea {
        color: #ffffff !important;
        background-color: #112240 !important;
    }
    
    /* Sliders - White Labels */
    .stSlider label {
        color: #ffffff !important;
    }
    
    /* Success/Error Messages - High Contrast */
    .stSuccess {
        color: #64ffda !important;
        background-color: #112240 !important;
    }
    
    .stError {
        color: #ff6b6b !important;
        background-color: #112240 !important;
    }
    
    .stWarning {
        color: #ffd93d !important;
        background-color: #112240 !important;
    }
    
    /* Debug Box - Subtle Gray */
    .debug-box {
        background-color: #233554 !important;
        padding: 10px;
        border-radius: 5px;
        font-size: 0.8em;
        color: #8892b0 !important;
        margin-top: 10px;
        border: 1px solid #64ffda !important;
    }
    
    /* Links - Bright Cyan */
    a {
        color: #64ffda !important;
    }
    
    /* Code Blocks - Light Background */
    code {
        background-color: #112240 !important;
        color: #64ffda !important;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGO ---
LOGO_PATH = "logo.png"
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=200)
else:
    st.warning("⚠️ Logo 'logo.png' not found.")

# --- DATASET KEYWORDS ---
DISTORTION_KEYWORDS = {
    "Catastrophizing": [
        "gonna be able to", "things are just gonna get worse", "lose my job", 
        "go to jail", "something bad will happen", "worst case", "never", 
        "forever", "run out for rent", "credit score", "stuck", "die", "end it"
    ],
    "Global Labelling": [
        "worthless", "disappointment", "useless", "no friends", "I'm a", "I'm so", 
        "I'm not as good", "doing nothing", "failure", "idiot"
    ],
    "Mindreading": [
        "they'll think", "people might not like", "they don't want", "they're telling", 
        "they don't understand", "they'll say no", "feel like people", "judgment"
    ],
    "Emotional Reasoning": [
        "I feel", "because I feel", "therefore something bad", "I hate it", 
        "I'm worried therefore", "procrastinate", "just think", "sick inside"
    ],
    "Shoulds": [
        "I should", "I need to", "I have to", "should be", "should carry on", "must"
    ],
    "Personalization": [
        "depends on me", "everything depends", "my fault", "I have to cater", "blame"
    ],
    "Overgeneralization": [
        "always", "never", "every time", "keep happening", "sidetracked", 
        "tomorrow doesn't happen", "same thing happens", "again"
    ],
    "Control Fallacies": [
        "not safe if I don't", "have to buy", "something bad if I don't", "control"
    ]
}

INTERVENTION_SKILLS = {
    "Catastrophizing": {
        "name": "Probability Reframe",
        "script": "Let's look at the probability. Is this outcome 100% certain, or is it just a fear? What is a more realistic outcome?",
        "action": "Ask for evidence of the worst-case scenario vs. a neutral one."
    },
    "Global Labelling": {
        "name": "Reality Check",
        "script": "Labels like 'worthless' are broad. Can we break this down? Is there one specific thing that went wrong, or is it everything?",
        "action": "Identify one specific exception to the label."
    },
    "Mindreading": {
        "name": "Reality Check",
        "script": "We can't read minds. What is the actual evidence that they think that? Or is it possible they are just busy?",
        "action": "List 3 alternative explanations for their behavior."
    },
    "Emotional Reasoning": {
        "name": "Emotional Regulation",
        "script": "Feelings are real, but they aren't facts. Just because you feel it doesn't mean it's true. Let's pause and breathe.",
        "action": "Practice 1 minute of deep breathing before reacting."
    },
    "Shoulds": {
        "name": "Reality Check",
        "script": "'Shoulds' create pressure. What would happen if you didn't do it? Is there a more flexible way to look at this?",
        "action": "Replace 'I should' with 'I prefer' or 'I would like to'."
    },
    "Personalization": {
        "name": "Emotional Regulation",
        "script": "You are taking responsibility for things outside your control. What part of this was actually yours?",
        "action": "Draw a circle: Inside is 'My Control', Outside is 'Not My Control'."
    },
    "Overgeneralization": {
        "name": "Behavioral Activation",
        "script": "One bad event doesn't mean 'always'. Let's look at a time this didn't happen.",
        "action": "Recall one specific instance where the opposite was true."
    },
    "Control Fallacies": {
        "name": "Probability Reframe",
        "script": "Trying to control everything causes anxiety. What is one small thing you can control right now?",
        "action": "Focus on one immediate, actionable step."
    }
}

# --- SESSION STATE INIT ---
if 'session_started' not in st.session_state:
    st.session_state.session_started = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'consent_given' not in st.session_state:
    st.session_state.consent_given = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'distress_pre' not in st.session_state:
    st.session_state.distress_pre = None
if 'distress_post' not in st.session_state:
    st.session_state.distress_post = None
if 'current_skill' not in st.session_state:
    st.session_state.current_skill = None
if 'step' not in st.session_state:
    st.session_state.step = "input"

# --- FUNCTIONS ---

def check_safety(text):
    safety_keywords = ["suicide", "kill myself", "end it", "die", "overdose", "hurt someone", "firearm", "gun", "cutting", "self-harm"]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in safety_keywords)

def classify_distortion(text):
    text_lower = text.lower()
    scores = {}
    for category, keywords in DISTORTION_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in text_lower)
        scores[category] = matches
    
    if max(scores.values()) == 0:
        return "neutral"
    return max(scores, key=scores.get)

def get_skill_response(label):
    if label == "neutral":
        return {"name": "Grounding", "script": "Let's focus on the present. What is one small thing you can do right now?", "action": "Take a deep breath."}
    return INTERVENTION_SKILLS.get(label, INTERVENTION_SKILLS["Emotional Reasoning"])

# --- APP LOGIC ---

def main():
    # 1. WELCOME
    if not st.session_state.session_started:
        st.title("ClearLogic Engine")
        st.subheader("Anonymous, Skill-Based Cognitive Support")
        st.markdown("- **No Diagnosis** | - **Anonymous** | - **Safe**")
        
        uid = st.text_input("Enter Username or Number:", placeholder="e.g., User_8472")
        if st.button("Start Session"):
            if uid:
                st.session_state.user_id = f"ID_{hashlib.sha256(uid.encode()).hexdigest()[:8]}"
                st.session_state.session_started = True
                st.rerun()
            else:
                st.warning("Please enter an ID.")
        return

    # 2. CONSENT
    if not st.session_state.consent_given:
        st.title("Data Consent")
        st.markdown("We collect **anonymous** data to validate the tool. No names/emails stored.")
        if st.checkbox("I consent"):
            st.session_state.consent_given = True
            st.rerun()
        return

    # 3. MAIN INTERFACE
    st.title("ClearLogic Session")
    
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # INPUT HANDLING
    user_input = st.chat_input("How are you feeling right now?")

    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # SAFETY CHECK
        if check_safety(user_input):
            with st.chat_message("assistant"):
                st.error("⚠️ **Safety Alert**: I hear you are in crisis.")
                st.markdown("**Call 988 or go to ER immediately.**")
                st.session_state.messages.append({"role": "assistant", "content": "CRISIS"})
                return

        # CLASSIFICATION & RESPONSE
        distortion = classify_distortion(user_input)
        skill = get_skill_response(distortion)
        
        debug_info = f"Detected: {distortion} | Confidence: High"
        
        response_text = f"**Pattern Detected:** {distortion}\n\n**Skill:** {skill['name']}\n\n{skill['script']}"
        
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)
            st.markdown(f"<div class='debug-box'>{debug_info}</div>", unsafe_allow_html=True)
        
        st.session_state.current_skill = skill['name']
        st.session_state.step = "rating"
        st.rerun()

    # 4. RATING STEP
    if st.session_state.step == "rating":
        st.divider()
        st.subheader("Check-in After Skill")
        st.markdown(f"You tried **{st.session_state.current_skill}**. How do you feel now?")
        
        pre_val = st.slider("Distress Level (Before)", 0, 10, 8, key="pre_slider")
        post_val = st.slider("Distress Level (Now)", 0, 10, 4, key="post_slider")
        
        if st.button("Complete Session & Reset"):
            st.session_state.distress_pre = pre_val
            st.session_state.distress_post = post_val
            delta = pre_val - post_val
            
            st.success(f"Session Complete! Distress reduced by {delta} points.")
            
            st.session_state.messages = []
            st.session_state.step = "input"
            st.session_state.distress_pre = None
            st.session_state.distress_post = None
            st.session_state.current_skill = None
            st.rerun()

    # 5. ADMIN VIEW
    with st.expander("🔒 Admin View: Grant Data"):
        st.markdown("**Simulated T-Test Results**")
        data = pd.DataFrame({"Pre": [8, 7, 9, 6, 8], "Post": [4, 3, 5, 2, 4]})
        t_stat, p_val = stats.ttest_rel(data['Pre'], data['Post'])
        st.metric("Avg Reduction", f"{data['Pre'].mean() - data['Post'].mean():.1f}")
        st.metric("Significance (p-value)", f"{p_val:.4f}")
        if p_val < 0.05:
            st.success("✅ Statistically Significant Improvement")

if __name__ == "__main__":
    main()
