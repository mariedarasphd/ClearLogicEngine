"""ClearLogic Engine — original Phase I intervention library."""

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
