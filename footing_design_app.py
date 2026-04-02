"""
BEAM REBAR CUTTING OPTIMIZER
Full Running Length Series — Top Bars
"""

import streamlit as st

st.set_page_config(page_title="Beam Rebar Optimizer", page_icon="🏗️")

st.title("🏗️ Beam Rebar Optimizer")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 0 — COMMERCIAL LENGTHS
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("Commercial Lengths")

com_lengths_m = st.multiselect(
    "Commercial lengths (m)",
    options=[6.0, 7.5, 9.0, 10.5, 12.0, 13.5, 15.0],
    default=[6.0, 7.5, 9.0, 10.5, 12.0],
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
    h1, h2, h3, h4, h5 = st.columns([1.5, 2, 2, 2, 2])
    h1.markdown("**Label**")
    h2.markdown("**Running Length (mm)**")
    h3.markdown("**Com. Length (mm)**")
    h4.markdown("**Waste (mm)**")
    h5.markdown("**Cumul. Waste (mm)**")
    for row in rows:
        c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2, 2, 2])
        c1.write(row["label"])
        c2.write(f"{row['running_length']:,.0f}")
        if row["com_length"] is None:
            c3.write("— exceeds max —"); c4.write("—"); c5.write("—")
        else:
            c3.write(f"{row['com_length']:,.0f}")
            c4.write(f"{row['waste']:,.0f}")
            cw = row.get("cum_waste")
            c5.write(f"{cw:,.0f}" if cw is not None else "—")

# ══════════════════════════════════════════════════════════════════════════════
# CORE ENGINE — generate all series recursively
# ══════════════════════════════════════════════════════════════════════════════
#
# Each "bar" is described by:
#   label       : e.g. "R2BA"
#   running_length
#   com_length
#   waste
#   cum_waste   : sum of waste of this bar + all ancestors
#   span_idx    : span (0-based) where this bar terminates (left splice zone)
#                 OR no_spans-1 flagged as terminal (hook end)
#   is_terminal : True if this bar ends with Emb+Hk at the last column
#   parent_waste: cumulative waste inherited from the parent chain
#
# Terminal condition for a bar ending in last span:
#   length = (S[last] - left_zone[last]) + Emb + Hk
#   (starts at beginning of left splice zone of last span, goes to right hook)
#
# Mid-series bar from span p to span q (q > p, not yet last):
#   length = (S[p] - left_zone[p]) + col[p+1]
#            + sum over k in p+1..q-1 of (S[k] + col[k+1])
#            + left_zone[q] + LapT
#
# R1 (first series) is special — starts from left hook:
#   length = Hk + Emb + [spans/cols] + left_zone[j] + LapT   (non-terminal)
#   terminal R1 (if last span reachable):
#   length = Hk + Emb + [spans/cols through last span] + Emb + Hk
#            but that is just a full-beam bar handled separately.

def mid_bar_length(p, q, clear_spans, col_widths, top_zones, LapT):
    """Length of a bar that starts at the beginning of left_zone[p] and
    terminates at the end of the lap in left_zone[q]."""
    dist = clear_spans[p] - top_zones[p]["left"]   # remainder of span p
    dist += col_widths[p + 1]                       # column right of span p
    for k in range(p + 1, q):
        dist += clear_spans[k] + col_widths[k + 1]
    dist += top_zones[q]["left"] + LapT
    return dist

def terminal_bar_length(p, clear_spans, col_widths, top_zones, Hk, Emb, no_spans):
    """Length of a bar that starts at the beginning of left_zone[p] and
    terminates through the last span to the right hook."""
    last = no_spans - 1
    dist = clear_spans[p] - top_zones[p]["left"]   # remainder of span p
    dist += col_widths[p + 1]
    for k in range(p + 1, last):
        dist += clear_spans[k] + col_widths[k + 1]
    # last span: full clear span + Emb + Hk on the right
    if p < last:
        dist += clear_spans[last]
    dist += Emb + Hk
    return dist

# ──────────────────────────────────────────────────────────────────────────────
# Build all series
# ──────────────────────────────────────────────────────────────────────────────

all_series = []   # list of lists; all_series[0] = R1 bars, [1] = R2 bars, …

# ── R1 series ──
r1_bars = []
for j in range(no_spans):
    dist = Emb
    for k in range(j):
        dist += clear_spans[k] + col_widths[k + 1]

    # Non-terminal: terminates at left_zone[j] + LapT
    rl = Hk + dist + top_zones[j]["left"] + LapT
    cl, w = waste_row(rl, com_lengths)

    r1_bars.append({
        "label":          f"R1{ALPHA[j]}",
        "running_length": rl,
        "com_length":     cl,
        "waste":          w,
        "cum_waste":      w,
        "span_idx":       j,
        "is_terminal":    False,
        "parent_waste":   0,
        "suffix":         ALPHA[j],   # label suffix chain for children
    })

    if cl is None:
        break   # exceeded max — no point going further right

    # Check: can this same R1 bar be extended to a terminal (hook) ending?
    # That would be a different bar altogether — handled in higher series.

all_series.append(r1_bars)

# ── Higher series (R2, R3, …) ──
series_idx = 2
parent_bars = r1_bars

while True:
    new_bars   = []
    series_chr = str(series_idx)

    for parent in parent_bars:
        if parent["com_length"] is None:
            continue
        if parent["is_terminal"]:
            continue   # already ended with a hook — no continuation

        p            = parent["span_idx"]
        parent_waste = parent["cum_waste"] if parent["cum_waste"] is not None else 0
        parent_sfx   = parent["suffix"]    # e.g. "A", "BA", "CBA"

        children = []

        # ── Option 1: mid-span terminations (left splice zones of spans q > p) ──
        for q in range(p + 1, no_spans):
            sub_sfx   = ALPHA[q - p - 1]   # A, B, C…
            child_lbl = f"R{series_chr}{parent_sfx}{sub_sfx}"

            rl      = mid_bar_length(p, q, clear_spans, col_widths, top_zones, LapT)
            cl, w   = waste_row(rl, com_lengths)
            cum_w   = (parent_waste + w) if w is not None else None

            children.append({
                "label":        child_lbl,
                "running_length": rl,
                "com_length":   cl,
                "waste":        w,
                "cum_waste":    cum_w,
                "span_idx":     q,
                "is_terminal":  False,
                "parent_waste": parent_waste,
                "suffix":       parent_sfx + sub_sfx,
            })

            if cl is None:
                break   # exceeded max — don't try further spans

        # ── Option 2: terminal ending (last span → right hook) ──
        # Only add if the last mid-span option didn't already reach the last span
        # OR if the mid-span version to the last span exceeds max_com.
        last = no_spans - 1
        if p < last:
            term_rl = terminal_bar_length(p, clear_spans, col_widths, top_zones, Hk, Emb, no_spans)
            term_cl, term_w = waste_row(term_rl, com_lengths)
            term_cum_w = (parent_waste + term_w) if term_w is not None else None
            term_sfx   = parent_sfx + "T"   # "T" marks terminal

            # Only add terminal if:
            # (a) we haven't already added a mid-span bar reaching the last span, OR
            # (b) the mid-span bar to the last span exceeded max_com
            last_mid_exceeds = (
                len(children) > 0 and
                children[-1]["span_idx"] == last and
                children[-1]["com_length"] is None
            )
            last_mid_reached = any(c["span_idx"] == last and not c["is_terminal"] for c in children)

            if last_mid_exceeds or not last_mid_reached:
                children.append({
                    "label":          f"R{series_chr}{parent_sfx}T",
                    "running_length": term_rl,
                    "com_length":     term_cl,
                    "waste":          term_w,
                    "cum_waste":      term_cum_w,
                    "span_idx":       last,
                    "is_terminal":    True,
                    "parent_waste":   parent_waste,
                    "suffix":         term_sfx,
                })

        new_bars.extend(children)

    if not new_bars:
        break

    all_series.append(new_bars)
    parent_bars = new_bars
    series_idx += 1

    if series_idx > 30:   # safety cap
        break

# ══════════════════════════════════════════════════════════════════════════════
# PRINT ALL SERIES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Running Length Series — Top Bars")

for s_idx, series_bars in enumerate(all_series):
    series_num = s_idx + 1
    st.markdown(f"### R{series_num} Series")

    if series_num == 1:
        # R1 has no grouping — flat list
        print_rl_table(series_bars)
    else:
        # Group by parent label (first N-1 chars of label after "R{n}")
        printed_parents = set()
        for bar in series_bars:
            # Derive parent label: strip last character of the suffix
            parent_sfx = bar["suffix"][:-1] if not bar["is_terminal"] else bar["suffix"][:-2]
            # Simpler: group by parent_waste key — use label up to last char
            parent_label_key = bar["label"][:-1] if not bar["label"].endswith("T") else bar["label"][:-2]

            if parent_label_key not in printed_parents:
                printed_parents.add(parent_label_key)
                # Find parent bar
                parent_series = all_series[s_idx - 1]
                matching = [b for b in parent_series if b["suffix"] == bar["suffix"][:-1]]
                if matching:
                    pm = matching[0]
                    st.markdown(f"**Splicing with {pm['label']}** *(terminated at Span {pm['span_idx']+1} left zone)*")

            # Print this bar
            print_rl_table([bar])

    st.markdown("")

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
