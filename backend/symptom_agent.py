from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from backend.memory import save_symptom

llm = OllamaLLM(model="llama3.2:1b")

SYSTEM = """You are a celiac symptom tracking assistant.
- Help log symptoms: bloating, fatigue, brain fog, abdominal pain, nausea, diarrhea, rash
- Ask about severity (1-10) and timing relative to meals
- Identify patterns suggesting gluten exposure
- Always recommend seeing a doctor for severe symptoms

Context: {context}
History: {history}
User: {question}
Response:"""

prompt = PromptTemplate(template=SYSTEM, input_variables=["context", "history", "question"])

SYMPTOM_KEYWORDS = ["bloating", "fatigue", "pain", "brain fog", "nausea", "diarrhea", "rash", "cramping", "headache"]

def run(retriever, history: list, message: str, session_id: str) -> str:
    docs = retriever.invoke(message)
    context = "\n".join([d.page_content for d in docs])
    history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-4:]])
    
    # Auto-log any symptoms mentioned
    for kw in SYMPTOM_KEYWORDS:
        if kw in message.lower():
            save_symptom(session_id, kw)
    
    return llm.invoke(prompt.format(context=context, history=history_str, question=message))