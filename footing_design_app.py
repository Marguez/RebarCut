"""
BEAM REBAR CUTTING OPTIMIZER
Step 1: Structure Geometry Input
=====================================
Collects span/column geometry from the user.
Outputs: session_state with columns and spans ready for Step 2.
"""

import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Beam Rebar Optimizer",
    page_icon="🏗️",
    layout="wide",
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'IBM Plex Sans', sans-serif;
        }
        h1, h2, h3 {
            font-family: 'IBM Plex Mono', monospace !important;
        }
        .main-title {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 2rem;
            font-weight: 600;
            color: #1a1a2e;
            border-bottom: 3px solid #e63946;
            padding-bottom: 0.4rem;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.95rem;
            color: #555;
            margin-bottom: 2rem;
        }
        .step-badge {
            background: #e63946;
            color: white;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 2px;
            display: inline-block;
            margin-bottom: 0.5rem;
            letter-spacing: 0.08em;
        }
        .section-header {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 1rem;
            font-weight: 600;
            color: #1a1a2e;
            background: #f0f2f5;
            padding: 0.5rem 0.8rem;
            border-left: 4px solid #e63946;
            margin: 1.2rem 0 0.8rem 0;
        }
        .col-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.82rem;
            color: #333;
            font-weight: 600;
        }
        .span-card {
            background: #f8f9fc;
            border: 1px solid #dde1ea;
            border-radius: 6px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.8rem;
        }
        .geometry-preview {
            background: #1a1a2e;
            color: #e0e0e0;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.82rem;
            padding: 1.2rem;
            border-radius: 6px;
            white-space: pre;
            overflow-x: auto;
            line-height: 1.7;
        }
        .stButton > button {
            background: #e63946;
            color: white;
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 600;
            border: none;
            border-radius: 3px;
            padding: 0.5rem 1.5rem;
            letter-spacing: 0.05em;
        }
        .stButton > button:hover {
            background: #c1121f;
        }
        div[data-testid="stNumberInput"] label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.8rem;
            font-weight: 600;
            color: #333;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🏗️ Beam Rebar Cutting Optimizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Minimize waste · Enforce splicing zones · Comply with lap lengths</div>',
    unsafe_allow_html=True,
)

# ── Step badge ─────────────────────────────────────────────────────────────────
st.markdown('<span class="step-badge">STEP 1 OF 4 — STRUCTURE GEOMETRY</span>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION A — Number of Spans
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">A. Number of Spans</div>', unsafe_allow_html=True)

col_ns, col_info = st.columns([1, 2])
with col_ns:
    no_spans = st.number_input(
        "NoSpans — Number of spans (column-to-column)",
        min_value=1,
        max_value=20,
        value=st.session_state.get("no_spans", 2),
        step=1,
        help="Each span is defined between two columns. "
             "For N spans you will have N+1 columns (C1 … C(N+1)).",
    )
    st.session_state["no_spans"] = int(no_spans)

with col_info:
    st.info(
        f"**{int(no_spans)} span(s)** → **{int(no_spans)+1} column(s)** "
        f"(C1 through C{int(no_spans)+1})"
    )

# ══════════════════════════════════════════════════════════════════════════════
# SECTION B — Column & Span Dimensions
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">B. Column Widths & Span Lengths</div>', unsafe_allow_html=True)
st.markdown(
    "_Enter dimensions in **millimeters (mm)**. "
    "Column width = the dimension parallel to the beam axis (i.e. the depth of the column)._"
)

# Initialise storage lists if needed
if "col_widths" not in st.session_state or len(st.session_state["col_widths"]) != int(no_spans) + 1:
    st.session_state["col_widths"] = [400] * (int(no_spans) + 1)
if "span_lengths" not in st.session_state or len(st.session_state["span_lengths"]) != int(no_spans):
    st.session_state["span_lengths"] = [6000] * int(no_spans)

col_widths  = list(st.session_state["col_widths"])
span_lengths = list(st.session_state["span_lengths"])

# ── Layout helper: draw one row per span + final column ────────────────────────
for i in range(int(no_spans)):
    st.markdown(f'<div class="span-card">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])

    with c1:
        st.markdown(f'<p class="col-label">C{i+1} — Column {i+1} width (mm)</p>', unsafe_allow_html=True)
        col_widths[i] = st.number_input(
            f"C{i+1} width",
            min_value=100,
            max_value=3000,
            value=col_widths[i],
            step=50,
            key=f"cw_{i}",
            label_visibility="collapsed",
        )

    with c2:
        st.markdown(f'<p class="col-label">L{i+1} — Span {i+1} clear length (mm)</p>', unsafe_allow_html=True)
        span_lengths[i] = st.number_input(
            f"L{i+1}",
            min_value=500,
            max_value=50000,
            value=span_lengths[i],
            step=100,
            key=f"sl_{i}",
            label_visibility="collapsed",
            help="Clear distance between column faces",
        )

    with c3:
        # Show last column only on the final span iteration
        if i == int(no_spans) - 1:
            st.markdown(f'<p class="col-label">C{i+2} — Column {i+2} width (mm)</p>', unsafe_allow_html=True)
            col_widths[i + 1] = st.number_input(
                f"C{i+2} width",
                min_value=100,
                max_value=3000,
                value=col_widths[i + 1],
                step=50,
                key=f"cw_{i+1}",
                label_visibility="collapsed",
            )

    st.markdown("</div>", unsafe_allow_html=True)

# For multi-span beams we need C(i+2) widths for intermediate columns too.
# They're already captured as col_widths[i] for the NEXT span's left column.
# Re-show intermediate columns that appear on the RHS of each non-last span:
if int(no_spans) > 1:
    st.markdown("**Intermediate column widths** (right column of each non-final span)")
    for i in range(int(no_spans) - 1):
        st.markdown(f'<div class="span-card">', unsafe_allow_html=True)
        c1, _ = st.columns([1, 3])
        with c1:
            st.markdown(f'<p class="col-label">C{i+2} — Column {i+2} width (mm)</p>', unsafe_allow_html=True)
            col_widths[i + 1] = st.number_input(
                f"C{i+2} width (intermediate)",
                min_value=100,
                max_value=3000,
                value=col_widths[i + 1],
                step=50,
                key=f"cw_mid_{i+1}",
                label_visibility="collapsed",
            )
        st.markdown("</div>", unsafe_allow_html=True)

# Persist to session state
st.session_state["col_widths"]   = col_widths
st.session_state["span_lengths"] = span_lengths

# ══════════════════════════════════════════════════════════════════════════════
# SECTION C — Geometry Preview (ASCII diagram)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">C. Geometry Preview</div>', unsafe_allow_html=True)

def build_ascii_diagram(no_spans, col_widths, span_lengths):
    """Render a simple ASCII plan-view beam diagram."""
    total_mm = sum(col_widths) + sum(span_lengths)
    lines = []

    # Top line — column labels
    label_row = ""
    dim_row   = ""
    bar_row   = ""

    for i in range(no_spans):
        cw = col_widths[i]
        sl = span_lengths[i]
        col_tag  = f" C{i+1}({cw}) "
        span_tag = f"——— L{i+1}={sl/1000:.2f}m ———"
        label_row += col_tag.ljust(len(col_tag)) + span_tag
        bar_row   += "█" * len(col_tag) + "─" * len(span_tag)

    # Last column
    cw = col_widths[no_spans]
    last_col = f" C{no_spans+1}({cw}) "
    label_row += last_col
    bar_row   += "█" * len(last_col)

    lines.append("BEAM AXIS →")
    lines.append("")
    lines.append(label_row)
    lines.append(bar_row)
    lines.append("")
    lines.append(f"Total beam length  : {total_mm:,} mm  ({total_mm/1000:.3f} m)")
    lines.append(f"Number of spans    : {no_spans}")
    lines.append(f"Number of columns  : {no_spans+1}")
    return "\n".join(lines)

diagram = build_ascii_diagram(int(no_spans), col_widths, span_lengths)
st.markdown(f'<div class="geometry-preview">{diagram}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION D — Derived Values (for verification)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">D. Summary</div>', unsafe_allow_html=True)

total_clear  = sum(span_lengths)
total_col_w  = sum(col_widths)
total_length = total_clear + total_col_w

summary_cols = st.columns(4)
summary_cols[0].metric("Total spans",         f"{int(no_spans)}")
summary_cols[1].metric("Total columns",        f"{int(no_spans)+1}")
summary_cols[2].metric("Total column width",   f"{total_col_w:,} mm")
summary_cols[3].metric("Total beam length",    f"{total_length:,} mm  ({total_length/1000:.3f} m)")

# ══════════════════════════════════════════════════════════════════════════════
# CONFIRM & PROCEED
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### Ready for the next step?")
st.markdown(
    "Once the geometry looks correct, click **Confirm Geometry** to lock it in "
    "and proceed to **Step 2 — Rebar & Splicing Parameters**."
)

if st.button("✅ Confirm Geometry → Proceed to Step 2"):
    # Compute centre-lines and column face positions (useful for subsequent steps)
    positions = {}  # {label: (left_face_mm, right_face_mm, centerline_mm)}
    cursor = 0
    for i in range(int(no_spans) + 1):
        cw = col_widths[i]
        lf = cursor
        rf = cursor + cw
        cl = cursor + cw / 2
        positions[f"C{i+1}"] = {"left_face": lf, "right_face": rf, "centerline": cl, "width": cw}
        cursor = rf
        if i < int(no_spans):
            cursor += span_lengths[i]

    st.session_state["geometry_confirmed"] = True
    st.session_state["column_positions"]   = positions
    st.session_state["total_beam_length"]  = total_length
    st.success("✅ Geometry confirmed and saved! Proceed to Step 2 in the sidebar or next page.")
    st.balloons()

# ── Dev debug expander ─────────────────────────────────────────────────────────
with st.expander("🔧 Session State (debug)", expanded=False):
    st.json(
        {
            "no_spans":     st.session_state.get("no_spans"),
            "col_widths":   st.session_state.get("col_widths"),
            "span_lengths": st.session_state.get("span_lengths"),
            "geometry_confirmed": st.session_state.get("geometry_confirmed", False),
            "column_positions":   st.session_state.get("column_positions", {}),
        }
    )
