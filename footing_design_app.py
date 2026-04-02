"""
BEAM REBAR CUTTING OPTIMIZER
Step 1: Rebar Parameters + Structure Geometry + Splice Zones + Running Lengths R1 & R2
"""

import streamlit as st
import math

st.set_page_config(page_title="Beam Rebar Optimizer", page_icon="🏗️")

st.title("🏗️ Beam Rebar Optimizer")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 0 — COMMERCIAL LENGTHS
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("Commercial Lengths")

com_length_defaults = [6.0, 7.5, 9.0, 10.5, 12.0]
com_lengths_m = st.multiselect(
    "Commercial lengths (m)",
    options=[6.0, 7.5, 9.0, 10.5, 12.0, 13.5, 15.0],
    default=com_length_defaults,
)
com_lengths_m = sorted(com_lengths_m)
com_lengths   = [l * 1000 for l in com_lengths_m]
max_com       = max(com_lengths) if com_lengths else 12000

st.write("Selected (mm):", [f"{l:,.0f}" for l in com_lengths])
st.session_state["com_lengths"] = com_lengths

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — REBAR PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Rebar Parameters")

c1, c2 = st.columns(2)
with c1:
    Db  = st.number_input("Db — Rebar diameter (mm)",    min_value=6,   max_value=50,   value=25,  step=1)
with c2:
    Anc = st.number_input("Anc — Anchorage length (mm)", min_value=100, max_value=2000, value=680, step=10)

prev_Db  = st.session_state.get("prev_Db",  Db)
prev_Anc = st.session_state.get("prev_Anc", Anc)
params_changed = (Db != prev_Db) or (Anc != prev_Anc)
default_Hk  = 12 * Db
default_Emb = Anc - default_Hk

if params_changed:
    st.session_state["Hk_val"]  = default_Hk
    st.session_state["Emb_val"] = default_Emb
    st.session_state["prev_Db"]  = Db
    st.session_state["prev_Anc"] = Anc

if "Hk_val"  not in st.session_state: st.session_state["Hk_val"]  = default_Hk
if "Emb_val" not in st.session_state: st.session_state["Emb_val"] = default_Emb

c3, c4 = st.columns(2)
with c3:
    Hk = st.number_input(
        f"Hk — Hook length (mm)  *(default: 12 × Db = {default_Hk})*",
        min_value=0, max_value=2000, value=st.session_state["Hk_val"], step=10, key="Hk_input",
    )
    st.session_state["Hk_val"] = Hk
with c4:
    Emb = st.number_input(
        f"Emb — Embedment length (mm)  *(default: Anc − Hk = {default_Emb})*",
        min_value=0, max_value=2000, value=st.session_state["Emb_val"], step=10, key="Emb_input",
    )
    st.session_state["Emb_val"] = Emb

st.markdown("")
st.markdown("**Lap Splice Lengths**")
c1, c2 = st.columns(2)
with c1:
    LapT = st.number_input("LapT — Top lap splice length (mm)",    min_value=100, max_value=3000, value=800, step=10)
with c2:
    LapB = st.number_input("LapB — Bottom lap splice length (mm)", min_value=100, max_value=3000, value=650, step=10)

st.markdown("")
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
h1.markdown("**Column**"); h2.markdown("**Span Length (mm)**"); h3.markdown("**Column**")

for i in range(no_spans):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        col_widths[i] = st.number_input(
            f"C{i+1} (mm)", min_value=100, max_value=3000,
            value=col_widths[i], step=50, key=f"cw_{i}",
        )
    with c2:
        span_lengths[i] = st.number_input(
            f"L{i+1} (mm)", min_value=500, max_value=50000,
            value=span_lengths[i], step=100, key=f"sl_{i}",
        )
    if i == no_spans - 1:
        with c3:
            col_widths[n_cols-1] = st.number_input(
                f"C{n_cols} (mm)", min_value=100, max_value=3000,
                value=col_widths[n_cols-1], step=50, key=f"cw_{n_cols-1}",
            )

st.session_state["col_widths"]   = col_widths
st.session_state["span_lengths"] = span_lengths

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — CLEAR SPAN LENGTHS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Clear Span Lengths")
st.markdown("**Sᵢ = Lᵢ − 0.5 × Cᵢ − 0.5 × C(i+1)**")

clear_spans = [
    span_lengths[i] - 0.5 * col_widths[i] - 0.5 * col_widths[i+1]
    for i in range(no_spans)
]

h1, h2, h3, h4 = st.columns([1, 2, 2, 2])
h1.markdown("**Span**"); h2.markdown("**L (mm)**")
h3.markdown("**− 0.5C − 0.5C (mm)**"); h4.markdown("**Clear Span S (mm)**")

for i in range(no_spans):
    deduction = 0.5 * col_widths[i] + 0.5 * col_widths[i+1]
    r1, r2, r3, r4 = st.columns([1, 2, 2, 2])
    r1.write(f"S{i+1}"); r2.write(f"{span_lengths[i]:,}")
    r3.write(f"− {deduction:,.0f}"); r4.write(f"**{clear_spans[i]:,.0f}**")

total = sum(col_widths) + sum(span_lengths)
st.markdown("---")
st.metric("Total Beam Length", f"{total:,} mm  ({total/1000:.3f} m)")

st.session_state["clear_spans"]       = clear_spans
st.session_state["no_spans"]          = no_spans
st.session_state["total_beam_length"] = total

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — SPLICE ZONES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Splice Zones")

def top_splice_zone(i, clear_spans, SplTEx, SplTIn, no_spans):
    S = clear_spans
    left  = SplTEx * S[0]          if i == 0          else SplTIn * max(S[i-1], S[i])
    right = SplTEx * S[no_spans-1] if i == no_spans-1 else SplTIn * max(S[i],   S[i+1])
    return left, right

def bot_splice_zone(i, clear_spans, SplBEx, SplBIn, no_spans):
    S = clear_spans
    left  = SplBEx * S[0]          if i == 0          else SplBIn * max(S[i-1], S[i])
    right = SplBEx * S[no_spans-1] if i == no_spans-1 else SplBIn * max(S[i],   S[i+1])
    return left, right

st.markdown("**Top Bars**")
h1, h2, h3 = st.columns([1, 2, 2])
h1.markdown("**Span**"); h2.markdown("**Left zone (mm)**"); h3.markdown("**Right zone (mm)**")

top_zones = []
for i in range(no_spans):
    lz, rz = top_splice_zone(i, clear_spans, SplTEx, SplTIn, no_spans)
    top_zones.append({"left": lz, "right": rz})
    r1, r2, r3 = st.columns([1, 2, 2])
    r1.write(f"S{i+1}"); r2.write(f"{lz:,.0f}"); r3.write(f"{rz:,.0f}")

st.markdown("")
st.markdown("**Bottom Bars**")
h1, h2, h3 = st.columns([1, 2, 2])
h1.markdown("**Span**"); h2.markdown("**Left zone (mm)**"); h3.markdown("**Right zone (mm)**")

bot_zones = []
for i in range(no_spans):
    lz, rz = bot_splice_zone(i, clear_spans, SplBEx, SplBIn, no_spans)
    bot_zones.append({"left": lz, "right": rz})
    r1, r2, r3 = st.columns([1, 2, 2])
    r1.write(f"S{i+1}"); r2.write(f"{lz:,.0f}"); r3.write(f"{rz:,.0f}")

st.session_state["top_zones"] = top_zones
st.session_state["bot_zones"] = bot_zones

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def ceiling_com(length, com_lengths):
    for cl in sorted(com_lengths):
        if cl >= length:
            return cl
    return None

def waste_row(length, com_lengths):
    cl = ceiling_com(length, com_lengths)
    w  = (cl - length) if cl is not None else None
    return cl, w

def print_rl_table(rows):
    """Print a running-length result table. rows = list of dicts."""
    h1, h2, h3, h4 = st.columns([1, 2, 2, 2])
    h1.markdown("**Label**")
    h2.markdown("**Running Length (mm)**")
    h3.markdown("**Com. Length (mm)**")
    h4.markdown("**Waste (mm)**")
    for row in rows:
        c1, c2, c3, c4 = st.columns([1, 2, 2, 2])
        c1.write(row["label"])
        c2.write(f"{row['running_length']:,.0f}")
        if row["com_length"] is None:
            c3.write("— exceeds max —"); c4.write("—")
        else:
            c3.write(f"{row['com_length']:,.0f}")
            c4.write(f"{row['waste']:,.0f}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — R1 SERIES (TOP BARS)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("R1 Series — Top Bars")
st.markdown("Bars starting at the **left hook of Span 1**, terminating at successive left splice zones.")

# R1j terminates at the LEFT splice zone of span j (0-based index j)
# Length = Hk + Emb + [S0 + C1+1 + S1 + C2+1 + ... through spans 0..j-1] + top_zones[j]["left"] + LapT

r1_series = []
for j in range(no_spans):
    dist = Emb
    for k in range(j):
        dist += clear_spans[k] + col_widths[k + 1]

    rl  = Hk + dist + top_zones[j]["left"] + LapT
    cl, w = waste_row(rl, com_lengths)
    r1_series.append({
        "label":          f"R1{ALPHA[j]}",
        "running_length": rl,
        "com_length":     cl,
        "waste":          w,
        "span_idx":       j,       # terminates at left zone of span j
    })
    if cl is None:
        break

if com_lengths:
    print_rl_table(r1_series)
else:
    st.warning("Select at least one commercial length.")

st.session_state["r1_series"] = r1_series

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — R2 SERIES (TOP BARS)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("R2 Series — Top Bars")
st.markdown(
    "Each R2 bar splices with an R1 bar. It starts just past where R1 terminated "
    "(inside the right splice zone of that span) and terminates at the left splice "
    "zone of a subsequent span."
)

# ── Logic ──────────────────────────────────────────────────────────────────────
# R1x terminates at the LEFT splice zone of span p (p = r1["span_idx"]).
# The R2 bar overlaps R1x by LapT within that same left splice zone.
# Then it travels rightward, passing through the RIGHT splice zone of span p,
# then through successive columns and spans, terminating at the LEFT splice zone
# of span q (q > p).
#
# R2 length from its own start to termination:
#   = top_zones[p]["right"]          ← right zone of span p (must clear it)
#   + col_widths[p+1]                ← column between span p and span p+1
#   + [for each interior span p+1..q-1: clear_spans[k] + col_widths[k+1]]
#   + top_zones[q]["left"] + LapT    ← left zone of span q + min lap
#
# The bar ends when q reaches the last span OR length > max_com.

r2_all = []  # flat list of all R2 rows across all R1 parents

for r1 in r1_series:
    if r1["com_length"] is None:
        continue  # R1 itself exceeded max — skip

    p          = r1["span_idx"]   # span where R1 terminated (0-based)
    r1_suffix  = r1["label"][-1]  # e.g. "A", "B", …

    # R2 can only continue if there is at least one span to the right of p
    if p >= no_spans - 1:
        continue

    r2_parent = []

    for q in range(p + 1, no_spans):
        sub_label = ALPHA[q - p - 1]   # A, B, C… for first, second, third reach

        # Distance from the start of the R2 bar to its termination point
        dist = top_zones[p]["right"]        # right splice zone of span p
        dist += col_widths[p + 1]           # column immediately to the right

        # Travel through interior spans p+1 .. q-1
        for k in range(p + 1, q):
            dist += clear_spans[k] + col_widths[k + 1]

        dist += top_zones[q]["left"] + LapT  # left splice zone of span q + lap

        cl, w = waste_row(dist, com_lengths)
        r2_parent.append({
            "label":          f"R2{r1_suffix}{sub_label}",
            "running_length": dist,
            "com_length":     cl,
            "waste":          w,
            "r1_parent":      r1["label"],
            "from_span":      p,
            "to_span":        q,
        })

        if cl is None:
            break   # exceeded max com length — no point going further

    r2_all.extend(r2_parent)

    # Print per-parent group
    if r2_parent:
        st.markdown(f"**Splicing with {r1['label']}** *(terminates at left zone of Span {p+1})*")
        print_rl_table(r2_parent)
        st.markdown("")

if not r2_all:
    st.info("No R2 bars generated — either only one span or all R1 bars reached the last span.")

st.session_state["r2_series"] = r2_all

# ── Confirm ─────────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("Confirm →"):
    cursor = 0
    positions = {}
    for i in range(n_cols):
        cw = col_widths[i]
        positions[f"C{i+1}"] = {
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
