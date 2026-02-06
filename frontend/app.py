"""Streamlit frontend for the Virtual Department Representatives system."""

import requests
import streamlit as st

API_URL = "http://localhost:8000"

# ---- Page config ----
st.set_page_config(page_title="Virtual Representatives", page_icon="🏢", layout="wide")
st.title("🏢 Virtual Department Representatives")
st.caption("Ask any department representative a question based on your uploaded knowledge base.")

# ---- Fetch departments from the backend ----
@st.cache_data(ttl=60)
def fetch_departments():
    try:
        resp = requests.get(f"{API_URL}/departments", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None

departments = fetch_departments()

if departments is None:
    st.error("Cannot reach the backend API. Make sure the FastAPI server is running on http://localhost:8000")
    st.stop()

# ---- Sidebar: department selector + file upload + document list ----
with st.sidebar:
    st.header("Department")
    dept_names = [f"{d['icon']} {d['name']}" for d in departments]
    selected_label = st.radio("Choose a representative:", dept_names)
    # Extract the plain department name (strip icon)
    selected_dept = selected_label.split(" ", 1)[1]

    st.divider()

    # File upload
    st.header("Upload Document")
    uploaded_file = st.file_uploader(
        "Add to the knowledge base",
        type=["txt", "md", "pdf"],
        help="Upload meeting notes, reports, or any text document.",
    )
    if uploaded_file is not None:
        if st.button("Upload"):
            with st.spinner("Uploading..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    resp = requests.post(f"{API_URL}/upload/document", files=files, timeout=30)
                    resp.raise_for_status()
                    st.success(f"Uploaded: {uploaded_file.name}")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    st.divider()

    # Document list
    st.header("Documents")
    try:
        docs_resp = requests.get(f"{API_URL}/documents", timeout=5)
        docs_resp.raise_for_status()
        docs = docs_resp.json()
    except Exception:
        docs = []

    if not docs:
        st.info("No documents uploaded yet.")
    else:
        for doc in docs:
            with st.expander(doc["title"]):
                st.text(doc["content"][:500] + ("..." if len(doc["content"]) > 500 else ""))
                if st.button("Delete", key=f"del_{doc['id']}"):
                    requests.delete(f"{API_URL}/documents/{doc['id']}", timeout=5)
                    st.cache_data.clear()
                    st.rerun()

# ---- Initialize chat history per department ----
if "histories" not in st.session_state:
    st.session_state.histories = {}

if selected_dept not in st.session_state.histories:
    st.session_state.histories[selected_dept] = []

history = st.session_state.histories[selected_dept]

# ---- Display chat history ----
dept_info = next((d for d in departments if d["name"] == selected_dept), None)
st.subheader(f"{dept_info['icon']} {selected_dept} Representative" if dept_info else selected_dept)
st.caption(dept_info["description"] if dept_info else "")

for msg in history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---- Chat input ----
if prompt := st.chat_input("Ask the representative a question..."):
    # Show user message immediately
    history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call the backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "department": selected_dept,
                    "message": prompt,
                    "history": history[:-1],  # send prior turns as context
                }
                resp = requests.post(f"{API_URL}/chat", json=payload, timeout=120)
                resp.raise_for_status()
                reply = resp.json()["reply"]
            except requests.exceptions.ConnectionError:
                reply = "Cannot reach the backend API. Is it running?"
            except Exception as e:
                reply = f"Error: {e}"

        st.markdown(reply)

    history.append({"role": "assistant", "content": reply})
