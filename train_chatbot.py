from llama_index import (
    SimpleDirectoryReader,
    GPTSimpleVectorIndex,
    LLMPredictor,
    ServiceContext
)
from langchain import OpenAI
import gradio as gr
import os

os.environ["OPENAI_API_KEY"] = ''

def construct_index(directory_path):
    num_outputs = 512

    llm_predictor = LLMPredictor(
        llm=OpenAI(
            temperature=0.7,
            model_name="text-davinci-003",
            max_tokens=num_outputs
        )
    )

    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

    docs = SimpleDirectoryReader(directory_path).load_data()

    index = GPTSimpleVectorIndex.from_documents(
        docs, service_context=service_context
    )

    index.save_to_disk('index.json')

    return index


def chatbot_generator(input_text):
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    response = index.query(input_text, response_mode="compact")
    return response.response


def add_text(history, text):
    history = history + [(text, None)]
    return history, ""


def bot(history):
    response = chatbot_generator(history[-1][0])
    history[-1][1] = response
    return history


with gr.Blocks() as demo:
    chatbot = gr.Chatbot([], elem_id="chatbot").style(height=750)
    
    with gr.Row():
        # with gr.Column(scale=0.85):
        txt = gr.Textbox(
            show_label=False,
            placeholder="Ingresa tu pregunta",
        ).style(container=False)
        
    txt.submit(add_text, [chatbot, txt], [chatbot, txt]).then(
        bot, chatbot, chatbot
    )

if __name__ == "__main__":
    demo.launch()