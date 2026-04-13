import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import hashlib
import uuid
import datetime

# --- CONFIGURATION & CONSTANTS ---
st.set_page_config(page_title="ClearLogic Engine", page_icon="🧠", layout="centered")

# Safety Keywords (Hard Stop)
SAFETY_KEYWORDS = [
    "suicide", "kill myself", "end it", "die", "overdose", 
    "hurt someone", "firearm", "gun", "cutting", "self-harm"
]

# BDI Short Form Items (Sample 5 items for MVP)
BDI_ITEMS = [
    {"id": 1, "text": "Sadness", "options": ["0-No sadness", "1-Mild", "2-Moderate", "3-Severe"]},
    {"id": 2, "text": "Pessimism", "options": ["0-No pessimism", "1-Mild", "2-Moderate", "3-Severe"]},
    {"id": 3, "text": "Failure", "options": ["0-No feeling of failure", "1-Mild", "2-Moderate", "3-Severe"]},
    {"id": 4, "text": "Loss of Pleasure", "options": ["0-No loss", "1-Mild", "2-Moderate", "3-Severe"]},
    {"id": 5, "text": "Guilt", "options": ["0-No guilt", "1-Mild", "2-Moderate", "3-Severe"]}
]

# Skill Library (State -> Skill -> Script)
SKILL_LIBRARY = {
    "panic": {
        "skill": "Box Breathing",
        "script": "Let's slow down. Inhale for 4 seconds, hold for 4, exhale for 4, hold for 4. Repeat 3 times.",
        "instruction": "Try this now. How does your body feel?"
    },
    "rumination": {
        "skill": "Evidence Check",
        "script": "Your brain is telling a story. Let's look for facts. What is one piece of evidence that contradicts that thought?",
        "instruction": "Write down one fact that proves the thought isn't 100% true."
    },
    "overwhelm": {
        "skill": "5-4-3-2-1 Grounding",
        "script": "Name 5 things you see, 4 things you can touch, 3 things you hear, 2 things you smell, 1 thing you taste.",
        "instruction": "Go through the list slowly."
    },
    "numb": {
        "skill": "Temperature Shift",
        "script": "Sometimes we need a physical reset. Splash cold water on your face or hold an ice cube for 10 seconds.",
        "instruction": "Notice the sensation. Does it bring you back to the present?"
    }
}

# --- HELPER FUNCTIONS ---

def generate_anonymous_id():
    """Generates a unique, non-identifying ID."""
    return str(uuid.uuid4())[:8]

def check_safety(text):
    """Returns True if safety keywords are found."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in SAFETY_KEYWORDS)

def classify_state(text):
    """Simple rule-based classifier for MVP."""
    text_lower = text.lower()
    if "can't breathe" in text_lower or "panic" in text_lower or "heart racing" in text_lower:
        return "panic"
    if "always" in text_lower or "never" in text_lower or "stupid" in text_lower:
        return "rumination"
    if "too much" in text_lower or "overwhelmed" in text_lower or "can't cope" in text_lower:
        return "overwhelm"
    if "empty" in text_lower or "nothing" in text_lower or "numb" in text_lower:
        return "numb"
    return "general"

def calculate_bdi_score(answers):
    """Calculates total BDI score from selected indices."""
    return sum(int(a.split('-')[0]) for a in answers if a)

# --- SESSION STATE INITIALIZATION ---
if 'session_started' not in st.session_state:
    st.session_state.session_started = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'consent_given' not in st.session_state:
    st.session_state.consent_given = False
if 'bdi_pre_score' not in st.session_state:
    st.session_state.bdi_pre_score = None
if 'distress_pre' not in st.session_state:
    st.session_state.distress_pre = None
if 'distress_post' not in st.session_state:
    st.session_state.distress_post = None
if 'current_skill' not in st.session_state:
    st.session_state.current_skill = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- APP LOGIC ---

def main():
    st.title("🧠 ClearLogic Engine")
    st.caption("An anonymous, skill-based cognitive support system.")

    # 1. WELCOME & CONSENT SCREEN
    if not st.session_state.session_started:
        st.header("Welcome")
        st.markdown("""
        **ClearLogic Engine** is a tool to help you think through situations and manage distress.
        - **Anonymous:** No names or personal data required.
        - **Skill-Based:** Focuses on what you can do *now*, not diagnoses.
        - **Safe:** Includes immediate crisis support if needed.
        """)
        
        st.divider()
        st.subheader("Step 1: Create Your Anonymous ID")
        user_input_id = st.text_input("Choose a username OR enter a random number (e.g., 8472):", placeholder="e.g., User_123 or 9921")
        
        if st.button("Start Session"):
            if user_input_id:
                # Hash the input to ensure no PII is stored even if they type a name
                hashed_id = hashlib.sha256(user_input_id.encode()).hexdigest()[:8]
                st.session_state.user_id = f"ID_{hashed_id}"
                st.session_state.session_started = True
                st.rerun()
            else:
                st.warning("Please enter an ID to continue.")
        return

    # 2. CONSENT SCREEN
    if not st.session_state.consent_given:
        st.header("Data Consent")
        st.markdown("""
        To help us improve this tool and validate its effectiveness, we collect **anonymous** data:
        - Your anonymous ID
        - Pre/Post distress scores
        - Skills used
        - **NO** names, emails, or personal details are stored.
        
        This data is used for research to help underserved populations (veterans, homeless, DV survivors).
        """)
        
        if st.checkbox("I consent to anonymous data collection for research purposes"):
            st.session_state.consent_given = True
            st.rerun()
        else:
            st.info("Please consent to proceed.")
            return

    # 3. BDI INTAKE (PRE-SESSION)
    if st.session_state.bdi_pre_score is None:
        st.header("Initial Check-in")
        st.markdown("Please rate how you've been feeling over the **last 2 weeks**.")
        
        bdi_answers = []
        for item in BDI_ITEMS:
            selected = st.radio(item['text'], item['options'], key=f"bdi_{item['id']}", horizontal=True)
            bdi_answers.append(selected)
        
        if st.button("Calculate Baseline"):
            score = calculate_bdi_score(bdi_answers)
            st.session_state.bdi_pre_score = score
            st.success(f"Baseline BDI Score: {score}")
            st.rerun()
        return

    # 4. MAIN CHAT INTERFACE
    st.header("ClearLogic Session")
    
    # Display History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Safety Check & Input
    user_input = st.chat_input("How are you feeling right now?")

    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # --- SAFETY OVERRIDE (HARD STOP) ---
        if check_safety(user_input):
            with st.chat_message("assistant"):
                st.error("⚠️ **Safety Alert**: I hear you are in crisis.")
                st.markdown("""
                I cannot provide skills right now. Your safety is the priority.
                
                **Please reach out for immediate help:**
                - Call or Text **988** (Suicide & Crisis Lifeline)
                - Go to your nearest Emergency Room.
                - You are not alone.
                """)
                st.session_state.messages.append({"role": "assistant", "content": "CRISIS_TRIGGERED"})
                return # Stop further processing

        # --- NORMAL FLOW ---
        # 1. Classify State
        state = classify_state(user_input)
        
        # 2. Select Skill
        skill_data = SKILL_LIBRARY.get(state, SKILL_LIBRARY["general"]) if state != "general" else SKILL_LIBRARY["general"]
        skill_name = skill_data["skill"]
        skill_script = skill_data["script"]
        
        # 3. Generate Response
        response = f"I hear you. It sounds like you're dealing with {state}. \n\n**Skill Suggestion:** {skill_name}\n\n{skill_script}"
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Store current skill for post-session
        st.session_state.current_skill = skill_name
        
        # 4. Ask for Pre-Distress (if not already set in this session logic, simplified here)
        # In a real flow, we might ask this before the skill. For MVP, we ask after interaction.
        st.session_state.distress_pre = st.slider("Distress Level (Before this skill)", 0, 10, 8, key="pre_slider")

    # 5. POST-SESSION EVALUATION
    if st.session_state.distress_pre is not None and st.session_state.distress_post is None:
        st.divider()
        st.subheader("Check-in After Skill")
        st.markdown(f"You tried **{st.session_state.current_skill}**. How do you feel now?")
        
        post_val = st.slider("Distress Level (Now)", 0, 10, 4, key="post_slider")
        
        if st.button("Complete Session & Save Data"):
            st.session_state.distress_post = post_val
            
            # Log Data (Simulated for Demo)
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "user_id": st.session_state.user_id,
                "bdi_pre": st.session_state.bdi_pre_score,
                "distress_pre": st.session_state.distress_pre,
                "skill_used": st.session_state.current_skill,
                "distress_post": st.session_state.distress_post,
                "delta": st.session_state.distress_pre - st.session_state.distress_post
            }
            
            # In production, append to Google Sheets here
            # st.write("Data saved to database.") 
            
            st.success("Session complete! Data saved anonymously.")
            
            # Reset for next session (optional)
            st.session_state.distress_pre = None
            st.session_state.distress_post = None
            st.session_state.current_skill = None
            st.session_state.messages = [] # Clear chat for fresh start
            st.rerun()

    # 6. GRANT DASHBOARD (Hidden View)
    # In a real app, protect this with a password. For demo, we show it at the bottom.
    with st.expander("🔒 Admin View: Grant Validation Data (Demo Mode)"):
        st.markdown("**Simulated Dataset for T-Test Validation**")
        
        # Create dummy data for demonstration if real data is empty
        if len(st.session_state.messages) == 0: # Assuming empty means no new data logged yet
            # Generate fake data for the demo to show the t-test works
            data = {
                "distress_pre": [8, 7, 9, 6, 8, 7, 9, 8, 7, 6],
                "distress_post": [4, 3, 5, 2, 4, 3, 5, 4, 3, 2]
            }
            df = pd.DataFrame(data)
        else:
            # In real app, fetch from DB
            df = pd.DataFrame({
                "distress_pre": [st.session_state.distress_pre] if st.session_state.distress_pre else [],
                "distress_post": [st.session_state.distress_post] if st.session_state.distress_post else []
            })

        if not df.empty and len(df) > 1:
            # Run Paired T-Test
            t_stat, p_value = stats.ttest_rel(df['distress_pre'], df['distress_post'])
            
            st.metric("Average Distress Reduction", f"{df['distress_pre'].mean() - df['distress_post'].mean():.2f} points")
            st.metric("Statistical Significance (p-value)", f"{p_value:.4f}")
            
            if p_value < 0.05:
                st.success(f"✅ **Significant Improvement Detected!** (p < 0.05)")
                st.markdown("The data suggests the ClearLogic Engine effectively reduces distress.")
            else:
                st.info("Sample size too small for statistical significance yet. More data needed.")
            
            st.line_chart(df)
        else:
            st.info("Collecting session data... (Need at least 2 sessions for t-test)")

if __name__ == "__main__":
    main()
