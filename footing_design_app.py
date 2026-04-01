"""
BEAM REBAR CUTTING OPTIMIZER
Step 1: Structure Geometry Input (Simplified)
"""

import streamlit as st

st.set_page_config(page_title="Beam Rebar Optimizer", page_icon="🏗️")

st.title("🏗️ Beam Rebar Optimizer")
st.subheader("Step 1 — Beam Geometry")

# ── Number of spans ────────────────────────────────────────────────────────────
no_spans = st.number_input("Number of spans", min_value=1, max_value=20, value=2, step=1)
no_spans = int(no_spans)

st.markdown("---")
st.markdown("Enter the **column width** and **span length** for each span (in mm):")

# ── Table header ───────────────────────────────────────────────────────────────
header = st.columns([1.2, 2, 1.2])
header[0].markdown("**Column**")
header[1].markdown("**Span Length (mm)**")
header[2].markdown("**Column**")

# ── Initialise session state ───────────────────────────────────────────────────
if "col_widths" not in st.session_state or len(st.session_state["col_widths"]) != no_spans + 1:
    st.session_state["col_widths"] = [400] * (no_spans + 1)
if "span_lengths" not in st.session_state or len(st.session_state["span_lengths"]) != no_spans:
    st.session_state["span_lengths"] = [6000] * no_spans

col_widths = list(st.session_state["col_widths"])
span_lengths = list(st.session_state["span_lengths"])

# ── One row per span ───────────────────────────────────────────────────────────
for i in range(no_spans):
    c1, c2, c3 = st.columns([1.2, 2, 1.2])

    with c1:
        col_widths[i] = st.number_input(
            f"C{i+1} (mm)",
            min_value=100, max_value=3000,
            value=col_widths[i], step=50,
            key=f"cw_{i}",
        )

    with c2:
        span_lengths[i] = st.number_input(
            f"L{i+1} (mm)",
            min_value=500, max_value=50000,
            value=span_lengths[i], step=100,
            key=f"sl_{i}",
        )

    with c3:
        col_widths[i + 1] = st.number_input(
            f"C{i+2} (mm)",
            min_value=100, max_value=3000,
            value=col_widths[i + 1], step=50,
            key=f"cw_{i+1}",
        )

# Persist
st.session_state["col_widths"] = col_widths
st.session_state["span_lengths"] = span_lengths

# ── Summary ────────────────────────────────────────────────────────────────────
st.markdown("---")
total_length = sum(col_widths) + sum(span_lengths)
st.metric("Total Beam Length", f"{total_length:,} mm  ({total_length/1000:.3f} m)")

# ── Confirm ────────────────────────────────────────────────────────────────────
if st.button("Confirm Geometry →"):
    cursor = 0
    positions = {}
    for i in range(no_spans + 1):
        cw = col_widths[i]
        positions[f"C{i+1}"] = {
            "left_face": cursor,
            "right_face": cursor + cw,
            "centerline": cursor + cw / 2,
            "width": cw,
        }
        cursor += cw
        if i < no_spans:
            cursor += span_lengths[i]

    st.session_state["geometry_confirmed"] = True
    st.session_state["column_positions"] = positions
    st.session_state["no_spans"] = no_spans
    st.session_state["total_beam_length"] = total_length
    st.success("Geometry confirmed! Ready for Step 2.")
