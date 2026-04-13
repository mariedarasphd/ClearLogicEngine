import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import hashlib
import uuid
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ClearLogic Engine", 
    page_icon="🧠", 
    layout="wide",
    theme={
        "base": "dark",
        "primaryColor": "#64ffda",
        "backgroundColor": "#0a192f",
        "secondaryBackgroundColor": "#112240",
        "textColor": "#ffffff",
        "font": "sans serif"
    }
)

# --- STYLING (High Contrast - Bright White Text) ---
st.markdown("""
<style>
    /* Force all text to white */
    .stApp { 
        background-color: #0a192f; 
        color: #ffffff !important; 
    }
    
    /* Headers and general text */
    h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
    p, span, div, li, label, button { color: #ffffff !important; }
    
    /* Chat messages */
    .stChatMessage { 
        background-color: #112240 !important; 
        color: #ffffff !important; 
        border-radius: 10px; 
        padding: 15px; 
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
    
    /* Text inputs and text areas */
    .stTextInput input, .stTextArea textarea { 
        color: #ffffff !important; 
        background-color: #112240 !important; 
        border: 1px solid #64ffda !important;
    }
    
    /* SELECTBOX FIX - Multiple selectors for maximum coverage */
    .stSelectbox > div > div {
        background-color: #112240 !important;
        color: #ffffff !important;
        border: 2px solid #64ffda !important;
    }
    .stSelectbox select {
        background-color: #112240 !important;
        color: #ffffff !important;
        border: 2px solid #64ffda !important;
    }
    .stSelectbox option {
        background-color: #112240 !important;
        color: #ffffff !important;
    }
    .stSelectbox label {
        color: #ffffff !important;
    }
    
    /* Sliders */
    .stSlider label { color: #ffffff !important; }
    
    /* Status messages */
    .stSuccess { color: #64ffda !important; background-color: #112240 !important; }
    .stError { color: #ff6b6b !important; background-color: #112240 !important; }
    .stWarning { color: #ffd93d !important; background-color: #112240 !important; }
    
    /* Custom boxes */
    .info-box { 
        background-color: #1d3557; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 4px solid #64ffda; 
        margin: 10px 0; 
    }
    .distortion-card { 
        background-color: #112240; 
        padding: 15px; 
        border-radius: 8px; 
        margin: 5px 0; 
        border: 1px solid #233554; 
    }
    .debug-box { 
        background-color: #233554; 
        padding: 10px; 
        border-radius: 5px; 
        font-size: 0.8em; 
        color: #8892b0; 
        margin-top: 10px; 
    }
</style>
""", unsafe_allow_html=True)

# --- LOGO ---
LOGO_PATH = "logo.png"
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=200)
else:
    st.warning("⚠️ Logo 'logo.png' not found.")

# --- 15 COGNITIVE DISTORTIONS (From Your Document) ---
COGNITIVE_DISTORTIONS = {
    "Filtering": {
        "definition": "Taking negative details and magnifying them while filtering out all positive aspects.",
        "example": "Dwelling on one criticism while ignoring all praise.",
        "keywords": ["only", "but", "ignoring", "positive", "negative", "focus on"],
        "reframe": "What are 3 positive aspects you're overlooking in this situation?"
    },
    "Polarized Thinking": {
        "definition": "Things are either black-or-white. No middle ground. Perfect or failure.",
        "example": "If I'm not perfect, I'm a total failure.",
        "keywords": ["perfect", "failure", "all or nothing", "either or", "total", "complete"],
        "reframe": "Where is the middle ground? What's a more realistic standard?"
    },
    "Overgeneralization": {
        "definition": "General conclusion based on a single incident. One bad event = never-ending pattern.",
        "example": "Something bad happened once, so it will always happen.",
        "keywords": ["always", "never", "every time", "everyone", "no one", "all", "none"],
        "reframe": "Is this truly always, or is there an exception?"
    },
    "Jumping to Conclusions": {
        "definition": "Knowing what others feel/think without evidence. Mind reading or fortune telling.",
        "example": "They're reacting negatively toward me (without asking).",
        "keywords": ["they think", "they feel", "they know", "they want", "they don't", "surely"],
        "reframe": "What evidence do I have? What else could explain this?"
    },
    "Catastrophizing": {
        "definition": "Expecting disaster. Magnifying problems or minimizing positives.",
        "example": "What if tragedy strikes? This is the worst thing ever.",
        "keywords": ["worst", "disaster", "terrible", "horrible", "can't stand", "ruined", "gone"],
        "reframe": "What's the most realistic outcome? What's the worst that could actually happen?"
    },
    "Personalization": {
        "definition": "Everything others do/say is a reaction to us. Comparing ourselves to others.",
        "example": "The hostess overcooked because I was late (when I wasn't responsible).",
        "keywords": ["my fault", "because of me", "I caused", "they're mad at me", "I made"],
        "reframe": "What factors were outside my control? What else could have caused this?"
    },
    "Control Fallacies": {
        "definition": "Feeling externally controlled (helpless) or internally controlling (responsible for others' happiness).",
        "example": "I can't help it (external) OR Why aren't you happy? (internal)",
        "keywords": ["can't help", "helpless", "victim", "responsible for", "make me", "have to"],
        "reframe": "What is actually within my control right now?"
    },
    "Fallacy of Fairness": {
        "definition": "Resentment from measuring situations against a 'fairness' ruler that others won't agree with.",
        "example": "Life is always fair (but it's not).",
        "keywords": ["fair", "unfair", "should", "deserve", "right", "wrong", "justice"],
        "reframe": "Is life always fair? What would help me accept this situation?"
    },
    "Blaming": {
        "definition": "Holding others responsible for pain OR blaming ourselves for everything.",
        "example": "Stop making me feel bad! OR This is all my fault.",
        "keywords": ["you made me", "your fault", "my fault", "blame", "responsible", "caused"],
        "reframe": "Who actually controls my emotions? What part can I influence?"
    },
    "Shoulds": {
        "definition": "Ironclad rules about how others/we should behave. Guilt when violated.",
        "example": "I should exercise. I shouldn't be so lazy.",
        "keywords": ["should", "shouldn't", "must", "ought", "have to", "need to"],
        "reframe": "What would happen if I dropped this rule? Is it flexible?"
    },
    "Emotional Reasoning": {
        "definition": "Believing what we feel must be true automatically. 'I feel it, therefore it's true.'",
        "example": "I feel stupid, so I must be stupid.",
        "keywords": ["I feel", "because I feel", "therefore", "must be", "obviously", "clearly"],
        "reframe": "Are feelings facts? What evidence contradicts this feeling?"
    },
    "Fallacy of Change": {
        "definition": "Expecting others to change if we pressure them enough. Happiness depends on them.",
        "example": "If I just push hard enough, they'll change.",
        "keywords": ["if they would", "if only they", "change them", "make them", "pressure"],
        "reframe": "Can I control their change? What can I control about my response?"
    },
    "Global Labeling": {
        "definition": "Generalizing one/two qualities into a negative global judgment. Mislabeling.",
        "example": "I'm a loser. He's a real jerk.",
        "keywords": ["loser", "jerk", "idiot", "worthless", "useless", "disappointment", "stupid"],
        "reframe": "Can I describe this more specifically without the label?"
    },
    "Always Being Right": {
        "definition": "Continually on trial to prove opinions/actions correct. Being wrong is unthinkable.",
        "example": "I'm going to win this argument no matter what.",
        "keywords": ["right", "wrong", "prove", "correct", "argument", "win", "defend"],
        "reframe": "Is being right more important than the relationship?"
    },
    "Heaven's Reward Fallacy": {
        "definition": "Expecting sacrifices to be rewarded. Resentment when they aren't.",
        "example": "I've done so much, I deserve recognition.",
        "keywords": ["deserve", "reward", "sacrifice", "earned", "owed", "after all I've done"],
        "reframe": "Can I find satisfaction in the action itself, not the reward?"
    }
}

# --- EMOTIONS QUICK-SELECT ---
EMOTIONS = [
    {"emoji": "😰", "label": "Anxious"},
    {"emoji": "😢", "label": "Sad"},
    {"emoji": "😠", "label": "Angry"},
    {"emoji": "😶", "label": "Numb"},
    {"emoji": "😔", "label": "Guilty"},
    {"emoji": "😨", "label": "Scared"},
    {"emoji": "😤", "label": "Frustrated"},
    {"emoji": "😞", "label": "Disappointed"},
    {"emoji": "😐", "label": "Neutral"},
    {"emoji": "😌", "label": "Calm"}
]

# --- SAFETY KEYWORDS ---
SAFETY_KEYWORDS = ["suicide", "kill myself", "end it", "die", "overdose", "hurt someone", "firearm", "gun", "cutting", "self-harm"]

# --- SESSION STATE ---
if 'session_started' not in st.session_state:
    st.session_state.session_started = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'consent_given' not in st.session_state:
    st.session_state.consent_given = False
if 'step' not in st.session_state:
    st.session_state.step = "landing"
if 'situation' not in st.session_state:
    st.session_state.situation = ""
if 'emotion' not in st.session_state:
    st.session_state.emotion = ""
if 'distortion' not in st.session_state:
    st.session_state.distortion = ""
if 'reframe' not in st.session_state:
    st.session_state.reframe = ""
if 'distress_pre' not in st.session_state:
    st.session_state.distress_pre = None
if 'distress_post' not in st.session_state:
    st.session_state.distress_post = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- FUNCTIONS ---

def check_safety(text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in SAFETY_KEYWORDS)

def classify_distortion_auto(text):
    text_lower = text.lower()
    scores = {}
    for dist_name, dist_data in COGNITIVE_DISTORTIONS.items():
        matches = sum(1 for kw in dist_data["keywords"] if kw in text_lower)
        scores[dist_name] = matches
    if max(scores.values()) == 0:
        return "None Identified"
    return max(scores, key=scores.get)

# --- APP LOGIC ---

def main():
    # 1. LANDING PAGE
    if st.session_state.step == "landing":
        st.title("🧠 ClearLogic Engine")
        st.subheader("Cognitive Behavioral Therapy (CBT) Support Tool")
        
        st.markdown("""
        ### What is CBT?
        
        Cognitive Behavioral Therapy helps us identify and change **unhelpful thinking patterns** 
        that contribute to emotional distress. By recognizing these patterns, we can develop 
        healthier, more balanced thoughts.
        
        ---
        
        ### 15 Common Cognitive Distortions
        
        """)
        
        # Display all 15 distortions in cards
        cols = st.columns(3)
        for idx, (dist_name, dist_data) in enumerate(COGNITIVE_DISTORTIONS.items()):
            col = cols[idx % 3]
            with col:
                with st.container():
                    st.markdown(f"""
                    <div class="distortion-card">
                        <strong>{dist_name}</strong><br>
                        <small>{dist_data['definition'][:60]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### Ready to work through a situation?")
        
        uid = st.text_input("Enter Username or Random Number:", placeholder="e.g., User_8472")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Session"):
                if uid:
                    st.session_state.user_id = f"ID_{hashlib.sha256(uid.encode()).hexdigest()[:8]}"
                    st.session_state.step = "consent"
                    st.rerun()
                else:
                    st.warning("Please enter an ID.")
        with col2:
            if st.button("Learn More About CBT"):
                st.info("This tool is based on evidence-based CBT principles. Not a replacement for therapy.")
        
        return

    # 2. CONSENT
    if st.session_state.step == "consent":
        st.title("Data Consent")
        st.markdown("""
        We collect **anonymous** data to validate the tool's effectiveness for underserved populations.
        
        - No names or emails stored
        - Data used for research only
        - You can delete your data anytime
        """)
        
        if st.checkbox("I consent to anonymous data collection"):
            st.session_state.consent_given = True
            st.session_state.step = "situation"
            st.rerun()
        return

    # 3. STEP 1: SITUATION
    if st.session_state.step == "situation":
        st.title("Step 1: Describe the Situation")
        st.markdown("What happened? Describe the event or thought that's bothering you.")
        
        situation = st.text_area("Situation:", height=100, placeholder="e.g., I made a mistake at work and my boss noticed...")
        
        if st.button("Next: How Do You Feel?"):
            if situation:
                if check_safety(situation):
                    st.error("⚠️ **Safety Alert**: I hear you are in crisis.")
                    st.markdown("**Call 988 or go to ER immediately.**")
                    return
                st.session_state.situation = situation
                st.session_state.step = "emotion"
                st.rerun()
            else:
                st.warning("Please describe the situation.")
        return

    # 4. STEP 2: EMOTION
    if st.session_state.step == "emotion":
        st.title("Step 2: Identify Your Emotion")
        st.markdown("How are you feeling right now? Select one or more:")
        
        cols = st.columns(5)
        selected_emotion = None
        for idx, emo in enumerate(EMOTIONS):
            col = cols[idx % 5]
            with col:
                if st.button(f"{emo['emoji']} {emo['label']}", key=f"emo_{idx}"):
                    selected_emotion = emo['label']
        
        if selected_emotion:
            st.session_state.emotion = selected_emotion
            st.session_state.step = "distortion"
            st.rerun()
        return

    # 5. STEP 3: DISTORTION
    if st.session_state.step == "distortion":
        st.title("Step 3: Identify the Cognitive Distortion")
        st.markdown(f"**Situation:** {st.session_state.situation}")
        st.markdown(f"**Emotion:** {st.session_state.emotion}")
        
        # Auto-detect
        auto_detected = classify_distortion_auto(st.session_state.situation)
        st.info(f"🤖 Auto-detected: **{auto_detected}**")
        
        # Manual selection
        dist_options = ["None Identified"] + list(COGNITIVE_DISTORTIONS.keys())
        selected_dist = st.selectbox("Which pattern matches best?", dist_options, key="dist_select")
        
        if st.button("Next: Create Healthier Thought"):
            st.session_state.distortion = selected_dist
            st.session_state.step = "reframe"
            st.rerun()
        return

    # 6. STEP 4: REFRAME
    if st.session_state.step == "reframe":
        st.title("Step 4: Create a Healthier Thought")
        st.markdown(f"**Distortion:** {st.session_state.distortion}")
        
        # Show reframe guidance based on distortion
        if st.session_state.distortion != "None Identified":
            dist_data = COGNITIVE_DISTORTIONS[st.session_state.distortion]
            st.markdown(f"""
            <div class="info-box">
                <strong>Definition:</strong> {dist_data['definition']}<br>
                <strong>Example:</strong> {dist_data['example']}<br>
                <strong>Try asking:</strong> {dist_data['reframe']}
            </div>
            """, unsafe_allow_html=True)
        
        new_thought = st.text_area("Write a more balanced thought:", height=100, 
                                    placeholder="e.g., I made a mistake, but I can learn from it...")
        
        if st.button("Next: Check-In"):
            if new_thought:
                st.session_state.reframe = new_thought
                st.session_state.step = "checkin"
                st.rerun()
            else:
                st.warning("Please write a healthier thought.")
        return

    # 7. STEP 5: CHECK-IN
    if st.session_state.step == "checkin":
        st.title("Step 5: Check-In")
        st.markdown("How do you feel now after working through this?")
        
        col1, col2 = st.columns(2)
        with col1:
            pre = st.slider("Distress Before", 0, 10, 8, key="pre_checkin")
        with col2:
            post = st.slider("Distress Now", 0, 10, 4, key="post_checkin")
        
        if st.button("Complete Session"):
            st.session_state.distress_pre = pre
            st.session_state.distress_post = post
            delta = pre - post
            
            # Session Summary
            st.success(f"✅ Session Complete!")
            st.markdown(f"""
            ### Summary
            - **Situation:** {st.session_state.situation[:50]}...
            - **Emotion:** {st.session_state.emotion}
            - **Distortion:** {st.session_state.distortion}
            - **Healthier Thought:** {st.session_state.reframe[:50]}...
            - **Distress:** {pre} → {post} (**{-delta} points**)
            """)
            
            # Reset for next session
            st.session_state.step = "situation"
            st.session_state.situation = ""
            st.session_state.emotion = ""
            st.session_state.distortion = ""
            st.session_state.reframe = ""
            st.session_state.distress_pre = None
            st.session_state.distress_post = None
            st.rerun()
        return

    # 8. ADMIN VIEW (Grant Data)
    with st.expander("🔒 Admin View: Grant Validation Data"):
        st.markdown("**Simulated T-Test Results**")
        data = pd.DataFrame({"Pre": [8, 7, 9, 6, 8], "Post": [4, 3, 5, 2, 4]})
        t_stat, p_val = stats.ttest_rel(data['Pre'], data['Post'])
        st.metric("Avg Reduction", f"{data['Pre'].mean() - data['Post'].mean():.1f}")
        st.metric("Significance (p-value)", f"{p_val:.4f}")
        if p_val < 0.05:
            st.success("✅ Statistically Significant Improvement")

if __name__ == "__main__":
    main()
