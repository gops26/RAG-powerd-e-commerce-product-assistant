from answer import answer_question

import gradio as gr

def format_context(context):
    result = "<h2 style='color: #ff7800;'>Relevant Context</h2>\n\n"
    for doc in context:
        result += f"<span style='color: #ff7800;'>Source: {doc.metadata['source']}</span>\n\n"
        result += doc.page_content + "\n\n"
    return result


def chat(history):
    last_message = history[-1]["content"]
    prior = history[:-1]

    answer, context = answer_question(last_message, prior)
    history.append({"role": "assistant", "content": answer})
    return history, format_context(context)


def main():
    def put_message_chatbot(message, history):
        return "", history + [{"role": "user", "content":message}] 
    
    theme = gr.themes.Soft(font=["Roboto","sans-serif"])
    
    with gr.Blocks(title="Product Rag recommender", theme=theme) as ui:
        gr.Markdown("# Product RAG recommender, ask me about any product")

        with gr.Row():
            with gr.Column(scale=1):
                chatbot = gr.Chatbot(
                    label="conversation de product",
                    height=500, type="messages",
                    )
                
                message = gr.Textbox(
                    label="your queries here",
                    placeholder="Ask anything about any product",
                    show_label=False
                )

            with gr.Column(scale=1):
                context_display = gr.HTML(
                    value="<h2 style='color: #0d8b96;'>Relevant Context</h2>\n\n<p>Ask a question to see retrieved context here.</p>",
                    label="Retrieved Context",
                )

        message.submit(put_message_chatbot, [message, chatbot], [message, chatbot]).then(
            chat, [chatbot], [chatbot, context_display]
        )

    ui.launch()


main()