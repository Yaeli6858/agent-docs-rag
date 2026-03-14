import gradio as gr

def create_ui(query_callback):
    """
    יוצר ממשק צ'אט בעזרת Gradio.
    query_callback: פונקציה שתקבל את השאלה ותחזיר תשובה מה-RAG.
    """
    
    with gr.Blocks(title="Agentic Docs Assistant") as demo:
        gr.Markdown("# 🤖 Agentic Coding Assistant")
        gr.Markdown("Ask anything about your technical decisions, rules, and tasks.")
        
        chatbot = gr.Chatbot(label="Chat History")
        msg = gr.Textbox(label="Your Question", placeholder="e.g., What is the main design color?")
        clear = gr.Button("Clear")

        def respond(message, chat_history):
            # כאן אנחנו קוראים למנוע ה-RAG שנבנה ב-core
            bot_message = query_callback(message)
            chat_history.append((message, bot_message))
            return "", chat_history

        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        clear.click(lambda: None, None, chatbot, queue=False)

    return demo

if __name__ == "__main__":
    # הרצה לבדיקה ויזואלית בלבד (מחזיר תשובה קבועה בינתיים)
    demo = create_ui(lambda q: f"I received your question: '{q}'. Waiting for Pinecone to be open!")
    demo.launch()