import gradio as gr
from music_assistant.prompts import agent_prompt_tpl
from music_assistant.agent import MusicAgent

agent = MusicAgent(agent_prompt_tpl).get_agent()


def agent_response(message, history):
    return agent.chat(message).response


if __name__ == "__main__":
    demo = gr.ChatInterface(agent_response, type="messages")
    demo.launch()
