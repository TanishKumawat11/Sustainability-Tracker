"""
Climate Action & Sustainability Tracker — Streamlit UI.

Run with:
    streamlit run app.py

This file is intentionally thin — it only collects user input,
calls ActivityService, and renders results. All business logic
lives in tracker/services.py.
"""

import datetime
import streamlit as st
import pandas as pd

from tracker.services import ActivityService
from tracker.models import SustainabilityGoal
from tracker.factors import EnvironmentalFactors
from tracker.exceptions import (
    InvalidAmountError,
    InvalidCategoryError,
    InvalidDateError,
    InvalidGoalError,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="🌱 Sustainability Tracker",
    page_icon="🌱",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
# The ActivityService is created once and stored in session_state so it
# is not recreated (and the JSON file re-read) on every Streamlit rerun.

if "service" not in st.session_state:
    st.session_state.service = ActivityService()

if "goal" not in st.session_state:
    st.session_state.goal = None  # SustainabilityGoal or None

service: ActivityService = st.session_state.service

# ---------------------------------------------------------------------------
# Sidebar — monthly sustainability goal
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🌿 Sustainability Tracker")
    st.markdown("Track your environmental activities and monitor your carbon footprint.")
    st.divider()

    st.subheader("📋 Monthly CO₂ Goal")
    goal_input = st.number_input(
        "Target CO₂ (kg) for this month",
        min_value=0.1,
        max_value=10_000.0,
        value=float(st.session_state.goal.monthly_target_kg_co2)
        if st.session_state.goal
        else 100.0,
        step=1.0,
        help="Set the maximum kg of CO₂ you want to emit this month.",
    )

    if st.button("Set Goal", use_container_width=True):
        try:
            st.session_state.goal = SustainabilityGoal(goal_input)
            st.success(f"Goal set: {goal_input:.1f} kg CO₂ / month")
        except InvalidGoalError as e:
            st.error(str(e))

    if st.session_state.goal:
        st.info(f"Current goal: **{st.session_state.goal.monthly_target_kg_co2:.1f} kg CO₂**")
    else:
        st.warning("No goal set yet. Enter a target above and click **Set Goal**.")

    st.divider()
    st.caption(
        "⚠️ Environmental factors are simplified approximations "
        "for educational purposes only."
    )

# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

st.title("🌱 Climate Action & Sustainability Tracker")
st.markdown(
    "Record your daily environmental activities, monitor your impact, "
    "and work toward a greener lifestyle."
)

tab_add, tab_view, tab_summary, tab_tips = st.tabs(
    ["➕ Add Activity", "📋 View Activities", "📊 Impact Summary", "💡 Recommendations"]
)

# ---------------------------------------------------------------------------
# Tab 1 — Add Activity
# ---------------------------------------------------------------------------

with tab_add:
    st.subheader("Record a New Activity")

    with st.form("add_activity_form", clear_on_submit=True):
        category = st.selectbox(
            "Category",
            options=list(EnvironmentalFactors.ALLOWED_CATEGORIES),
            help="Select the type of environmental activity.",
        )

        # Derive the unit from the selected category for display
        unit_label = EnvironmentalFactors.CATEGORY_UNITS[category]

        amount = st.number_input(
            f"Amount ({unit_label})",
            min_value=0.0,
            max_value=100_000.0,
            value=0.0,
            step=0.1,
            format="%.2f",
            help=f"Enter the quantity in {unit_label}.",
        )

        description = st.text_input(
            "Description (optional)",
            max_chars=200,
            placeholder="e.g. Drove to work, Showered, Monthly electricity bill…",
        )

        date = st.date_input(
            "Activity Date",
            value=datetime.date.today(),
            max_value=datetime.date.today(),
            help="The date this activity occurred. Cannot be in the future.",
        )

        submitted = st.form_submit_button("Add Activity", use_container_width=True)

    if submitted:
        try:
            new_activity = service.add_activity(
                category=category,
                amount=amount,
                description=description,
                date=date,
            )
            factor = EnvironmentalFactors.IMPACT_FACTORS[category]
            impact_label = (
                f"{new_activity.impact:.4f} kg CO₂"
                if category in EnvironmentalFactors.CARBON_CATEGORIES
                else f"{new_activity.impact:.2f} {unit_label}"
            )
            st.success(
                f"✅ Activity added! "
                f"**{new_activity.amount} {new_activity.unit}** of {new_activity.category} "
                f"→ impact: **{impact_label}**"
            )
        except InvalidAmountError as e:
            st.error(f"Invalid amount: {e}")
        except InvalidCategoryError as e:
            st.error(f"Invalid category: {e}")
        except InvalidDateError as e:
            st.error(f"Invalid date: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

# ---------------------------------------------------------------------------
# Tab 2 — View Activities
# ---------------------------------------------------------------------------

with tab_view:
    st.subheader("All Recorded Activities")

    activities = service.get_all_activities()

    if not activities:
        st.info("No activities recorded yet. Use the **➕ Add Activity** tab to get started.")
    else:
        # Build a display-friendly dataframe
        rows = []
        for a in activities:
            impact_display = (
                f"{a.impact:.4f} kg CO₂"
                if a.category in EnvironmentalFactors.CARBON_CATEGORIES
                else f"{a.impact:.2f} {a.unit}"
            )
            rows.append({
                "Date": a.date.isoformat(),
                "Category": a.category,
                "Amount": f"{a.amount} {a.unit}",
                "Impact": impact_display,
                "Description": a.description or "—",
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Total activities recorded: **{len(activities)}**")

# ---------------------------------------------------------------------------
# Tab 3 — Impact Summary
# ---------------------------------------------------------------------------

with tab_summary:
    st.subheader("Environmental Impact Summary")

    activities = service.get_all_activities()

    if not activities:
        st.info("No activities recorded yet. Add some activities to see your impact summary.")
    else:
        total_co2 = service.total_carbon_emissions()
        total_water = service.total_water_usage()
        total_waste = service.total_waste_generated()

        # Metric cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔥 Total CO₂", f"{total_co2:.2f} kg")
        with col2:
            st.metric("💧 Total Water", f"{total_water:.2f} L")
        with col3:
            st.metric("🗑️ Total Waste", f"{total_waste:.2f} kg")

        st.divider()

        # Category breakdown
        st.subheader("Category Breakdown")
        summary = service.category_summary()

        summary_df = pd.DataFrame(
            [
                {
                    "Category": cat,
                    "Total Impact": round(val, 4),
                    "Unit": (
                        "kg CO₂"
                        if cat in EnvironmentalFactors.CARBON_CATEGORIES
                        else EnvironmentalFactors.CATEGORY_UNITS[cat]
                    ),
                }
                for cat, val in summary.items()
            ]
        )
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Bar chart — show only categories that have data
        chart_data = {
            cat: val for cat, val in summary.items() if val > 0
        }
        if chart_data:
            st.bar_chart(
                pd.DataFrame.from_dict(
                    {"Impact": chart_data}
                )
            )

        st.divider()

        # Progress toward goal
        st.subheader("📈 Progress Toward Monthly Goal")
        if st.session_state.goal is None:
            st.warning(
                "No monthly goal set yet. "
                "Use the sidebar to set your CO₂ target."
            )
        else:
            used_co2, target_co2, percent = service.get_progress(st.session_state.goal)
            progress_fraction = min(used_co2 / target_co2, 1.0)

            st.progress(progress_fraction)

            if percent >= 100:
                st.error(
                    f"⚠️ You have reached or exceeded your goal! "
                    f"Used: **{used_co2:.2f} kg** / Target: **{target_co2:.1f} kg** ({percent:.1f}%)"
                )
            elif percent >= 80:
                st.warning(
                    f"🔶 Approaching your limit — "
                    f"**{used_co2:.2f} kg** used of **{target_co2:.1f} kg** ({percent:.1f}%)"
                )
            else:
                st.success(
                    f"✅ On track — "
                    f"**{used_co2:.2f} kg** used of **{target_co2:.1f} kg** ({percent:.1f}%)"
                )

# ---------------------------------------------------------------------------
# Tab 4 — Recommendations
# ---------------------------------------------------------------------------

with tab_tips:
    st.subheader("💡 Sustainability Recommendations")
    st.markdown(
        "These tips are generated based on your recorded activities. "
        "Keep logging to get more personalised suggestions."
    )

    tips = service.get_recommendations(goal=st.session_state.goal)
    for tip in tips:
        st.markdown(f"- {tip}")
