"""
BEAM REBAR CUTTING OPTIMIZER
Step 1: Structure Geometry Input
"""

import streamlit as st

st.set_page_config(page_title="Beam Rebar Optimizer", page_icon="🏗️")

st.title("🏗️ Beam Rebar Optimizer")
st.subheader("Step 1 — Beam Geometry")

# ── Number of spans ─────────────────────────────────────────────────────────────
no_spans = int(st.number_input("Number of spans", min_value=1, max_value=20, value=2, step=1))

st.markdown("---")
st.markdown("Enter column widths and span lengths in **mm**:")

# ── Initialise storage ──────────────────────────────────────────────────────────
n_cols = no_spans + 1

if "col_widths" not in st.session_state or len(st.session_state["col_widths"]) != n_cols:
    st.session_state["col_widths"] = [400] * n_cols
if "span_lengths" not in st.session_state or len(st.session_state["span_lengths"]) != no_spans:
    st.session_state["span_lengths"] = [6000] * no_spans

col_widths   = list(st.session_state["col_widths"])
span_lengths = list(st.session_state["span_lengths"])

# ── Header row ──────────────────────────────────────────────────────────────────
h1, h2, h3 = st.columns([1, 2, 1])
h1.markdown("**Column**")
h2.markdown("**Span Length (mm)**")
h3.markdown("**Column**")

# ── One row per span ─────────────────────────────────────────────────────────────
# Key strategy:
#   Left column  of span i  → key "cw_{i}"          (unique, 0-based)
#   Span length  of span i  → key "sl_{i}"           (unique, 0-based)
#   Right column is NOT rendered here; it is the left column of the next row.
#   The very last right column (C_{n_cols}) is rendered after the loop.

for i in range(no_spans):
    c1, c2, c3 = st.columns([1, 2, 1])

    with c1:
        col_widths[i] = st.number_input(
            f"C{i + 1} (mm)",
            min_value=100, max_value=3000,
            value=col_widths[i], step=50,
            key=f"cw_{i}",
        )

    with c2:
        span_lengths[i] = st.number_input(
            f"L{i + 1} (mm)",
            min_value=500, max_value=50000,
            value=span_lengths[i], step=100,
            key=f"sl_{i}",
        )

    # c3 is intentionally left blank — the next row's left column IS this right column.
    # We only fill c3 on the last row to show the final column.
    if i == no_spans - 1:
        with c3:
            col_widths[n_cols - 1] = st.number_input(
                f"C{n_cols} (mm)",
                min_value=100, max_value=3000,
                value=col_widths[n_cols - 1], step=50,
                key=f"cw_{n_cols - 1}",
            )

# Persist
st.session_state["col_widths"]   = col_widths
st.session_state["span_lengths"] = span_lengths

# ── Total ───────────────────────────────────────────────────────────────────────
st.markdown("---")
total = sum(col_widths) + sum(span_lengths)
st.metric("Total Beam Length", f"{total:,} mm  ({total / 1000:.3f} m)")

# ── Confirm ──────────────────────────────────────────────────────────────────────
if st.button("Confirm Geometry →"):
    cursor = 0
    positions = {}
    for i in range(n_cols):
        cw = col_widths[i]
        positions[f"C{i + 1}"] = {
            "left_face":  cursor,
            "right_face": cursor + cw,
            "centerline": cursor + cw / 2,
            "width":      cw,
        }
        cursor += cw
        if i < no_spans:
            cursor += span_lengths[i]

    st.session_state["geometry_confirmed"] = True
    st.session_state["column_positions"]   = positions
    st.session_state["no_spans"]           = no_spans
    st.session_state["total_beam_length"]  = total
    st.success("Geometry confirmed! Ready for Step 2.")
