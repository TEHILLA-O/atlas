"""Lightweight Streamlit UI. No business logic lives here."""

from __future__ import annotations

import os

import httpx
import streamlit as st

API = os.environ.get("ATLAS_API_URL", "http://localhost:8000")


st.set_page_config(page_title="Atlas", layout="wide")
st.title("Atlas")
st.caption("Agentic research, retrieval and decision intelligence — not a chatbot.")

query = st.text_area(
    "Research question",
    value=(
        "Analyse whether Acme Technology should enter the UK public-sector "
        "cybersecurity market. Identify market opportunity, barriers, "
        "procurement requirements, major competitors, risks and a recommended "
        "entry strategy."
    ),
    height=140,
)

col_a, col_b = st.columns(2)
with col_a:
    uploaded = st.file_uploader("Upload evidence documents", accept_multiple_files=True)
    if uploaded and st.button("Ingest documents"):
        for item in uploaded:
            files = {"file": (item.name, item.getvalue(), item.type or "text/plain")}
            response = httpx.post(f"{API}/documents", files=files, timeout=60)
            st.write(response.json())
with col_b:
    if st.button("Start research", type="primary"):
        response = httpx.post(f"{API}/research", json={"query": query}, timeout=180)
        st.session_state["result"] = response.json()

result = st.session_state.get("result")
if not result:
    st.info("Start a research run to see the plan, evidence, contradictions and report.")
    st.stop()

st.subheader("Status")
st.write(
    {
        "research_id": result.get("research_id"),
        "status": result.get("status"),
        "intent": result.get("intent"),
        "confidence": result.get("confidence_score"),
    }
)
st.subheader("Progress")
for item in result.get("progress", []):
    st.write(f"- {item}")

st.subheader("Plan")
st.json(result.get("research_plan") or [])

tabs = st.tabs(["Report", "Evidence", "Contradictions", "Confidence", "Sources"])
with tabs[0]:
    st.markdown(result.get("final_report") or "_No final report yet._")
with tabs[1]:
    st.json(result.get("evidence") or [])
with tabs[2]:
    st.json(result.get("contradictions") or [])
with tabs[3]:
    st.json(result.get("confidence") or {})
with tabs[4]:
    report = result.get("report") or {}
    st.json(report.get("sources") or [])

if result.get("interrupt_payload"):
    st.warning("Human review required")
    st.json(result["interrupt_payload"])
    decision = st.radio("Decision", ["approve", "request_more_research", "cancel"])
    if st.button("Resume"):
        resumed = httpx.post(
            f"{API}/research/{result['research_id']}/resume",
            json={"decision": decision},
            timeout=180,
        )
        st.session_state["result"] = resumed.json()
        st.rerun()
