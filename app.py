"""ClearLogic Phase I — Gradio interface for synthetic prototype testing."""
from pathlib import Path
from copy import deepcopy
import gradio as gr
from engine import GREETING, initialize_session, process_turn, get_phase, phase_label

CSS = """
.gradio-container {background:#0a192f !important; color:#fff !important;}
.gradio-container h1, .gradio-container h2, .gradio-container .prose {color:#fff;}
#clearlogic-header {border-bottom:2px solid #64ffda; padding-bottom:12px;}
"""

def new_session():
    state = initialize_session()
    return "", [{"role":"assistant", "content":GREETING}], state, summarize(state)


def summarize(state):
    if state['safety']['status'] != 'none':
        return '### Safety support active\nOrdinary coaching is suspended.'
    phase = get_phase(state)
    lines = [f'### Session progress\nStep {phase} of 7 — {phase_label(state)}']
    for key, label in [('initial_distress','Starting distress'), ('final_distress','Ending distress')]:
        if state[key] is not None:
            lines.append(f'{label}: {state[key]}/10')
    return '\n\n'.join(lines)


def submit(message, history, state):
    state = deepcopy(state or initialize_session())
    history = list(history or [])
    if not message or not message.strip():
        return '', history, state, summarize(state)
    result = process_turn(message, state)
    history.extend([{'role':'user','content':message}, {'role':'assistant','content':result['message']}])
    return '', history, state, summarize(state)


def clear_session():
    # Explicitly discard the entire local session, not a safety assessment.
    return new_session()


def build_app():
    with gr.Blocks(title='ClearLogic Engine', analytics_enabled=False) as demo:
        state = gr.State(value=initialize_session)
        with gr.Row(elem_id='clearlogic-header'):
            logo = Path(__file__).with_name('logo.png')
            if logo.exists():
                gr.Image(value=str(logo), show_label=False, interactive=False, height=125, scale=1, buttons=[])
            gr.Markdown('# ClearLogic Engine\nAgentic Cognitive Support · Phase I')
        gr.Markdown('**Experimental prototype — synthetic testing only.** Not a diagnostic, treatment or emergency-care service. Do not enter identifying or sensitive personal information.')
        with gr.Row():
            with gr.Column(scale=3):
                chat = gr.Chatbot(value=[{'role':'assistant','content':GREETING}], label='Cognitive support', height=440, sanitize_html=True)
                message = gr.Textbox(label='Message', placeholder='Enter a response...', lines=2)
                with gr.Row():
                    send = gr.Button('Send', variant='primary')
                    clear = gr.Button('Clear conversation / new session')
            with gr.Column(scale=1):
                progress = gr.Markdown(summarize(initialize_session()))
                gr.Markdown('Session data is held in application memory. Clearing the conversation discards this session state; hosting infrastructure may have separate logging policies. Clearing is not a safety assessment.')
        outputs = [message, chat, state, progress]
        send.click(submit, [message, chat, state], outputs, concurrency_limit=1)
        message.submit(submit, [message, chat, state], outputs, concurrency_limit=1)
        clear.click(clear_session, outputs=outputs, concurrency_limit=1)
    return demo


demo = build_app()
if __name__ == '__main__':
    demo.launch(theme=gr.themes.Base(primary_hue='teal', neutral_hue='slate', font=['Arial','sans-serif']).set(body_background_fill='#0a192f', body_background_fill_dark='#0a192f', body_text_color='#ffffff', body_text_color_dark='#ffffff', block_background_fill='#112240', block_background_fill_dark='#112240', block_label_text_color='#ffffff', block_label_text_color_dark='#ffffff', input_background_fill='#112240', input_background_fill_dark='#112240', input_text_color='#ffffff', input_text_color_dark='#ffffff'), css=CSS, share=False, show_error=False)
