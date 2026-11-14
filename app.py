"""
SkillPath AI - Main Streamlit Application Dashboard.

An AI-powered personalized learning platform that integrates:
- Student Profile management
- Skill Gap Analysis Agent (using Gemini)
- Career Matching Agent (using Gemini)
- Learning Recommendation Agent (using Gemini)
- Real Progress Tracking (with Supabase & session persistence)
- Context-aware Gemini AI Mentor
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List

# Internal project modules
from utils.helpers import load_css, format_progress_percentage
from database.supabase_client import SupabaseService
from agents import (
    SkillGapAgent,
    CareerAgent,
    RecommendationAgent,
    ProgressAgent,
    MentorAgent
)

# ---------------------------------------------------------
# 1. Page Configuration & Theme Injection
# ---------------------------------------------------------
st.set_page_config(
    page_title="SkillPath AI - Personalized Career Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
css_content = load_css("assets/style.css")
if css_content:
    st.markdown(css_content, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Session State Initialization
# ---------------------------------------------------------
if "student_profile" not in st.session_state:
    st.session_state.student_profile = {
        "name": "Alex Mercer",
        "email": "alex.mercer@example.com",
        "education": "B.Tech in Computer Science",
        "target_career": "Full Stack Developer",
        "skills": [
            {"skill": "HTML/CSS", "level": "Intermediate"},
            {"skill": "JavaScript", "level": "Intermediate"},
            {"skill": "Python", "level": "Beginner"},
            {"skill": "SQL", "level": "Beginner"}
        ]
    }

if "skill_gap_result" not in st.session_state:
    st.session_state.skill_gap_result = None

if "career_matches" not in st.session_state:
    st.session_state.career_matches = None

if "roadmap_data" not in st.session_state:
    st.session_state.roadmap_data = None

if "completed_task_ids" not in st.session_state:
    st.session_state.completed_task_ids = set()

if "mentor_messages" not in st.session_state:
    st.session_state.mentor_messages = [
        {
            "role": "assistant",
            "content": "👋 Hi there! I'm your **SkillPath AI Mentor**. Ask me anything about mastering new skills, debugging code, or preparing for technical interviews!"
        }
    ]

if "ai_progress_feedback" not in st.session_state:
    st.session_state.ai_progress_feedback = None

# Initialize Database Service & Agents
supabase_service = SupabaseService()
skill_gap_agent = SkillGapAgent()
career_agent = CareerAgent()
recommendation_agent = RecommendationAgent()
progress_agent = ProgressAgent()
mentor_agent = MentorAgent()

# ---------------------------------------------------------
# 3. Sidebar Navigation & Diagnostics
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎓 SkillPath AI")
    st.caption("AI-Powered Personalized Upskilling")

    # Current Student Mini-Badge
    current_name = st.session_state.student_profile.get("name", "Student")
    current_target = st.session_state.student_profile.get("target_career", "Undecided")
    st.markdown(f"""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px; border-radius: 8px; margin-bottom: 15px;">
        <span style="font-size: 0.8rem; color: #64748B; font-weight: 600;">ACTIVE LEARNER</span>
        <div style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">{current_name}</div>
        <div style="font-size: 0.85rem; color: #4F46E5; font-weight: 500;">🎯 {current_target}</div>
    </div>
    """, unsafe_allow_html=True)

    menu_option = st.radio(
        "Platform Modules",
        [
            "👤 Student Profile",
            "🎯 Skill Gap Analyzer",
            "💼 Career Matching",
            "🗺️ Learning Roadmap",
            "📊 Progress Tracker",
            "💬 Gemini AI Mentor"
        ],
        index=0
    )

    st.markdown("---")
    st.subheader("System Health")

    # Check live services
    gemini_healthy = True
    try:
        from utils.helpers import get_gemini_client
        gemini_healthy = get_gemini_client() is not None
    except Exception:
        gemini_healthy = False

    db_info = supabase_service.test_connection()
    db_healthy = db_info.get("connected", False)

    st.write(f"**Gemini 3.1 API:** {'🟢 Active' if gemini_healthy else '🔴 Error'}")
    st.write(f"**Supabase PostgreSQL:** {'🟢 Active' if db_healthy else '🔴 Offline'}")
    st.caption("Anon Key Authentication • RLS Active")

# ---------------------------------------------------------
# 4. Helper Charts
# ---------------------------------------------------------
def render_readiness_gauge(score: int):
    """Renders a Plotly Gauge meter for career readiness."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Career Readiness Score", 'font': {'size': 20, 'color': '#0F172A'}},
        number={'suffix': "%", 'font': {'size': 36, 'color': '#4F46E5', 'weight': 'bold'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
            'bar': {'color': "#4F46E5"},
            'bgcolor': "#F1F5F9",
            'borderwidth': 1,
            'bordercolor': "#CBD5E1",
            'steps': [
                {'range': [0, 40], 'color': '#FEE2E2'},
                {'range': [40, 70], 'color': '#FEF3C7'},
                {'range': [70, 100], 'color': '#DCFCE7'}
            ]
        }
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
    return fig


# ---------------------------------------------------------
# 5. Module 1: Student Profile
# ---------------------------------------------------------
if menu_option == "👤 Student Profile":
    st.markdown('<h1 class="main-title">Student Profile & Skill Inventory 👤</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Set up your educational background, target career path, and existing competencies.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("1. General Information")
        with st.form("profile_form"):
            name = st.text_input("Full Name", value=st.session_state.student_profile.get("name", ""))
            email = st.text_input("Email Address", value=st.session_state.student_profile.get("email", ""))
            education = st.selectbox(
                "Education Background",
                [
                    "B.Tech / B.E. in Computer Science",
                    "B.S. in Information Technology",
                    "Self-Taught Programmer",
                    "Coding Bootcamp Graduate",
                    "Master's Degree (M.Tech / M.S.)",
                    "High School / Undergraduate Beginner",
                    "Other Non-CS Degree"
                ],
                index=0
            )
            target_career = st.text_input(
                "Target Career Goal",
                value=st.session_state.student_profile.get("target_career", "")
            )

            save_submitted = st.form_submit_button("💾 Save Profile Changes", use_container_width=True)

        if save_submitted:
            st.session_state.student_profile["name"] = name
            st.session_state.student_profile["email"] = email
            st.session_state.student_profile["education"] = education
            st.session_state.student_profile["target_career"] = target_career

            # Attempt to record to existing Supabase table 'learners'
            save_resp = supabase_service.save_learner_profile(name, email, education)
            if save_resp.get("success"):
                st.success("✅ Profile successfully saved to Supabase database!")
            elif save_resp.get("permission_error"):
                st.warning(
                    f"ℹ️ **Database Notice:** {save_resp.get('message')}\n\n"
                    "Your profile is active in this session. (Row-Level Security enforces read/write policies)."
                )
            else:
                st.info(f"Session updated. {save_resp.get('message')}")

    with col2:
        st.subheader("2. Existing Skills & Proficiency")

        # Form to add a new skill
        with st.form("add_skill_form", clear_on_submit=True):
            skill_cols = st.columns([2, 1])
            with skill_cols[0]:
                new_skill_name = st.text_input("Skill / Tool Name", placeholder="e.g. Python, Docker, SQL")
            with skill_cols[1]:
                new_skill_level = st.selectbox("Proficiency", ["Beginner", "Intermediate", "Advanced"])

            add_skill_btn = st.form_submit_button("➕ Add Skill", use_container_width=True)

        if add_skill_btn and new_skill_name.strip():
            # Check for duplicate
            existing_names = [s["skill"].lower() for s in st.session_state.student_profile["skills"]]
            if new_skill_name.strip().lower() not in existing_names:
                st.session_state.student_profile["skills"].append({
                    "skill": new_skill_name.strip(),
                    "level": new_skill_level
                })
                st.success(f"Added {new_skill_name} ({new_skill_level})")
                st.rerun()

        # Display current skills list
        skills_list = st.session_state.student_profile.get("skills", [])
        st.write(f"**Current Skills Inventory ({len(skills_list)}):**")

        if not skills_list:
            st.info("No skills added yet. Add a few skills to begin gap analysis.")
        else:
            for i, item in enumerate(skills_list):
                lvl = item.get("level", "Beginner")
                badge_class = "badge-success" if lvl == "Advanced" else ("badge-primary" if lvl == "Intermediate" else "badge-warning")

                row_cols = st.columns([3, 1, 1])
                row_cols[0].markdown(f"**{item.get('skill')}**")
                row_cols[1].markdown(f'<span class="badge {badge_class}">{lvl}</span>', unsafe_allow_html=True)
                if row_cols[2].button("🗑️", key=f"del_{i}", help="Remove skill"):
                    st.session_state.student_profile["skills"].pop(i)
                    st.rerun()


# ---------------------------------------------------------
# 6. Module 2: Skill Gap Analyzer
# ---------------------------------------------------------
elif menu_option == "🎯 Skill Gap Analyzer":
    st.markdown('<h1 class="main-title">Skill Gap Analysis Agent 🎯</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">AI comparison of your skills against 2026 industry standards for your target role.</p>', unsafe_allow_html=True)

    profile = st.session_state.student_profile
    target = profile.get("target_career", "")
    skills = profile.get("skills", [])

    st.markdown(f"""
    <div class="card">
        <div class="card-title">Target Goal: <strong>{target}</strong></div>
        <div class="card-desc">Analyzing profile of <strong>{profile.get('name')}</strong> with <strong>{len(skills)} declared skills</strong>.</div>
    </div>
    """, unsafe_allow_html=True)

    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button("🚀 Run Live Skill Gap Analysis", type="primary", use_container_width=True):
            with st.spinner("Gemini is analyzing market requirements and comparing competencies..."):
                try:
                    result = skill_gap_agent.analyze_gap(
                        student_name=profile.get("name", "Student"),
                        education=profile.get("education", ""),
                        target_career=target,
                        skills_with_levels=skills
                    )
                    st.session_state.skill_gap_result = result
                    st.success("Skill gap analysis complete!")
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    # Display Results if available
    gap_data = st.session_state.skill_gap_result
    if gap_data:
        st.markdown("---")
        score_col, summary_col = st.columns([1, 2])

        with score_col:
            st.plotly_chart(render_readiness_gauge(gap_data.get("readiness_score", 50)), use_container_width=True)

        with summary_col:
            st.markdown("### Executive Strategic Summary")
            st.markdown(f"""
            <div class="card">
                <p style="font-size: 1.05rem; line-height: 1.6; color: #1E293B;">
                    {gap_data.get("executive_summary", "")}
                </p>
                <div style="margin-top: 10px; font-size: 0.9rem; color: #64748B;">
                    <strong>Role Overview:</strong> {gap_data.get("target_career_overview", "")}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Matched vs Missing Skills
        m_col1, m_col2 = st.columns(2, gap="medium")

        with m_col1:
            st.markdown("### ✅ Verified Strengths")
            matched = gap_data.get("matched_skills", [])
            if matched:
                for item in matched:
                    st.markdown(f"""
                    <div style="background-color: #F0FDF4; border-left: 4px solid #16A34A; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                        <strong style="color: #166534;">{item.get('skill')}</strong>
                        <span class="badge badge-success" style="float: right;">{item.get('current_level', 'Verified')}</span>
                        <div style="font-size: 0.85rem; color: #15803D; margin-top: 4px;">{item.get('feedback', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No matching skills found yet for this target career.")

        with m_col2:
            st.markdown("### ⚠️ Critical Missing Competencies")
            missing = gap_data.get("missing_skills", [])
            if missing:
                for item in missing:
                    imp = item.get("importance", "High")
                    badge_cls = "badge-danger" if imp == "Critical" else ("badge-warning" if imp == "High" else "badge-primary")
                    st.markdown(f"""
                    <div style="background-color: #FFF7ED; border-left: 4px solid #EA580C; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                        <strong style="color: #9A3412;">{item.get('skill')}</strong>
                        <span class="badge {badge_cls}" style="float: right;">{imp}</span>
                        <div style="font-size: 0.85rem; color: #7C2D12; margin-top: 4px;">{item.get('reason', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No missing foundational skills identified!")

        # Priority Focus Areas
        priorities = gap_data.get("priority_focus_areas", [])
        if priorities:
            st.markdown("### 🎯 Immediate Priority Focus")
            p_cols = st.columns(len(priorities))
            for idx, p in enumerate(priorities):
                with p_cols[idx]:
                    st.markdown(f"""
                    <div class="card" style="text-align: center; border-top: 3px solid #4F46E5;">
                        <div style="font-size: 0.8rem; font-weight: 700; color: #4F46E5;">PRIORITY {idx + 1}</div>
                        <div style="font-weight: 600; margin-top: 5px; color: #0F172A;">{p}</div>
                    </div>
                    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# 7. Module 3: Career Matching Agent
# ---------------------------------------------------------
elif menu_option == "💼 Career Matching":
    st.markdown('<h1 class="main-title">Career Matching Agent 💼</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Discover top industry career roles aligned with your existing technical competencies.</p>', unsafe_allow_html=True)

    profile = st.session_state.student_profile
    skills = profile.get("skills", [])

    st.write(f"Analyzing matches based on your **{len(skills)} registered skills** and education background: *{profile.get('education')}*.")

    if st.button("🔍 Find Matching Careers for My Skills", type="primary"):
        with st.spinner("Gemini is matching your skillset against current market demand..."):
            try:
                matches = career_agent.match_careers(
                    education=profile.get("education", ""),
                    skills_with_levels=skills
                )
                st.session_state.career_matches = matches
                st.success("Career recommendations generated!")
            except Exception as e:
                st.error(f"Career matching failed: {e}")

    career_data = st.session_state.career_matches
    if career_data:
        st.markdown("---")
        st.subheader("Top Recommended Career Matches")

        for i, match in enumerate(career_data):
            match_pct = match.get("match_percentage", 70)
            role_title = match.get("role_title", "Software Specialist")

            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="card-title" style="margin: 0; font-size: 1.25rem;">{role_title}</div>
                        <span class="badge badge-primary" style="font-size: 0.9rem;">{match_pct}% Match</span>
                    </div>
                    <div style="margin: 10px 0;">
                        <div style="background-color: #EEF2FF; border-radius: 9999px; height: 8px; width: 100%;">
                            <div style="background-color: #4F46E5; width: {match_pct}%; height: 8px; border-radius: 9999px;"></div>
                        </div>
                    </div>
                    <p class="card-desc">{match.get('why_good_fit', '')}</p>
                    <div style="margin-top: 10px;">
                        <div style="font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 4px;">Strengths Utilized:</div>
                        {''.join(f'<span class="skill-tag" style="background-color: #DCFCE7; color: #166534;">{s}</span>' for s in match.get('key_strengths_utilized', []))}
                    </div>
                    <div style="margin-top: 8px;">
                        <div style="font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 4px;">Skills to Bridge:</div>
                        {''.join(f'<span class="skill-tag" style="background-color: #FEF3C7; color: #92400E;">{s}</span>' for s in match.get('skills_to_bridge', []))}
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 12px; font-size: 0.85rem; color: #64748B;">
                        <span>📈 Demand: <strong>{match.get('market_demand', 'High')}</strong></span>
                        <span>⏱️ Estimated Transition: <strong>{match.get('estimated_timeline', '8-12 weeks')}</strong></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"🎯 Set '{role_title}' as My Target Career", key=f"adopt_role_{i}"):
                    st.session_state.student_profile["target_career"] = role_title
                    st.success(f"Updated your target career to {role_title}! Head to the Skill Gap Analyzer or Roadmap.")
                    st.rerun()


# ---------------------------------------------------------
# 8. Module 4: Learning Recommendation Agent
# ---------------------------------------------------------
elif menu_option == "🗺️ Learning Roadmap":
    st.markdown('<h1 class="main-title">Personalized Learning Roadmap 🗺️</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Step-by-step milestone curriculum generated by Gemini based on your specific missing competencies.</p>', unsafe_allow_html=True)

    profile = st.session_state.student_profile
    target = profile.get("target_career", "Full Stack Developer")

    # Retrieve missing skills from gap result if exists
    missing_skills = []
    if st.session_state.skill_gap_result:
        missing_skills = st.session_state.skill_gap_result.get("missing_skills", [])

    st.markdown(f"""
    <div class="card">
        <div class="card-title">Curriculum for: <strong>{target}</strong></div>
        <div class="card-desc">Addressing identified gaps with phased tasks and curated resources.</div>
    </div>
    """, unsafe_allow_html=True)

    cfg_col1, cfg_col2 = st.columns(2)
    with cfg_col1:
        hours = st.slider("Weekly Commitment (Hours/Week)", min_value=5, max_value=40, value=10, step=5)
    with cfg_col2:
        style = st.selectbox(
            "Preferred Learning Style",
            ["Hands-on projects & documentation", "Video tutorials & guided exercises", "Academic & theoretical depth"]
        )

    if st.button("⚡ Generate Personalized Learning Roadmap", type="primary"):
        with st.spinner("Gemini is designing your structured multi-phase curriculum..."):
            try:
                roadmap = recommendation_agent.generate_roadmap(
                    student_name=profile.get("name", "Student"),
                    target_career=target,
                    missing_skills=missing_skills,
                    hours_per_week=hours,
                    learning_style=style
                )
                st.session_state.roadmap_data = roadmap
                st.success("Personalized roadmap generated!")
            except Exception as e:
                st.error(f"Failed to create roadmap: {e}")

    roadmap = st.session_state.roadmap_data
    if roadmap:
        st.markdown("---")
        st.markdown(f"### 📋 {roadmap.get('roadmap_title', 'Curriculum')}")
        st.caption(f"⏱️ Estimated Duration: **{roadmap.get('total_estimated_weeks', 8)} Weeks** | Total Time: **{roadmap.get('estimated_total_hours', 50)} Hours**")

        for p_idx, phase in enumerate(roadmap.get("phases", [])):
            with st.expander(f"📍 {phase.get('phase_name', f'Phase {p_idx+1}')} — *{phase.get('goal', '')}*", expanded=True):
                for task in phase.get("tasks", []):
                    tid = task.get("task_id", f"task_{p_idx}")
                    is_done = tid in st.session_state.completed_task_ids

                    t_col1, t_col2 = st.columns([4, 1])

                    with t_col1:
                        st.markdown(f"#### {'✅' if is_done else '📌'} {task.get('title')}")
                        st.markdown(f"**Target Skill:** `{task.get('target_skill', '')}` • **Effort:** `{task.get('estimated_hours', 4)} hours`")
                        st.write(task.get("description", ""))

                        resources = task.get("resources", [])
                        if resources:
                            st.write("**Curated Resources:**")
                            res_html = "".join([
                                f'<span class="skill-tag" style="background-color: #EFF6FF; color: #1D4ED8;">🔗 {r.get("title")} ({r.get("type", "Doc")})</span>'
                                for r in resources
                            ])
                            st.markdown(res_html, unsafe_allow_html=True)

                    with t_col2:
                        toggle_label = "Completed" if is_done else "Mark Done"
                        if st.button(toggle_label, key=f"btn_toggle_{tid}", type="secondary" if is_done else "primary"):
                            if is_done:
                                st.session_state.completed_task_ids.remove(tid)
                            else:
                                st.session_state.completed_task_ids.add(tid)
                            # Attempt persistence to Supabase
                            supabase_service.record_progress(
                                profile.get("email", ""),
                                list(st.session_state.completed_task_ids)
                            )
                            st.rerun()

                    st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px dashed #E2E8F0;'/>", unsafe_allow_html=True)


# ---------------------------------------------------------
# 9. Module 5: Progress Tracker
# ---------------------------------------------------------
elif menu_option == "📊 Progress Tracker":
    st.markdown('<h1 class="main-title">Progress & Milestone Tracking 📊</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Real-time completion metrics backed by Supabase and verified by Gemini evaluation.</p>', unsafe_allow_html=True)

    roadmap = st.session_state.roadmap_data
    if not roadmap:
        st.info("💡 You haven't generated a Learning Roadmap yet. Head to **'Learning Roadmap'** to create your plan first!")
    else:
        # Extract all tasks from roadmap
        all_tasks = []
        for phase in roadmap.get("phases", []):
            for t in phase.get("tasks", []):
                all_tasks.append(t)

        completed_set = st.session_state.completed_task_ids
        stats = progress_agent.calculate_progress(all_tasks, completed_set)

        # Metric Tiles
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tasks Completed", f"{stats['completed_count']} / {stats['total_tasks']}")
        m2.metric("Overall Completion", f"{stats['percentage']}%")
        m3.metric("Hours Invested", f"{stats['completed_hours']} hrs")
        m4.metric("Hours Remaining", f"{stats['remaining_hours']} hrs")

        st.progress(stats["percentage"] / 100.0)

        # Visualization & Interactive Task List
        chart_col, list_col = st.columns([1, 1], gap="large")

        with chart_col:
            st.subheader("Progress Breakdown")
            donut_fig = go.Figure(data=[go.Pie(
                labels=["Completed Tasks", "Remaining Tasks"],
                values=[stats["completed_count"], stats["remaining_count"]],
                hole=0.6,
                marker_colors=["#10B981", "#E2E8F0"]
            )])
            donut_fig.update_layout(
                showlegend=True,
                height=260,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(donut_fig, use_container_width=True)

            # AI Progress Feedback Button
            if st.button("🤖 Request AI Progress Assessment", use_container_width=True):
                with st.spinner("Gemini is analyzing your completed tasks and learning velocity..."):
                    feedback = progress_agent.generate_progress_evaluation(
                        student_name=st.session_state.student_profile.get("name", "Student"),
                        target_career=st.session_state.student_profile.get("target_career", "Engineer"),
                        all_tasks=all_tasks,
                        completed_task_ids=completed_set
                    )
                    st.session_state.ai_progress_feedback = feedback

            if st.session_state.ai_progress_feedback:
                st.markdown(f"""
                <div class="card" style="border-left: 4px solid #4F46E5; background-color: #F8FAFC;">
                    <div style="font-weight: 700; color: #4F46E5; font-size: 0.95rem; margin-bottom: 5px;">
                        🧠 AI Mentor Assessment:
                    </div>
                    <div style="color: #1E293B; font-size: 0.95rem; line-height: 1.5;">
                        {st.session_state.ai_progress_feedback}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with list_col:
            st.subheader("Interactive Checklist")
            st.caption("Check tasks as you complete them to persist progress:")

            for task in all_tasks:
                tid = task.get("task_id", "")
                is_checked = tid in completed_set

                checked = st.checkbox(
                    f"{task.get('title')} ({task.get('estimated_hours', 4)}h)",
                    value=is_checked,
                    key=f"chk_{tid}"
                )

                if checked != is_checked:
                    if checked:
                        st.session_state.completed_task_ids.add(tid)
                    else:
                        st.session_state.completed_task_ids.discard(tid)

                    # Persist progress
                    save_res = supabase_service.record_progress(
                        st.session_state.student_profile.get("email", ""),
                        list(st.session_state.completed_task_ids)
                    )
                    st.rerun()


# ---------------------------------------------------------
# 10. Module 6: Gemini AI Mentor Chat
# ---------------------------------------------------------
elif menu_option == "💬 Gemini AI Mentor":
    st.markdown('<h1 class="main-title">Gemini AI Career & Code Mentor 💬</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Direct interactive tutoring, code review, and concept explanations grounded in your learning plan.</p>', unsafe_allow_html=True)

    profile = st.session_state.student_profile

    # Mentor Banner
    st.markdown(f"""
    <div class="agent-banner">
        <h3>Senior Tech Mentor Online 🤖</h3>
        <p>I know your goal is <strong>{profile.get('target_career')}</strong> and I'm here to clarify tricky concepts, explain code, or prepare you for technical rounds.</p>
    </div>
    """, unsafe_allow_html=True)

    # Prompt Chips
    st.write("**Quick Questions to Ask:**")
    q_col1, q_col2, q_col3 = st.columns(3)
    preset_q = None
    if q_col1.button("💡 Explain REST vs GraphQL with an analogy", use_container_width=True):
        preset_q = "Explain REST vs GraphQL with a clear real-world analogy."
    if q_col2.button("🛠️ How should I structure my capstone project?", use_container_width=True):
        preset_q = f"How should I structure a real-world portfolio capstone project for a {profile.get('target_career')}?"
    if q_col3.button("❓ What are top interview questions for my role?", use_container_width=True):
        preset_q = f"What are 3 essential technical interview questions for a {profile.get('target_career')} and how should I answer them?"

    # Display Chat History
    for msg in st.session_state.mentor_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle Input (from text input or preset chips)
    user_query = st.chat_input("Ask a question about code, architecture, or your roadmap...") or preset_q

    if user_query:
        # Add user message to history
        st.session_state.mentor_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate response from MentorAgent
        with st.chat_message("assistant"):
            with st.spinner("AI Mentor is formulating an explanation..."):
                try:
                    mentor_reply = mentor_agent.answer_question(
                        question=user_query,
                        student_context=profile,
                        chat_history=st.session_state.mentor_messages
                    )
                    st.markdown(mentor_reply)
                    st.session_state.mentor_messages.append({"role": "assistant", "content": mentor_reply})
                except Exception as e:
                    err_msg = f"Mentor encountered an issue: {e}"
                    st.error(err_msg)
                    st.session_state.mentor_messages.append({"role": "assistant", "content": err_msg})
