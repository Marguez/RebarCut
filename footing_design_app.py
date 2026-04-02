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

st.markdown("**Lap Splice Lengths**")
c1, c2 = st.columns(2)
with c1:
    LapT = st.number_input("LapT — Top lap splice length (mm)",    min_value=100, max_value=3000, value=800, step=10)
with c2:
    LapB = st.number_input("LapB — Bottom lap splice length (mm)", min_value=100, max_value=3000, value=650, step=10)

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
# SECTION 3 — CLEAR SPANS
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
st.session_state["clear_spans"] = clear_spans
st.session_state["no_spans"]    = no_spans

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — SPLICE ZONES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Splice Zones")

def top_splice_zone(i):
    S = clear_spans
    left  = SplTEx * S[0]          if i == 0          else SplTIn * max(S[i-1], S[i])
    right = SplTEx * S[no_spans-1] if i == no_spans-1 else SplTIn * max(S[i],   S[i+1])
    return left, right

top_zones = []
st.markdown("**Top Bars**")
h1, h2, h3 = st.columns([1, 2, 2])
h1.markdown("**Span**"); h2.markdown("**Left zone (mm)**"); h3.markdown("**Right zone (mm)**")
for i in range(no_spans):
    lz, rz = top_splice_zone(i)
    top_zones.append({"left": lz, "right": rz})
    r1, r2, r3 = st.columns([1, 2, 2])
    r1.write(f"S{i+1}"); r2.write(f"{lz:,.0f}"); r3.write(f"{rz:,.0f}")

bot_zones = []
st.markdown("**Bottom Bars**")
h1, h2, h3 = st.columns([1, 2, 2])
h1.markdown("**Span**"); h2.markdown("**Left zone (mm)**"); h3.markdown("**Right zone (mm)**")
for i in range(no_spans):
    S = clear_spans
    lz = SplBEx * S[0]          if i == 0          else SplBIn * max(S[i-1], S[i])
    rz = SplBEx * S[no_spans-1] if i == no_spans-1 else SplBIn * max(S[i],   S[i+1])
    bot_zones.append({"left": lz, "right": rz})
    r1, r2, r3 = st.columns([1, 2, 2])
    r1.write(f"S{i+1}"); r2.write(f"{lz:,.0f}"); r3.write(f"{rz:,.0f}")

st.session_state["top_zones"] = top_zones
st.session_state["bot_zones"] = bot_zones

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def ceiling_com(length):
    for cl in sorted(com_lengths):
        if cl >= length:
            return cl
    return None

def get_waste(length):
    cl = ceiling_com(length)
    w  = (cl - length) if cl is not None else None
    return cl, w

def print_series_table(rows):
    h1, h2, h3, h4, h5 = st.columns([1.5, 2, 2, 2, 2])
    h1.markdown("**Label**"); h2.markdown("**Length (mm)**")
    h3.markdown("**Com. Length (mm)**"); h4.markdown("**Waste (mm)**")
    h5.markdown("**Cumul. Waste (mm)**")
    for row in rows:
        c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2, 2, 2])
        c1.write(row["label"])
        c2.write(f"{row['rl']:,.0f}")
        if row["cl"] is None:
            c3.write("exceeds max"); c4.write("—"); c5.write("—")
        else:
            c3.write(f"{row['cl']:,.0f}")
            c4.write(f"{row['waste']:,.0f}")
            c5.write(f"{row['cum_waste']:,.0f}")

# ══════════════════════════════════════════════════════════════════════════════
# RUNNING LENGTH ENGINE
# ══════════════════════════════════════════════════════════════════════════════
#
# A "node" represents a bar in a chain. Key fields:
#   label        : e.g. "R2BA"
#   rl           : running length (mm)
#   cl           : commercial length used (None if exceeds max)
#   waste        : individual waste
#   cum_waste    : cumulative waste of entire chain so far
#   span_idx     : span (0-based) where this bar's lap ends (left splice zone)
#   is_terminal  : True if this bar ends at the right hook
#
# Rules:
#   1. A bar is "mid" if it terminates at a left splice zone + LapT
#      and can be continued by the next series.
#   2. A bar is "terminal" if it ends with S[last] + Emb + Hk.
#      No continuation after terminal.
#   3. A bar exceeding max_com is dead — it cannot be used. But that splice
#      point still needs to be closed by the NEXT series starting fresh.
#   4. EVERY chain must eventually reach a terminal bar.
#
# For a mid-series bar starting at left_zone[p]:
#   To reach midspan of span q (q > p, q < last):
#     rl = (S[p] - lz[p]) + col[p+1] + sum(S[k]+col[k+1] for k=p+1..q-1) + lz[q] + LapT
#   To reach terminal (last span) within same bar (q = last):
#     rl = (S[p] - lz[p]) + col[p+1] + sum(S[k]+col[k+1] for k=p+1..last-1) + S[last] + Emb + Hk
#
# For a terminal-only bar starting at left_zone[last] (when parent reached last span
# but the terminal extension exceeded max):
#     rl = S[last] - lz[last] + Emb + Hk
#
# ── Build R1 (special: starts from left hook) ─────────────────────────────────

last = no_spans - 1

def mid_rl_from_p(p, q):
    """Bar starting at lz[p], terminating at lz[q] + LapT. p < q < last."""
    d = clear_spans[p] - top_zones[p]["left"]
    d += col_widths[p + 1]
    for k in range(p + 1, q):
        d += clear_spans[k] + col_widths[k + 1]
    d += top_zones[q]["left"] + LapT
    return d

def terminal_rl_from_p(p):
    """Bar starting at lz[p], going all the way to right hook through last span."""
    d = clear_spans[p] - top_zones[p]["left"]
    d += col_widths[p + 1]
    for k in range(p + 1, last):
        d += clear_spans[k] + col_widths[k + 1]
    d += clear_spans[last] + Emb + Hk
    return d

def terminal_rl_last_only():
    """Bar that starts at lz[last] and ends at right hook. Used when previous
    series reached last span but terminal extension exceeded max_com."""
    return clear_spans[last] - top_zones[last]["left"] + Emb + Hk

# Each node dict:
# { label, rl, cl, waste, cum_waste, span_idx, is_terminal, parent_cum_waste, suffix }

all_series = []   # list of lists

# ── R1 ────────────────────────────────────────────────────────────────────────
r1_nodes = []
for j in range(no_spans):
    # Base distance from hook to start of left_zone[j]
    d = Emb
    for k in range(j):
        d += clear_spans[k] + col_widths[k + 1]

    if j < last:
        # Mid termination at lz[j] + LapT
        rl = Hk + d + top_zones[j]["left"] + LapT
        cl, w = get_waste(rl)
        r1_nodes.append({
            "label": f"R1{ALPHA[j]}", "rl": rl, "cl": cl, "waste": w,
            "cum_waste": w, "span_idx": j, "is_terminal": False,
            "parent_cum_waste": 0, "suffix": ALPHA[j],
        })
        if cl is None:
            break  # exceeded max, stop exploring further spans in R1
    else:
        # j == last: offer both mid AND terminal in R1
        # Mid version (terminates at lz[last] + LapT)
        rl_mid = Hk + d + top_zones[last]["left"] + LapT
        cl_mid, w_mid = get_waste(rl_mid)
        r1_nodes.append({
            "label": f"R1{ALPHA[j]}", "rl": rl_mid, "cl": cl_mid, "waste": w_mid,
            "cum_waste": w_mid, "span_idx": last, "is_terminal": False,
            "parent_cum_waste": 0, "suffix": ALPHA[j],
        })
        # Terminal version (extends to right hook) — next letter
        rl_term = Hk + d + clear_spans[last] + Emb + Hk
        cl_term, w_term = get_waste(rl_term)
        r1_nodes.append({
            "label": f"R1{ALPHA[j+1]}", "rl": rl_term, "cl": cl_term, "waste": w_term,
            "cum_waste": w_term, "span_idx": last, "is_terminal": True,
            "parent_cum_waste": 0, "suffix": ALPHA[j+1],
        })
        break

all_series.append(r1_nodes)

# ── Higher series ─────────────────────────────────────────────────────────────
series_num = 2
parent_layer = r1_nodes

while True:
    new_nodes = []

    for parent in parent_layer:
        if parent["is_terminal"]:
            continue  # chain complete, no continuation
        if parent["cl"] is None:
            # Parent exceeded max — this splice point still needs to be closed.
            # BUT we cannot use a bar that exceeded max_com — skip mid options,
            # only the terminal-from-last is valid if parent reached last span.
            # Actually: parent exceeded max means we cannot cut this bar at all.
            # Skip — the chain ending here is invalid.
            continue

        p = parent["span_idx"]
        pcw = parent["cum_waste"]   # cumulative waste so far
        psuffix = parent["suffix"]

        children = []
        sub_idx = 0  # index for sub-label A, B, C...

        if p == last:
            # Parent already at last span (mid termination there).
            # Only option: terminal bar from lz[last] to right hook.
            rl = terminal_rl_last_only()
            cl, w = get_waste(rl)
            cum_w = pcw + w if w is not None else None
            children.append({
                "label": f"R{series_num}{psuffix}{ALPHA[sub_idx]}",
                "rl": rl, "cl": cl, "waste": w, "cum_waste": cum_w,
                "span_idx": last, "is_terminal": True,
                "parent_cum_waste": pcw, "suffix": psuffix + ALPHA[sub_idx],
            })
        else:
            # p < last: explore mid terminations at q = p+1 .. last-1,
            # then terminal at last span (same bar), then terminal-only if needed.
            for q in range(p + 1, last):
                rl = mid_rl_from_p(p, q)
                cl, w = get_waste(rl)
                cum_w = pcw + w if w is not None else None
                children.append({
                    "label": f"R{series_num}{psuffix}{ALPHA[sub_idx]}",
                    "rl": rl, "cl": cl, "waste": w, "cum_waste": cum_w,
                    "span_idx": q, "is_terminal": False,
                    "parent_cum_waste": pcw, "suffix": psuffix + ALPHA[sub_idx],
                })
                sub_idx += 1
                if cl is None:
                    break  # exceeded max, stop mid options

            # Terminal option: extend all the way to right hook in same bar
            rl_term = terminal_rl_from_p(p)
            cl_term, w_term = get_waste(rl_term)
            cum_w_term = pcw + w_term if w_term is not None else None

            if cl_term is not None:
                # Fits in a commercial length — add as terminal option
                children.append({
                    "label": f"R{series_num}{psuffix}{ALPHA[sub_idx]}",
                    "rl": rl_term, "cl": cl_term, "waste": w_term,
                    "cum_waste": cum_w_term,
                    "span_idx": last, "is_terminal": True,
                    "parent_cum_waste": pcw, "suffix": psuffix + ALPHA[sub_idx],
                })
            else:
                # Terminal exceeds max — add mid version to last span so next
                # series can close it with the short terminal-from-last bar.
                # (Only add if not already added in the mid loop above)
                already_has_last = any(c["span_idx"] == last and not c["is_terminal"]
                                       for c in children)
                if not already_has_last:
                    rl_mid_last = mid_rl_from_p(p, last)
                    cl_ml, w_ml = get_waste(rl_mid_last)
                    cum_w_ml = pcw + w_ml if w_ml is not None else None
                    children.append({
                        "label": f"R{series_num}{psuffix}{ALPHA[sub_idx]}",
                        "rl": rl_mid_last, "cl": cl_ml, "waste": w_ml,
                        "cum_waste": cum_w_ml,
                        "span_idx": last, "is_terminal": False,
                        "parent_cum_waste": pcw, "suffix": psuffix + ALPHA[sub_idx],
                    })

        new_nodes.extend(children)

    if not new_nodes:
        break

    all_series.append(new_nodes)
    parent_layer = new_nodes
    series_num += 1
    if series_num > 30:
        break

# ══════════════════════════════════════════════════════════════════════════════
# PRINT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Running Length Series — Top Bars")

for s_idx, series_bars in enumerate(all_series):
    sn = s_idx + 1
    st.markdown(f"### R{sn} Series")

    if sn == 1:
        print_series_table(series_bars)
    else:
        # Group by parent (all chars of label except the last suffix letter)
        seen = {}
        for bar in series_bars:
            # Parent label: strip "R{sn}" prefix and last letter to get parent suffix
            parent_sfx = bar["suffix"][:-1]
            if parent_sfx not in seen:
                seen[parent_sfx] = []
            seen[parent_sfx].append(bar)

        for parent_sfx, group in seen.items():
            # Find parent bar in previous series
            prev = all_series[s_idx - 1]
            parent_bar = next((b for b in prev if b["suffix"] == parent_sfx), None)
            if parent_bar:
                loc = f"Span {parent_bar['span_idx']+1} left zone"
                st.markdown(f"**Splicing with {parent_bar['label']}** *(terminated at {loc})*")
            print_series_table(group)
            st.markdown("")

st.markdown("---")
if st.button("Confirm →"):
    st.session_state["geometry_confirmed"] = True
    st.success("Confirmed! Ready for the next step.")
