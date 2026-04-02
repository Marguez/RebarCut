"""
BEAM REBAR CUTTING OPTIMIZER
Step 1: Rebar Parameters + Structure Geometry Input
"""

import streamlit as st

st.set_page_config(page_title="Beam Rebar Optimizer", page_icon="🏗️")

st.title("🏗️ Beam Rebar Optimizer")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — REBAR PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("Rebar Parameters")

# --- Db and Anc first (Hk/Emb defaults depend on these) ---
c1, c2 = st.columns(2)
with c1:
    Db  = st.number_input("Db — Rebar diameter (mm)",    min_value=6,   max_value=50,   value=25,  step=1)
with c2:
    Anc = st.number_input("Anc — Anchorage length (mm)", min_value=100, max_value=2000, value=680, step=10)

# --- Hk and Emb: editable, defaults computed from Db/Anc ---
# Use session state to detect when Db/Anc change so we can reset defaults
prev_Db  = st.session_state.get("prev_Db",  Db)
prev_Anc = st.session_state.get("prev_Anc", Anc)
params_changed = (Db != prev_Db) or (Anc != prev_Anc)

default_Hk  = 12 * Db
default_Emb = Anc - default_Hk

# Reset stored overrides if Db or Anc changed
if params_changed:
    st.session_state["Hk_val"]  = default_Hk
    st.session_state["Emb_val"] = default_Emb
    st.session_state["prev_Db"]  = Db
    st.session_state["prev_Anc"] = Anc

# Initialise if first run
if "Hk_val" not in st.session_state:
    st.session_state["Hk_val"] = default_Hk
if "Emb_val" not in st.session_state:
    st.session_state["Emb_val"] = default_Emb

c3, c4 = st.columns(2)
with c3:
    Hk = st.number_input(
        f"Hk — Hook length (mm)  *(default: 12 × Db = {default_Hk})*",
        min_value=0, max_value=2000,
        value=st.session_state["Hk_val"], step=10,
        key="Hk_input",
    )
    st.session_state["Hk_val"] = Hk

with c4:
    Emb = st.number_input(
        f"Emb — Embedment length (mm)  *(default: Anc − Hk = {default_Emb})*",
        min_value=0, max_value=2000,
        value=st.session_state["Emb_val"], step=10,
        key="Emb_input",
    )
    st.session_state["Emb_val"] = Emb

st.markdown("")

# --- Lap splice lengths ---
st.markdown("**Lap Splice Lengths**")
c1, c2 = st.columns(2)
with c1:
    LapT = st.number_input("LapT — Top lap splice length (mm)",    min_value=100, max_value=3000, value=800, step=10)
with c2:
    LapB = st.number_input("LapB — Bottom lap splice length (mm)", min_value=100, max_value=3000, value=650, step=10)

st.markdown("")

# --- Splice zones ---
st.markdown("**Splice Zones** *(as fraction of clear span)*")
c1, c2 = st.columns(2)
with c1:
    st.markdown("*Top bars*")
    SplTEx = st.number_input("SplTEx — Top, Exterior span", min_value=0.0, max_value=1.0, value=0.25, step=0.01, format="%.2f")
    SplTIn = st.number_input("SplTIn — Top, Interior span", min_value=0.0, max_value=1.0, value=0.33, step=0.01, format="%.2f")
with c2:
    st.markdown("*Bottom bars*")
    SplBEx = st.number_input("SplBEx — Bottom, Exterior span", min_value=0.0, max_value=1.0, value=0.20, step=0.01, format="%.2f")
    SplBIn = st.number_input("SplBIn — Bottom, Interior span", min_value=0.0, max_value=1.0, value=0.20, step=0.01, format="%.2f")

# Persist rebar params
for k, v in {"Db": Db, "Anc": Anc, "Hk": Hk, "Emb": Emb,
             "LapT": LapT, "LapB": LapB,
             "SplTEx": SplTEx, "SplTIn": SplTIn,
             "SplBEx": SplBEx, "SplBIn": SplBIn}.items():
    st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — STRUCTURE GEOMETRY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Structure Geometry")

no_spans = int(st.number_input("Number of spans", min_value=1, max_value=20, value=2, step=1))

st.markdown("Enter column widths and span lengths in **mm**:")

n_cols = no_spans + 1

if "col_widths" not in st.session_state or len(st.session_state["col_widths"]) != n_cols:
    st.session_state["col_widths"] = [400] * n_cols
if "span_lengths" not in st.session_state or len(st.session_state["span_lengths"]) != no_spans:
    st.session_state["span_lengths"] = [6000] * no_spans

col_widths   = list(st.session_state["col_widths"])
span_lengths = list(st.session_state["span_lengths"])

h1, h2, h3 = st.columns([1, 2, 1])
h1.markdown("**Column**")
h2.markdown("**Span Length (mm)**")
h3.markdown("**Column**")

for i in range(no_spans):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        col_widths[i] = st.number_input(
            f"C{i + 1} (mm)", min_value=100, max_value=3000,
            value=col_widths[i], step=50, key=f"cw_{i}",
        )
    with c2:
        span_lengths[i] = st.number_input(
            f"L{i + 1} (mm)", min_value=500, max_value=50000,
            value=span_lengths[i], step=100, key=f"sl_{i}",
        )
    if i == no_spans - 1:
        with c3:
            col_widths[n_cols - 1] = st.number_input(
                f"C{n_cols} (mm)", min_value=100, max_value=3000,
                value=col_widths[n_cols - 1], step=50, key=f"cw_{n_cols - 1}",
            )

st.session_state["col_widths"]   = col_widths
st.session_state["span_lengths"] = span_lengths

# ── Clear span computation ──────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Clear Span Lengths")
st.markdown("Formula: **Sᵢ = Lᵢ − 0.5 × Cᵢ − 0.5 × C(i+1)**")
st.markdown("")

clear_spans = []
for i in range(no_spans):
    s = span_lengths[i] - 0.5 * col_widths[i] - 0.5 * col_widths[i + 1]
    clear_spans.append(s)

h1, h2, h3, h4 = st.columns([1, 2, 2, 2])
h1.markdown("**Span**")
h2.markdown("**L (mm)**")
h3.markdown("**− 0.5C − 0.5C (mm)**")
h4.markdown("**Clear Span S (mm)**")

for i in range(no_spans):
    deduction = 0.5 * col_widths[i] + 0.5 * col_widths[i + 1]
    r1, r2, r3, r4 = st.columns([1, 2, 2, 2])
    r1.write(f"S{i + 1}")
    r2.write(f"{span_lengths[i]:,}")
    r3.write(f"− {deduction:,.0f}")
    r4.write(f"**{clear_spans[i]:,.0f}**")

st.markdown("---")
total = sum(col_widths) + sum(span_lengths)
st.metric("Total Beam Length", f"{total:,} mm  ({total / 1000:.3f} m)")

st.session_state["clear_spans"]       = clear_spans
st.session_state["no_spans"]          = no_spans
st.session_state["total_beam_length"] = total

# ── Confirm ─────────────────────────────────────────────────────────────────────
if st.button("Confirm →"):
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
    st.success("Confirmed! Ready for the next step.")
