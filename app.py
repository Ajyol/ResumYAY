import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from resume_parser import parse_resume
from resume_evaluator import evaluate_resume

# Page configuration
st.set_page_config(
    page_title="AI Resume Grader",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar upload
st.sidebar.title("📄 AI Resume Grader")
st.sidebar.markdown("Upload a PDF resume and get instant AI-powered feedback.")
uploaded_file = st.sidebar.file_uploader("Choose your resume (PDF)", type=["pdf"])

if uploaded_file:
    # Parse and evaluate
    with st.spinner("🔍 Parsing resume..."):
        parsed = parse_resume(uploaded_file)
    with st.spinner("🤖 Evaluating resume..."):
        feedback = evaluate_resume(parsed)
    st.sidebar.success("✅ Analysis ready!")

    # Tabs for organization
    tabs = st.tabs(["Overview", "Parsed Data", "Metrics", "Evaluation"])

    # --- Overview Tab ---
    with tabs[0]:
        st.header("🏁 Overview")
        overall = feedback.get('overall_score', feedback.get('keyword_score', 0))
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=overall,
            title={'text': "Overall Resume Quality"},
            gauge={
                'axis': {'range': [0,100]},
                'steps': [
                    {'range': [0,60], 'color': '#FF4B4B'},
                    {'range': [60,80], 'color': '#FFA500'},
                    {'range': [80,100], 'color': '#4CAF50'}
                ],
                'bar': {'color': '#4CAF50' if overall > 75 else '#FFA500'}
            }
        ))
        st.plotly_chart(gauge, use_container_width=True)
        st.markdown(f"**Overall Score:** {overall:.2f}/100")

        metrics = parsed.get('resume_metrics', {})
        summary = parsed.get('summary', {})
        st.markdown(
            f"- **Word Count:** {metrics.get('word_count', 0)}  \
"
            f"- **Pages:** {metrics.get('estimated_pages', 0)}  \
"
            f"- **Readability:** {summary.get('readability_score', 'N/A')}"
        )

    # --- Parsed Data Tab ---
    with tabs[1]:
        st.header("📑 Parsed Data")
        # Contact Info
        contact = parsed.get('contact_information', {})
        st.subheader("Contact Information")
        st.write(pd.DataFrame.from_dict(contact, orient='index', columns=['Value']))

        # Professional Summary
        st.subheader("Professional Summary")
        st.write(parsed.get('professional_summary', 'N/A'))

        # Skills in two columns
        st.subheader("Skills")
        tech = parsed.get('skills', {}).get('technical_skills', [])
        soft = parsed.get('skills', {}).get('soft_skills', [])
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Technical Skills**")
            if tech:
                for skill in tech:
                    st.markdown(f"- {skill}")
            else:
                st.write("None")
        with col2:
            st.markdown("**Soft Skills**")
            if soft:
                for skill in soft:
                    st.markdown(f"- {skill}")
            else:
                st.write("None")

        # Education
        st.subheader("Education")
        for edu in parsed.get('education', []):
            st.markdown(f"- {edu.get('degree', '')} ({edu.get('year', '')})")

        # Experience
        st.subheader("Experience")
        exp = parsed.get('experience', {})
        st.markdown(f"- {exp.get('level', 'N/A')} ({exp.get('years', 0)} years)")

    # --- Metrics Tab ---
    with tabs[2]:
        st.header("📊 Resume Metrics")
        metrics = parsed.get('resume_metrics', {})
        df_metrics = pd.DataFrame({
            'Word Count': [metrics.get('word_count', 0)],
            'Sentence Count': [metrics.get('sentence_count', 0)],
            'Estimated Pages': [metrics.get('estimated_pages', 0)],
            'Avg Words/Sentence': [metrics.get('average_words_per_sentence', 0)]
        })
        bar = go.Figure([go.Bar(x=df_metrics.columns, y=df_metrics.iloc[0])])
        st.plotly_chart(bar, use_container_width=True)

        st.header("🔖 Section Presence")
        sections = parsed.get('sections_present', {})
        df_sec = pd.DataFrame({
            'Section': list(sections.keys()),
            'Present': [1 if v else 0 for v in sections.values()]
        })
        pie = go.Figure(go.Pie(labels=df_sec['Section'], values=df_sec['Present'], hole=0.4))
        st.plotly_chart(pie, use_container_width=True)

    # --- Evaluation Tab ---
    with tabs[3]:
        st.header("✨ Evaluation Breakdown")
        scores = {
            'Keyword Match (%)': feedback.get('keyword_score', 0),
            'TF-IDF Similarity (%)': feedback.get('similarity_score_tfidf', 0) * 100,
            'BERT Similarity (%)': feedback.get('similarity_score_bert', 0) * 100
        }
        df_scores = pd.DataFrame.from_dict(scores, orient='index', columns=['Score']).reset_index()
        df_scores.columns = ['Metric', 'Score']
        st.dataframe(df_scores)

        st.subheader("Keyword Analysis")
        st.markdown(
            f"**Matched Keywords:** {', '.join(feedback.get('matched_keywords', [])) or 'None'}"
        )
        st.markdown(
            f"**Missing Keywords:** {', '.join(feedback.get('missing_keywords', [])) or 'None'}"
        )

