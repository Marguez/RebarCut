"""
BEAM REBAR CUTTING OPTIMIZER — Top Bars Running Length Series
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

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — REBAR PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Rebar Parameters")
c1, c2 = st.columns(2)
with c1: Db  = st.number_input("Db — Rebar diameter (mm)",    min_value=6,   max_value=50,   value=25,  step=1)
with c2: Anc = st.number_input("Anc — Anchorage length (mm)", min_value=100, max_value=2000, value=680, step=10)

prev_Db  = st.session_state.get("prev_Db",  Db)
prev_Anc = st.session_state.get("prev_Anc", Anc)
if (Db != prev_Db) or (Anc != prev_Anc):
    st.session_state["Hk_val"]  = 12 * Db
    st.session_state["Emb_val"] = Anc - 12 * Db
    st.session_state["prev_Db"]  = Db
    st.session_state["prev_Anc"] = Anc
if "Hk_val"  not in st.session_state: st.session_state["Hk_val"]  = 12 * Db
if "Emb_val" not in st.session_state: st.session_state["Emb_val"] = Anc - 12 * Db

c3, c4 = st.columns(2)
with c3:
    Hk = st.number_input(f"Hk (mm)  *(default: 12×Db = {12*Db})*", min_value=0, max_value=2000,
                         value=st.session_state["Hk_val"], step=10, key="Hk_input")
    st.session_state["Hk_val"] = Hk
with c4:
    Emb = st.number_input(f"Emb (mm)  *(default: Anc−Hk = {Anc - 12*Db})*", min_value=0, max_value=2000,
                          value=st.session_state["Emb_val"], step=10, key="Emb_input")
    st.session_state["Emb_val"] = Emb

st.markdown("**Lap Splice Lengths**")
c1, c2 = st.columns(2)
with c1: LapT = st.number_input("LapT — Top (mm)",    min_value=100, max_value=3000, value=800, step=10)
with c2: LapB = st.number_input("LapB — Bottom (mm)", min_value=100, max_value=3000, value=650, step=10)

st.markdown("**Splice Zones** *(fraction of clear span)*")
c1, c2 = st.columns(2)
with c1:
    st.markdown("*Top*")
    SplTEx = st.number_input("SplTEx — Exterior", min_value=0.0, max_value=1.0, value=0.25, step=0.01, format="%.2f")
    SplTIn = st.number_input("SplTIn — Interior", min_value=0.0, max_value=1.0, value=0.33, step=0.01, format="%.2f")
with c2:
    st.markdown("*Bottom*")
    SplBEx = st.number_input("SplBEx — Exterior", min_value=0.0, max_value=1.0, value=0.20, step=0.01, format="%.2f")
    SplBIn = st.number_input("SplBIn — Interior", min_value=0.0, max_value=1.0, value=0.20, step=0.01, format="%.2f")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — GEOMETRY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Structure Geometry")
no_spans = int(st.number_input("Number of spans", min_value=1, max_value=20, value=2, step=1))
n_cols = no_spans + 1

if "col_widths"   not in st.session_state or len(st.session_state["col_widths"])   != n_cols:    st.session_state["col_widths"]   = [400]  * n_cols
if "span_lengths" not in st.session_state or len(st.session_state["span_lengths"]) != no_spans: st.session_state["span_lengths"] = [6000] * no_spans

col_widths   = list(st.session_state["col_widths"])
span_lengths = list(st.session_state["span_lengths"])

h1, h2, h3 = st.columns([1, 2, 1])
h1.markdown("**Column**"); h2.markdown("**Span Length (mm)**"); h3.markdown("**Column**")
for i in range(no_spans):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: col_widths[i]   = st.number_input(f"C{i+1} (mm)", min_value=100, max_value=3000, value=col_widths[i],   step=50,  key=f"cw_{i}")
    with c2: span_lengths[i] = st.number_input(f"L{i+1} (mm)", min_value=500, max_value=50000,value=span_lengths[i], step=100, key=f"sl_{i}")
    if i == no_spans - 1:
        with c3: col_widths[n_cols-1] = st.number_input(f"C{n_cols} (mm)", min_value=100, max_value=3000, value=col_widths[n_cols-1], step=50, key=f"cw_{n_cols-1}")

st.session_state["col_widths"]   = col_widths
st.session_state["span_lengths"] = span_lengths

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — CLEAR SPANS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Clear Span Lengths")
clear_spans = [span_lengths[i] - 0.5*col_widths[i] - 0.5*col_widths[i+1] for i in range(no_spans)]

h1, h2, h3, h4 = st.columns([1, 2, 2, 2])
h1.markdown("**Span**"); h2.markdown("**L (mm)**"); h3.markdown("**−0.5C−0.5C**"); h4.markdown("**Clear S (mm)**")
for i in range(no_spans):
    ded = 0.5*col_widths[i] + 0.5*col_widths[i+1]
    r1,r2,r3,r4 = st.columns([1,2,2,2])
    r1.write(f"S{i+1}"); r2.write(f"{span_lengths[i]:,}"); r3.write(f"− {ded:,.0f}"); r4.write(f"**{clear_spans[i]:,.0f}**")

st.markdown("---")
st.metric("Total Beam Length", f"{sum(col_widths)+sum(span_lengths):,} mm")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — SPLICE ZONES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Splice Zones")

top_zones, bot_zones = [], []
for i in range(no_spans):
    S = clear_spans
    tl = SplTEx*S[0]          if i==0          else SplTIn*max(S[i-1],S[i])
    tr = SplTEx*S[no_spans-1] if i==no_spans-1 else SplTIn*max(S[i],  S[i+1])
    bl = SplBEx*S[0]          if i==0          else SplBIn*max(S[i-1],S[i])
    br = SplBEx*S[no_spans-1] if i==no_spans-1 else SplBIn*max(S[i],  S[i+1])
    top_zones.append({"left": tl, "right": tr})
    bot_zones.append({"left": bl, "right": br})

st.markdown("**Top Bars**")
h1,h2,h3 = st.columns([1,2,2]); h1.markdown("**Span**"); h2.markdown("**Left (mm)**"); h3.markdown("**Right (mm)**")
for i in range(no_spans):
    r1,r2,r3 = st.columns([1,2,2]); r1.write(f"S{i+1}"); r2.write(f"{top_zones[i]['left']:,.0f}"); r3.write(f"{top_zones[i]['right']:,.0f}")

st.markdown("**Bottom Bars**")
h1,h2,h3 = st.columns([1,2,2]); h1.markdown("**Span**"); h2.markdown("**Left (mm)**"); h3.markdown("**Right (mm)**")
for i in range(no_spans):
    r1,r2,r3 = st.columns([1,2,2]); r1.write(f"S{i+1}"); r2.write(f"{bot_zones[i]['left']:,.0f}"); r3.write(f"{bot_zones[i]['right']:,.0f}")

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
last  = no_spans - 1

def ceiling_com(rl):
    for cl in sorted(com_lengths):
        if cl >= rl: return cl
    return None

def get_waste(rl):
    cl = ceiling_com(rl)
    return cl, (cl - rl) if cl is not None else None

def print_table(rows):
    h1,h2,h3,h4,h5 = st.columns([1.5,2,2,2,2])
    h1.markdown("**Label**"); h2.markdown("**Length (mm)**")
    h3.markdown("**Com. Length (mm)**"); h4.markdown("**Waste (mm)**"); h5.markdown("**Cumul. Waste (mm)**")
    for r in rows:
        c1,c2,c3,c4,c5 = st.columns([1.5,2,2,2,2])
        lbl = f"{r['label']}*" if r["is_terminal"] else r["label"]
        c1.write(lbl); c2.write(f"{r['rl']:,.0f}")
        if r["cl"] is None:
            c3.write("**EXCEEDED**"); c4.write("—"); c5.write("—")
        else:
            c3.write(f"{r['cl']:,.0f}"); c4.write(f"{r['waste']:,.0f}"); c5.write(f"{r['cum_waste']:,.0f}")

# ══════════════════════════════════════════════════════════════════════════════
# ENGINE
# ══════════════════════════════════════════════════════════════════════════════
#
# Each bar has TWO possible termination types:
#
#   MID  — ends at left_zone[q] + LapT of span q
#          Can be continued by next series
#          Generated for ALL q > p, including q == last
#          Stop iterating q if rl exceeds max_com (mark exceeded, still print)
#
#   TERM — ends at right hook: remainder_of_span[last] + Emb + Hk
#          Only generated AFTER the mid version of the last span
#          i.e. it is the NEXT sub-label after the mid-last option
#          Only generated if mid-last was NOT exceeded
#          If term itself exceeds max_com → mark exceeded, next series closes it
#
# Rule: never skip any step. Always write every running length in sequence.
# If exceeded → print it as EXCEEDED and stop that branch (no continuation).
# Continuation only happens from bars that fit within max_com.

def make_bar(label, rl, pcw, span_idx, is_terminal, suffix, parent_chain_rls=None):
    cl, w = get_waste(rl)
    cum_w = (pcw + w) if (pcw is not None and w is not None) else None
    chain_rls = (parent_chain_rls or []) + [rl]
    return {"label": label, "rl": rl, "cl": cl, "waste": w,
            "cum_waste": cum_w, "span_idx": span_idx,
            "is_terminal": is_terminal, "parent_cum_waste": pcw,
            "suffix": suffix, "chain_rls": chain_rls}

def children_of(parent, series_num):
    """
    Generate all child bars for a parent node.
    Parent terminated at left_zone[p] (mid) or is terminal (no children).
    """
    if parent["is_terminal"] or parent["cl"] is None:
        return []

    p      = parent["span_idx"]
    pcw    = parent["cum_waste"]
    psuffix = parent["suffix"]
    sn     = str(series_num)
    pchain = parent["chain_rls"]
    result = []
    sub    = 0   # sub-label index (A, B, C...)

    # ── Mid terminations: q = p+1 .. last ─────────────────────────────────────
    for q in range(p + 1, no_spans):
        # Distance from start of left_zone[p] to end of lap at left_zone[q]
        d = clear_spans[p] - top_zones[p]["left"]   # remainder of span p
        d += col_widths[p + 1]                       # column right of p
        for k in range(p + 1, q):
            d += clear_spans[k] + col_widths[k + 1]
        d += top_zones[q]["left"] + LapT

        lbl = f"R{sn}{psuffix}{ALPHA[sub]}"
        bar = make_bar(lbl, d, pcw, q, False, psuffix + ALPHA[sub], pchain)
        result.append(bar)
        sub += 1

        if bar["cl"] is None:
            # Exceeded max — stop exploring further q in this branch
            return result

    # ── Terminal option: only reachable after mid-last was NOT exceeded ────────
    # (if we get here, mid-last bar fit within max_com)
    # Distance from start of left_zone[p] all the way to right hook
    d = clear_spans[p] - top_zones[p]["left"]
    d += col_widths[p + 1]
    for k in range(p + 1, last):
        d += clear_spans[k] + col_widths[k + 1]
    d += clear_spans[last] + Emb + Hk

    lbl = f"R{sn}{psuffix}{ALPHA[sub]}"
    bar = make_bar(lbl, d, pcw, last, True, psuffix + ALPHA[sub], pchain)
    result.append(bar)

    return result


def children_of_last_mid(parent, series_num):
    """
    Special case: parent is a mid bar at the LAST span.
    The only child is the short terminal bar:
        S[last] - left_zone[last] + Emb + Hk
    """
    if parent["is_terminal"] or parent["cl"] is None:
        return []
    if parent["span_idx"] != last:
        return []

    pcw     = parent["cum_waste"]
    psuffix = parent["suffix"]
    sn      = str(series_num)
    pchain  = parent["chain_rls"]

    d = clear_spans[last] - top_zones[last]["left"] + Emb + Hk
    lbl = f"R{sn}{psuffix}A"
    bar = make_bar(lbl, d, pcw, last, True, psuffix + "A", pchain)
    return [bar]


# ── Build R1 ──────────────────────────────────────────────────────────────────
r1_nodes = []
sub = 0

for j in range(no_spans):
    # Mid termination at left_zone[j]
    d = Emb
    for k in range(j): d += clear_spans[k] + col_widths[k + 1]
    d_mid = Hk + d + top_zones[j]["left"] + LapT

    lbl = f"R1{ALPHA[sub]}"
    bar = make_bar(lbl, d_mid, 0, j, False, ALPHA[sub])
    r1_nodes.append(bar)
    sub += 1

    if bar["cl"] is None:
        break   # exceeded, stop

# After all mid options, if the last mid bar was NOT exceeded and reached last span,
# add the terminal bar as the next R1 option
last_mid = next((b for b in reversed(r1_nodes) if not b["is_terminal"]), None)
if last_mid and last_mid["cl"] is not None and last_mid["span_idx"] == last:
    d = Emb
    for k in range(last): d += clear_spans[k] + col_widths[k + 1]
    d_term = Hk + d + clear_spans[last] + Emb + Hk
    lbl = f"R1{ALPHA[sub]}"
    bar = make_bar(lbl, d_term, 0, last, True, ALPHA[sub])
    r1_nodes.append(bar)

all_series = [r1_nodes]

# ── Build higher series ───────────────────────────────────────────────────────
series_num   = 2
parent_layer = r1_nodes

while True:
    new_nodes = []

    for parent in parent_layer:
        if parent["is_terminal"] or parent["cl"] is None:
            continue

        if parent["span_idx"] == last:
            # Parent is a mid bar at last span — only short terminal child
            kids = children_of_last_mid(parent, series_num)
        else:
            kids = children_of(parent, series_num)

        new_nodes.extend(kids)

    if not new_nodes:
        break

    all_series.append(new_nodes)
    parent_layer = new_nodes
    series_num  += 1
    if series_num > 30: break

# ══════════════════════════════════════════════════════════════════════════════
# PRINT ALL SERIES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Running Length Series — Top Bars")

for s_idx, series_bars in enumerate(all_series):
    sn = s_idx + 1
    st.markdown(f"### R{sn} Series")

    if sn == 1:
        print_table(series_bars)
    else:
        # Group by parent suffix
        groups = {}
        for bar in series_bars:
            psuffix = bar["suffix"][:-1]
            groups.setdefault(psuffix, []).append(bar)

        for psuffix, group in groups.items():
            prev_layer = all_series[s_idx - 1]
            parent_bar = next((b for b in prev_layer if b["suffix"] == psuffix), None)
            if parent_bar:
                st.markdown(f"**Splicing with {parent_bar['label']}**  *(Span {parent_bar['span_idx']+1} left zone)*")
            print_table(group)
            st.markdown("")

st.markdown("---")
if st.button("Confirm →"):
    st.success("Confirmed! Ready for the next step.")
