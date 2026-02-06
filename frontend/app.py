"""Streamlit frontend for the Virtual Department Representatives system."""

import requests
import streamlit as st

API_URL = "http://localhost:8000"

# ---- Page config ----
st.set_page_config(page_title="Virtual Representatives", page_icon="🏢", layout="wide")


# ---- Auth helpers ----

def handle_oauth_redirect():
    """Read ?token= from the URL after Google OAuth redirect and store it in session."""
    params = st.query_params
    if "token" in params:
        st.session_state["jwt_token"] = params["token"]
        st.query_params.clear()


def get_auth_headers() -> dict:
    """Return Authorization header dict for authenticated API calls."""
    token = st.session_state.get("jwt_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def check_login_status() -> dict | None:
    """Validate the stored JWT by calling /auth/me. Returns user dict or None."""
    token = st.session_state.get("jwt_token")
    if not token:
        return None
    try:
        resp = requests.get(f"{API_URL}/auth/me", headers=get_auth_headers(), timeout=5)
        if resp.status_code == 401:
            st.session_state.pop("jwt_token", None)
            return None
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def logout():
    """Clear the JWT from session state."""
    st.session_state.pop("jwt_token", None)
    st.session_state.pop("user_info", None)


# ---- Handle OAuth redirect (runs on every page load) ----
handle_oauth_redirect()

# ---- Check authentication ----
user_info = check_login_status()

if user_info is None:
    # ---- Login screen ----
    st.title("🏢 Virtual Department Representatives")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<h3 style='text-align: center;'>Welcome! Please sign in to continue.</h3>",
            unsafe_allow_html=True,
        )
        st.write("")

        # Fetch the Google OAuth URL from the backend
        if st.button("🔐 Sign in with Google", use_container_width=True, type="primary"):
            try:
                resp = requests.get(f"{API_URL}/auth/google/login", timeout=5)
                resp.raise_for_status()
                auth_url = resp.json()["authorization_url"]
                st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the backend API. Make sure the FastAPI server is running on http://localhost:8000")
            except Exception as e:
                st.error(f"Failed to start sign-in: {e}")

    st.stop()

# ---- User is authenticated – store info ----
st.session_state["user_info"] = user_info

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

# ---- Sidebar: user profile + department selector + file upload + document list ----
with st.sidebar:
    # User profile
    st.markdown(f"**{user_info['name']}**")
    st.caption(user_info["email"])
    if st.button("Logout"):
        logout()
        st.rerun()

    st.divider()

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
                    resp = requests.post(
                        f"{API_URL}/upload/document",
                        files=files,
                        headers=get_auth_headers(),
                        timeout=30,
                    )
                    if resp.status_code == 401:
                        logout()
                        st.rerun()
                    resp.raise_for_status()
                    st.success(f"Uploaded: {uploaded_file.name}")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    st.divider()

    # Document list
    st.header("Documents")
    try:
        docs_resp = requests.get(f"{API_URL}/documents", headers=get_auth_headers(), timeout=5)
        if docs_resp.status_code == 401:
            logout()
            st.rerun()
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
                    resp = requests.delete(
                        f"{API_URL}/documents/{doc['id']}",
                        headers=get_auth_headers(),
                        timeout=5,
                    )
                    if resp.status_code == 401:
                        logout()
                        st.rerun()
                    st.cache_data.clear()
                    st.rerun()

# ---- Department header ----
dept_info = next((d for d in departments if d["name"] == selected_dept), None)
st.subheader(f"{dept_info['icon']} {selected_dept} Representative" if dept_info else selected_dept)
st.caption(dept_info["description"] if dept_info else "")

# ---- Tabbed interface: Dashboard (default) | Chat ----
tab_dashboard, tab_chat = st.tabs(["Dashboard", "Chat"])

# =============== DASHBOARD TAB ===============
with tab_dashboard:

    def fetch_dashboard(dept: str) -> dict | None:
        """Fetch (or generate) today's dashboard snapshot from the API."""
        try:
            resp = requests.get(
                f"{API_URL}/dashboard/{dept}",
                headers=get_auth_headers(),
                timeout=180,  # generation can take a while
            )
            if resp.status_code == 401:
                logout()
                st.rerun()
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    # Cache dashboard in session state so we don't re-fetch on every interaction
    dash_key = f"dashboard_{selected_dept}"
    if dash_key not in st.session_state:
        with st.spinner("Generating dashboard — this may take a moment on first load..."):
            st.session_state[dash_key] = fetch_dashboard(selected_dept)

    dashboard = st.session_state[dash_key]

    # Regenerate button
    if st.button("Regenerate Dashboard", key=f"regen_{selected_dept}"):
        with st.spinner("Regenerating dashboard..."):
            try:
                resp = requests.post(
                    f"{API_URL}/dashboard/{selected_dept}/regenerate",
                    headers=get_auth_headers(),
                    timeout=180,
                )
                if resp.status_code == 401:
                    logout()
                    st.rerun()
                resp.raise_for_status()
                st.session_state[dash_key] = resp.json()
                st.rerun()
            except Exception as e:
                st.error(f"Failed to regenerate dashboard: {e}")

    if dashboard:
        st.caption(f"Generated: {dashboard['generated_at'][:16].replace('T', ' ')}")
        st.markdown(dashboard["content"])
    else:
        st.warning("Could not load the dashboard. Is the backend running and Ollama available?")

# =============== CHAT TAB ===============
with tab_chat:
    # Load chat history from backend per department
    if "histories" not in st.session_state:
        st.session_state.histories = {}

    if selected_dept not in st.session_state.histories:
        try:
            hist_resp = requests.get(
                f"{API_URL}/chat/history",
                params={"department": selected_dept},
                headers=get_auth_headers(),
                timeout=5,
            )
            if hist_resp.status_code == 401:
                logout()
                st.rerun()
            hist_resp.raise_for_status()
            st.session_state.histories[selected_dept] = hist_resp.json()
        except Exception:
            st.session_state.histories[selected_dept] = []

    history = st.session_state.histories[selected_dept]

    # Clear history button
    if history and st.button("Clear History", key=f"clear_{selected_dept}"):
        try:
            requests.delete(
                f"{API_URL}/chat/history",
                params={"department": selected_dept},
                headers=get_auth_headers(),
                timeout=5,
            )
        except Exception:
            pass
        st.session_state.histories[selected_dept] = []
        st.rerun()

    # Display chat messages
    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask the representative a question..."):
        history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    payload = {
                        "department": selected_dept,
                        "message": prompt,
                        "history": history[:-1],
                    }
                    resp = requests.post(
                        f"{API_URL}/chat",
                        json=payload,
                        headers=get_auth_headers(),
                        timeout=120,
                    )
                    if resp.status_code == 401:
                        logout()
                        st.rerun()
                    resp.raise_for_status()
                    reply = resp.json()["reply"]
                except requests.exceptions.ConnectionError:
                    reply = "Cannot reach the backend API. Is it running?"
                except Exception as e:
                    reply = f"Error: {e}"

            st.markdown(reply)

        history.append({"role": "assistant", "content": reply})
