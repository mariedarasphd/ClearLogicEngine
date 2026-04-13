import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import hashlib
import uuid
import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ClearLogic Engine", 
    page_icon="🧠", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM STYLING (Dark Navy Theme) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0a192f; /* Dark Navy */
        color: #ffffff;
    }
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    /* Buttons */
    .stButton>button {
        background-color: #64ffda;
        color: #0a192f;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #4cc9ac;
    }
    /* Chat Messages */
    .stChatMessage {
        background-color: #112240;
        border-radius: 10px;
        padding: 10px;
    }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #172a45;
    }
</style>
""", unsafe_allow_html=True)

# --- ASSET LOADING ---
# Check if logo exists
LOGO_PATH = "logo.png"
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=200)
else:
    st.warning("⚠️ Logo not found. Please ensure 'logo.png' is in the same folder.")

# --- DATASET DERIVED RULES ---
# Based on your provided dataset
DISTORTION_KEYWORDS = {
    "Catastrophizing": [
        "gonna be able to", "things are just gonna get worse", "lose my job", 
        "go to jail", "something bad will happen", "worst case", "never", 
        "forever", "run out for rent", "credit score going down", "stuck"
    ],
    "Global Labelling": [
        "worthless", "disappointment", "useless", "no friends at all", 
        "I'm a", "I'm so", "I'm not as good", "I have no friends", "doing nothing"
    ],
    "Mindreading": [
        "they'll think", "people might not like me", "they don't want", 
        "they're telling me", "they don't understand", "they'll say no", 
        "feel like people are not wanting"
    ],
    "Emotional Reasoning": [
        "I feel", "because I feel", "therefore something bad", "I hate it", 
        "I'm worried therefore", "it's just something to procrastinate", "I just think"
    ],
    "Shoulds": [
        "I should", "I need to", "I have to", "should be", "I should carry on"
    ],
    "Personalization": [
        "depends on me", "everything depends", "my fault", "I have to cater"
    ],
    "Overgeneralization": [
        "always", "never", "every time", "keep happening", "get sidetracked", 
        "tomorrow doesn't happen", "same thing happens"
    ],
    "Control Fallacies": [
        "I'm not safe if I don't", "have to buy things", "something bad will happen if I don't"
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

# --- HELPER FUNCTIONS ---

def generate_anonymous_id():
    return str(uuid.uuid4())[:8]

def check_safety(text):
    safety_keywords = [
        "suicide", "kill myself", "end it", "die", "overdose", 
        "hurt someone", "firearm", "gun", "cutting", "self-harm"
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in safety_keywords)

def classify_distortion(text):
    """Matches user text against your dataset keywords."""
    text_lower = text.lower()
    scores = {}
    
    for category, keywords in DISTORTION_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in text_lower)
        scores[category] = matches
    
    if max(scores.values()) == 0:
        return "neutral"
    
    return max(scores, key=scores.get)

def get_skill_response(distortion_label):
    """Returns the skill script based on your dataset's intervention needs."""
    if distortion_label == "neutral":
        return {
            "name": "Grounding",
            "script": "Let's focus on the present moment. What is one thing you can do right now to feel slightly better?",
            "action": "Take a deep breath and name one thing you see."
        }
    
    skill_data = INTERVENTION_SKILLS.get(distortion_label, INTERVENTION_SKILLS["Emotional Reasoning"])
    return skill_data

# --- SESSION STATE ---
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

# --- APP LOGIC ---

def main():
    # 1. WELCOME SCREEN
    if not st.session_state.session_started:
        st.title("ClearLogic Engine")
        st.subheader("Anonymous, Skill-Based Cognitive Support")
        
        st.markdown("""
        - **No Diagnosis:** We focus on skills, not labels.
        - **Anonymous:** No names or personal data required.
        - **Safe:** Immediate crisis support if needed.
        """)
        
        user_input_id = st.text_input("Enter a Username or Random Number:", placeholder="e.g., User_8472")
        
        if st.button("Start Session"):
            if user_input_id:
                hashed_id = hashlib.sha256(user_input_id.encode()).hexdigest()[:8]
                st.session_state.user_id = f"ID_{hashed_id}"
                st.session_state.session_started = True
                st.rerun()
            else:
                st.warning("Please enter an ID.")
        return

    # 2. CONSENT SCREEN
    if not st.session_state.consent_given:
        st.title("Data Consent")
        st.markdown("""
        We collect **anonymous** data to validate the tool's effectiveness for underserved populations.
        - No names or emails stored.
        - Data used for research only.
        """)
        
        if st.checkbox("I consent to anonymous data collection"):
            st.session_state.consent_given = True
            st.rerun()
        return

    # 3. MAIN CHAT INTERFACE
    st.title("ClearLogic Session")
    
    # Display History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    user_input = st.chat_input("How are you feeling right now?")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # SAFETY CHECK
        if check_safety(user_input):
            with st.chat_message("assistant"):
                st.error("⚠️ **Safety Alert**: I hear you are in crisis.")
                st.markdown("""
                **Please reach out for immediate help:**
                - Call or Text **988**
                - Go to the nearest ER.
                """)
                st.session_state.messages.append({"role": "assistant", "content": "CRISIS_TRIGGERED"})
                return

        # CLASSIFY & RESPOND
        distortion = classify_distortion(user_input)
        skill = get_skill_response(distortion)
        
        response_text = f"**Detected Pattern:** {distortion}\n\n**Skill:** {skill['name']}\n\n{skill['script']}"
        
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)
        
        st.session_state.current_skill = skill['name']
        st.session_state.distress_pre = st.slider("Distress Level (Before)", 0, 10, 8, key="pre_slider")

    # 4. POST-SESSION
    if st.session_state.distress_pre is not None and st.session_state.distress_post is None:
        st.divider()
        st.subheader("Check-in After Skill")
        post_val = st.slider("Distress Level (Now)", 0, 10, 4, key="post_slider")
        
        if st.button("Complete Session"):
            st.session_state.distress_post = post_val
            delta = st.session_state.distress_pre - post_val
            
            st.success(f"Session Complete! Distress reduced by {delta} points.")
            
            # Reset for next session
            st.session_state.distress_pre = None
            st.session_state.distress_post = None
            st.session_state.current_skill = None
            st.session_state.messages = []
            st.rerun()

    # 5. ADMIN VIEW (Demo Data)
    with st.expander("🔒 Admin View: Grant Validation Data"):
        st.markdown("**Simulated T-Test Results**")
        # Simulate data for demo
        data = pd.DataFrame({
            "Pre": [8, 7, 9, 6, 8],
            "Post": [4, 3, 5, 2, 4]
        })
        t_stat, p_val = stats.ttest_rel(data['Pre'], data['Post'])
        st.metric("Avg Reduction", f"{data['Pre'].mean() - data['Post'].mean():.1f}")
        st.metric("Significance (p-value)", f"{p_val:.4f}")
        if p_val < 0.05:
            st.success("✅ Statistically Significant Improvement")

if __name__ == "__main__":
    main()
