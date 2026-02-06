"""Streamlit frontend for the Virtual Department Representatives system."""

import json
import re

import plotly.graph_objects as go
import requests
import streamlit as st

API_URL = "http://localhost:8000"

# ---- Page config ----
st.set_page_config(page_title="Virtual Representatives", page_icon="🏢", layout="wide")

# ---- Dashboard styling ----
st.markdown("""
<style>
/* Compact typography inside dashboard bordered containers */
[data-testid="stVerticalBlockBorderWrapper"] p,
[data-testid="stVerticalBlockBorderWrapper"] li {
    font-size: 0.88rem;
    line-height: 1.4;
}
[data-testid="stVerticalBlockBorderWrapper"] h2 {
    font-size: 1rem;
    margin: 0 0 0.4rem 0;
    padding: 0;
}
[data-testid="stVerticalBlockBorderWrapper"] table {
    width: 100%;
    font-size: 0.82rem;
}
[data-testid="stVerticalBlockBorderWrapper"] th {
    font-weight: 600;
    opacity: 0.7;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
[data-testid="stVerticalBlockBorderWrapper"] th,
[data-testid="stVerticalBlockBorderWrapper"] td {
    padding: 3px 6px;
}
</style>
""", unsafe_allow_html=True)


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

        # ---- Render charts in compact cards ----
        try:
            charts = json.loads(dashboard.get("charts_json", "[]"))
        except (json.JSONDecodeError, TypeError):
            charts = []

        if charts:
            cols = st.columns(min(len(charts), 3))
            for idx, chart in enumerate(charts):
                with cols[idx % 3]:
                    chart_type = chart.get("type", "bar")
                    title = chart.get("title", "Chart")
                    labels = chart.get("labels", [])
                    values = chart.get("values", [])

                    if not labels or not values:
                        continue

                    if chart_type == "pie":
                        fig = go.Figure(data=[go.Pie(
                            labels=labels,
                            values=values,
                            hole=0.4,
                            textinfo="percent",
                            textfont_size=11,
                            hoverinfo="label+value+percent",
                        )])
                        fig.update_layout(
                            showlegend=True,
                            legend=dict(font=dict(size=9), orientation="h", y=-0.15),
                        )
                    else:
                        fig = go.Figure(data=[go.Bar(
                            x=labels,
                            y=values,
                            marker_color="#4A90D9",
                            marker_line_width=0,
                            text=values,
                            textposition="outside",
                            textfont_size=10,
                        )])
                        fig.update_layout(
                            showlegend=False,
                            xaxis=dict(tickfont=dict(size=9)),
                            yaxis=dict(tickfont=dict(size=9), showgrid=True, gridcolor="rgba(128,128,128,0.1)"),
                        )

                    fig.update_layout(
                        title=dict(text=title, font=dict(size=12)),
                        margin=dict(l=10, r=10, t=35, b=10),
                        height=240,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig, use_container_width=True)

        # ---- Render markdown sections as cards ----
        content = dashboard.get("content", "")
        # Split on ## headings into separate sections
        sections = re.split(r"(?=^## )", content, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        if sections:
            for row_start in range(0, len(sections), 2):
                row = sections[row_start : row_start + 2]
                cols = st.columns(len(row))
                for col, section in zip(cols, row):
                    with col:
                        with st.container(border=True):
                            st.markdown(section, unsafe_allow_html=True)
        else:
            st.markdown(content)
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
