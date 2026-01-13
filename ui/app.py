import streamlit as st
import uuid
import requests

BASE_URL = "http://127.0.0.1:8000/"


def upload_file(uploaded_file):
    try:
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
        }
        api_url = BASE_URL + "api/pdf/upload"
        response = requests.post(api_url, files=files)

        if response.status_code == 200:
            st.success("File processed successfully!")
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        st.error(f"Connection failed: {e}")
    return None


def display_compliance_results(compliance_list):
    st.markdown(f"### Contract Compliance: {st.session_state.filename}")
    st.divider()

    for i, item in enumerate(compliance_list):
        if item["compliance_state"] == "fully_compliant":
            state_label = "COMPLIANT"
            status_color = "green"
        elif item["compliance_state"] == "partially_compliant":
            state_label = "PARTIALLY COMPLIANT"
            status_color = "orange"
        else:
            state_label = "NON-COMPLIANT"
            status_color = "red"

        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(item["compliance_requirement"])
                st.markdown(f"**STATUS:** :{status_color}[{state_label}]")
            with col2:
                st.metric(label="Confidence Score", value=f"{item['confidence']}%")

            st.markdown("**Executive Summary**")
            st.write(item["rationale"])

            with st.expander("Relevant Quotes"):
                for quote in item["relevant_quotes"]:
                    st.markdown(
                        f"""<div style="border-left: 2px solid #d1d1d1; padding-left: 15px; margin-bottom: 10px; color: #555;">
                        {quote}
                        </div>""",
                        unsafe_allow_html=True,
                    )


def llm_stream(question, filename):
    try:
        params = {"uuid": str(uuid.uuid4()), "question": question, "filename": filename}
        headers = {"accept": "application/json"}
        with requests.post(
            BASE_URL + "api/question/ask", params=params, headers=headers, stream=True
        ) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    yield chunk

    except requests.exceptions.RequestException as e:
        print(f"Streaming error: {e}")
        yield "Something went wrong. Please try again later."


def reset_app():
    st.session_state.clear()


# Session state initialization
if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False

if "objects" not in st.session_state:
    st.session_state.objects = []

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("PDF Ana")

# Upload screen
if not st.session_state.pdf_uploaded:
    st.subheader("Upload a PDF to begin")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        with st.spinner("Processing PDF..."):
            compliance_ratings = upload_file(uploaded_file)
            if compliance_ratings:
                st.session_state.objects = compliance_ratings
                st.session_state.pdf_uploaded = True
                st.session_state.filename = uploaded_file.name
        st.rerun()

# Chat Screen
else:
    st.button("🔄 Reset", on_click=reset_app)
    display_compliance_results(st.session_state.objects)
    st.divider()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a question about the PDF")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            streamed_text = ""

            for token in llm_stream(user_input, st.session_state.filename):
                streamed_text += token
                response_placeholder.markdown(streamed_text)

        st.session_state.messages.append(
            {"role": "assistant", "content": streamed_text}
        )
