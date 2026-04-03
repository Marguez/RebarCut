"""
BEAM REBAR CUTTING OPTIMIZER — Top & Bottom Bars Running Length Series
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
    r1.write(f"S{i+1}"); r2.write(f"{span_lengths[i]:,.2f}"); r3.write(f"− {ded:,.2f}"); r4.write(f"**{clear_spans[i]:,.2f}**")

st.markdown("---")
st.metric("Total Beam Length", f"{sum(col_widths)+sum(span_lengths):,.2f} mm")

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
    r1,r2,r3 = st.columns([1,2,2]); r1.write(f"S{i+1}"); r2.write(f"{top_zones[i]['left']:,.2f}"); r3.write(f"{top_zones[i]['right']:,.2f}")

st.markdown("**Bottom Bars**")
h1,h2,h3 = st.columns([1,2,2]); h1.markdown("**Span**"); h2.markdown("**Left (mm)**"); h3.markdown("**Right (mm)**")
for i in range(no_spans):
    r1,r2,r3 = st.columns([1,2,2]); r1.write(f"S{i+1}"); r2.write(f"{bot_zones[i]['left']:,.2f}"); r3.write(f"{bot_zones[i]['right']:,.2f}")

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

def make_bar(label, rl, pcw, span_idx, zone_side, is_terminal, suffix, parent_chain_rls=None, parent_chain_wastes=None):
    cl, w = get_waste(rl)
    cum_w = (pcw + w) if (pcw is not None and w is not None) else None
    chain_rls    = (parent_chain_rls    or []) + [rl]
    chain_wastes = (parent_chain_wastes or []) + [w]
    return {"label": label, "rl": rl, "cl": cl, "waste": w,
            "cum_waste": cum_w, "span_idx": span_idx, "zone_side": zone_side,
            "is_terminal": is_terminal, "parent_cum_waste": pcw,
            "suffix": suffix, "chain_rls": chain_rls, "chain_wastes": chain_wastes}

def print_table(rows):
    h1,h2,h3,h4,h5 = st.columns([1.5,2,2,2,2])
    h1.markdown("**Label**"); h2.markdown("**Length (mm)**")
    h3.markdown("**Com. Length (mm)**"); h4.markdown("**Waste (mm)**"); h5.markdown("**Cumul. Waste (mm)**")
    for r in rows:
        c1,c2,c3,c4,c5 = st.columns([1.5,2,2,2,2])
        lbl = f"{r['label']}*" if r["is_terminal"] else r["label"]
        c1.write(lbl); c2.write(f"{r['rl']:,.2f}")
        if r["cl"] is None:
            c3.write("**EXCEEDED**"); c4.write("—"); c5.write("—")
        else:
            c3.write(f"{r['cl']:,.2f}"); c4.write(f"{r['waste']:,.2f}"); c5.write(f"{r['cum_waste']:,.2f}")

def optimize_chain(chain_rls, chain_wastes):
    """
    Find the single best waste reuse across the chain.
    For each Wi, try Wi - Lj for all j != i.
    Condition: Wi >= Lj (waste fully covers that component length).
    Saving = commercial length of component j = Lj + Wj.
    Returns the best reuse dict, or None if no reuse possible.
    """
    best = None
    for i, wi in enumerate(chain_wastes):
        if wi is None or wi <= 0:
            continue
        for j, lj in enumerate(chain_rls):
            if j == i:
                continue
            wj = chain_wastes[j]
            if wj is None:
                continue
            if wi >= lj:                            # waste covers the component length
                saving = lj + wj                    # full commercial bar of j eliminated
                if best is None or saving > best["saving"]:
                    best = {
                        "i": i,                     # waste index being reused
                        "j": j,                     # component index being covered
                        "wi_original": wi,
                        "lj": lj,
                        "wj": wj,
                        "remainder": wi - lj,       # new waste for component i after reuse
                        "saving": saving,
                    }
    return best

def print_summary(terminals, title, top_n=None):
    if title:
        st.markdown(f"**{title}**")
    st.markdown("_\\* = terminal bar. All values in metres (m)._")
    if not terminals:
        st.info("No complete chains found."); return

    # Apply reuse optimization to each terminal for ranking
    enhanced = []
    for bar in terminals:
        reuse   = optimize_chain(bar["chain_rls"], bar["chain_wastes"])
        opt_cum = bar["cum_waste"] - reuse["saving"] if reuse else bar["cum_waste"]
        enhanced.append({**bar, "reuse": reuse, "opt_cum_waste": opt_cum})

    enhanced.sort(key=lambda b: b["opt_cum_waste"])
    rows = enhanced[:top_n] if top_n else enhanced

    h1, h2, h3, h4, h5 = st.columns([1.8, 2.8, 2.8, 2.8, 1.8])
    h1.markdown("**Label**")
    h2.markdown("**Component Lengths (m)**")
    h3.markdown("**Original Wastes (m)**")
    h4.markdown("**Reduced Wastes (m)**")
    h5.markdown("**Opt. Cum. Waste (m)**")

    for b in rows:
        rls    = b["chain_rls"]
        wastes = b["chain_wastes"]
        reuse  = b["reuse"]
        n      = len(rls)

        # Component lengths — unchanged
        len_str = " — ".join(f"{rl/1000:.2f}" for rl in rls)

        # Original wastes
        orig_str = " — ".join(
            f"{w/1000:.2f}" if w is not None else "—" for w in wastes
        )

        # Reduced wastes column:
        # - Wi becomes WRi = Wi - Lj  (show as bold with note)
        # - Wj is struck through (eliminated — covered by Wi)
        # - all others unchanged
        if reuse:
            i, j = reuse["i"], reuse["j"]
            red_parts = []
            for k, w in enumerate(wastes):
                if k == i:
                    red_parts.append(f"**{reuse['remainder']/1000:.2f}**")
                elif k == j:
                    red_parts.append(f"~~{w/1000:.2f}~~")
                else:
                    red_parts.append(f"{w/1000:.2f}" if w is not None else "—")
            reuse_note = (
                f"W{i+1}({reuse['wi_original']/1000:.2f}) covers "
                f"L{j+1}({reuse['lj']/1000:.2f}) → "
                f"WR{i+1}={reuse['remainder']/1000:.2f}, "
                f"W{j+1} eliminated"
            )
            red_str = " — ".join(red_parts) + f"  \n_{reuse_note}_"
        else:
            red_str = orig_str + "  \n_No reuse possible_"

        c1, c2, c3, c4, c5 = st.columns([1.8, 2.8, 2.8, 2.8, 1.8])
        c1.write(f"{b['label']}*")
        c2.write(len_str)
        c3.write(orig_str)
        c4.markdown(red_str)
        c5.write(f"{b['opt_cum_waste']/1000:.2f}")

# ══════════════════════════════════════════════════════════════════════════════
# TOP BAR ENGINE
# ══════════════════════════════════════════════════════════════════════════════
# Splice points: LEFT zone of each span (near column, over support)
# Each bar terminates at left_zone[q] + LapT
# Terminal: travels through last span to right hook

def top_children_of(parent, series_num):
    if parent["is_terminal"] or parent["cl"] is None:
        return []
    p       = parent["span_idx"]
    pcw     = parent["cum_waste"]
    psuffix = parent["suffix"]
    sn      = str(series_num)
    pchain_rls    = parent["chain_rls"]
    pchain_wastes = parent["chain_wastes"]
    result  = []
    sub     = 0

    for q in range(p + 1, no_spans):
        d  = clear_spans[p] - top_zones[p]["left"]
        d += col_widths[p + 1]
        for k in range(p + 1, q):
            d += clear_spans[k] + col_widths[k + 1]
        d += top_zones[q]["left"] + LapT
        lbl = f"R{sn}{psuffix}{ALPHA[sub]}"
        bar = make_bar(lbl, d, pcw, q, "left", False, psuffix+ALPHA[sub], pchain_rls, pchain_wastes)
        result.append(bar); sub += 1
        if bar["cl"] is None: return result

    # Terminal
    d  = clear_spans[p] - top_zones[p]["left"]
    d += col_widths[p + 1]
    for k in range(p + 1, last):
        d += clear_spans[k] + col_widths[k + 1]
    d += clear_spans[last] + Emb + Hk
    lbl = f"R{sn}{psuffix}{ALPHA[sub]}"
    bar = make_bar(lbl, d, pcw, last, "terminal", True, psuffix+ALPHA[sub], pchain_rls, pchain_wastes)
    result.append(bar)
    return result

def top_children_of_last_mid(parent, series_num):
    if parent["is_terminal"] or parent["cl"] is None or parent["span_idx"] != last: return []
    pcw=parent["cum_waste"]; psuffix=parent["suffix"]; sn=str(series_num)
    pchain_rls=parent["chain_rls"]; pchain_wastes=parent["chain_wastes"]
    d = clear_spans[last] - top_zones[last]["left"] + Emb + Hk
    lbl = f"R{sn}{psuffix}A"
    return [make_bar(lbl, d, pcw, last, "terminal", True, psuffix+"A", pchain_rls, pchain_wastes)]

def build_top_series():
    r1 = []; sub = 0
    for j in range(no_spans):
        d = Emb
        for k in range(j): d += clear_spans[k] + col_widths[k+1]
        rl = Hk + d + top_zones[j]["left"] + LapT
        lbl = f"R1{ALPHA[sub]}"
        bar = make_bar(lbl, rl, 0, j, "left", False, ALPHA[sub], None, None)
        r1.append(bar); sub += 1
        if bar["cl"] is None: break

    last_mid = next((b for b in reversed(r1) if not b["is_terminal"]), None)
    if last_mid and last_mid["cl"] is not None and last_mid["span_idx"] == last:
        d = Emb
        for k in range(last): d += clear_spans[k] + col_widths[k+1]
        rl = Hk + d + clear_spans[last] + Emb + Hk
        lbl = f"R1{ALPHA[sub]}"
        bar = make_bar(lbl, rl, 0, last, "terminal", True, ALPHA[sub], last_mid["chain_rls"], last_mid["chain_wastes"])
        r1.append(bar)

    series = [r1]; parent_layer = r1; sn = 2
    while True:
        new = []
        for parent in parent_layer:
            if parent["is_terminal"] or parent["cl"] is None: continue
            kids = top_children_of_last_mid(parent, sn) if parent["span_idx"] == last else top_children_of(parent, sn)
            new.extend(kids)
        if not new: break
        series.append(new); parent_layer = new; sn += 1
        if sn > 30: break
    return series

# ══════════════════════════════════════════════════════════════════════════════
# BOTTOM BAR ENGINE
# ══════════════════════════════════════════════════════════════════════════════
# Splice points: per span there are TWO — left zone (near left support) and
#                right zone (near right support), both at midspan side
#
# Splice point index: encoded as (span_idx, side) where side = "left" or "right"
#
# All points in order left-to-right:
#   (0,left), (0,right), (1,left), (1,right), ..., (last,left), (last,right)
#
# Distance from LEFT HOOK to each splice point:
#   (i, "left")  : Hk + Emb + [S0+C1+S1+C2+...+Si-1+Ci] + LapB
#                  i.e. traverse spans 0..i-1 fully, then just LapB into span i
#   (i, "right") : Hk + Emb + [S0+C1+...+Ci] + (Si - bot_zones[i]["right"]) + LapB
#                  i.e. traverse spans 0..i-1 fully, then most of span i up to right zone
#
# R1 series: bars starting from left hook, terminating at each splice point in order
#
# Higher series: bar starts at the beginning of a splice zone (left or right of span p)
#   From (p, "left"):
#     next point (p, "right"): (S[p] - bot_zones[p]["left"] - bot_zones[p]["right"]) + LapB
#     next point (q, "left") : (S[p] - bot_zones[p]["left"]) + C[p+1] + [interior] + LapB
#     next point (q, "right"): (S[p] - bot_zones[p]["left"]) + C[p+1] + [interior] + (S[q]-bot[q]["right"]) + LapB
#
#   From (p, "right"):
#     next point (p+1,"left") : bot_zones[p]["right"] + C[p+1] + LapB
#     next point (p+1,"right"): bot_zones[p]["right"] + C[p+1] + (S[p+1]-bot[p+1]["right"]) + LapB
#     next point (q,"left")   : bot_zones[p]["right"] + C[p+1] + S[p+1] + C[p+2] + ... + LapB
#     next point (q,"right")  : ... + (S[q]-bot[q]["right"]) + LapB
#
# Terminal (from any splice point): travel remaining spans to right hook
#   same as top bars: remainder_of_current_span + cols/spans + S[last] + Emb + Hk

def _dist_from_left_of_span_p_to_right_hook(p_span, p_side):
    """Distance from the LAP START of (p_span, p_side) to the right hook."""
    if p_side == "left":
        remainder = clear_spans[p_span] - bot_zones[p_span]["left"]
    else:  # "right" — lap starts at start of right zone
        remainder = bot_zones[p_span]["right"]

    d = remainder + col_widths[p_span + 1]
    for k in range(p_span + 1, last):
        d += clear_spans[k] + col_widths[k + 1]
    d += clear_spans[last] + Emb + Hk
    return d

def _dist_between_splice_points(p_span, p_side, q_span, q_side):
    """
    Distance of a bar that starts at the beginning of splice zone (p_span, p_side)
    and terminates at the end of the lap at (q_span, q_side).
    """
    # Start: beginning of (p_span, p_side)
    # End:   beginning of (q_span, q_side) + LapB

    if p_side == "left":
        remainder_p = clear_spans[p_span] - bot_zones[p_span]["left"]
    else:
        remainder_p = bot_zones[p_span]["right"]

    # Same span, right zone (only valid if p_side=="left" and q_side=="right" and q_span==p_span)
    if q_span == p_span and p_side == "left" and q_side == "right":
        d = (clear_spans[p_span] - bot_zones[p_span]["left"] - bot_zones[p_span]["right"]) + LapB
        return d

    # Travel remainder of p_span, then column, then interior spans up to q_span
    d = remainder_p + col_widths[p_span + 1]
    for k in range(p_span + 1, q_span):
        d += clear_spans[k] + col_widths[k + 1]

    # Into q_span
    if q_side == "left":
        d += LapB
    else:  # right zone
        d += (clear_spans[q_span] - bot_zones[q_span]["right"]) + LapB

    return d

def bot_children_of(parent, series_num):
    if parent["is_terminal"] or parent["cl"] is None: return []

    p_span  = parent["span_idx"]
    p_side  = parent["zone_side"]
    pcw     = parent["cum_waste"]
    psuffix = parent["suffix"]
    sn      = str(series_num)
    pchain_rls    = parent["chain_rls"]
    pchain_wastes = parent["chain_wastes"]
    result  = []
    sub     = 0

    # Generate all splice points to the right of (p_span, p_side) in order
    # Points: (p_span, "right") if p_side=="left", then (p_span+1,"left"),
    #         (p_span+1,"right"), (p_span+2,"left"), ... up to (last,"right")

    points = []
    if p_side == "left":
        points.append((p_span, "right"))
    for q in range(p_span + 1, no_spans):
        points.append((q, "left"))
        points.append((q, "right"))

    for (q_span, q_side) in points:
        d   = _dist_between_splice_points(p_span, p_side, q_span, q_side)
        lbl = f"R{sn}{psuffix}{ALPHA[sub]}"
        bar = make_bar(lbl, d, pcw, q_span, q_side, False, psuffix+ALPHA[sub], pchain_rls, pchain_wastes)
        result.append(bar); sub += 1
        if bar["cl"] is None: return result  # exceeded, stop

    # Terminal — from (p_span, p_side) to right hook
    if p_span < last:
        d   = _dist_from_left_of_span_p_to_right_hook(p_span, p_side)
        lbl = f"R{sn}{psuffix}{ALPHA[sub]}"
        bar = make_bar(lbl, d, pcw, last, "terminal", True, psuffix+ALPHA[sub], pchain_rls, pchain_wastes)
        result.append(bar)
    return result

def bot_children_of_last_zone(parent, series_num):
    """Parent is at (last, left) or (last, right) — only terminal child possible."""
    if parent["is_terminal"] or parent["cl"] is None: return []
    if parent["span_idx"] != last: return []

    pcw=parent["cum_waste"]; psuffix=parent["suffix"]; sn=str(series_num)
    pchain_rls=parent["chain_rls"]; pchain_wastes=parent["chain_wastes"]
    p_side = parent["zone_side"]

    if p_side == "left":
        # Right zone of last span is still reachable before terminal
        points = [("right",)]
    else:
        points = []

    result = []; sub = 0

    for (side,) in points:
        d   = _dist_between_splice_points(last, p_side, last, side)
        lbl = f"R{sn}{psuffix}{ALPHA[sub]}"
        bar = make_bar(lbl, d, pcw, last, side, False, psuffix+ALPHA[sub], pchain_rls, pchain_wastes)
        result.append(bar); sub += 1
        if bar["cl"] is None: return result

    # Terminal from last zone
    if p_side == "left":
        d = bot_zones[last]["right"] + Emb + Hk
    else:
        d = Emb + Hk   # already past right zone, just embed + hook
        # Actually: from right zone start to right hook
        d = bot_zones[last]["right"] + Emb + Hk

    # Correct: from (last, right) the remainder to hook = bot_zones[last]["right"] + Emb + Hk
    # From (last, left) if right zone was exceeded: short-cut terminal
    if p_side == "left":
        # terminal skipping right zone (right zone exceeded)
        d = clear_spans[last] - bot_zones[last]["left"] + Emb + Hk
    else:
        d = bot_zones[last]["right"] + Emb + Hk

    lbl = f"R{sn}{psuffix}{ALPHA[sub]}"
    bar = make_bar(lbl, d, pcw, last, "terminal", True, psuffix+ALPHA[sub], pchain_rls, pchain_wastes)
    result.append(bar)
    return result

def build_bot_series():
    # R1: left hook to each splice point in order
    r1 = []; sub = 0

    for i in range(no_spans):
        # Left zone of span i
        d = Emb
        for k in range(i): d += clear_spans[k] + col_widths[k+1]
        rl = Hk + d + LapB
        lbl = f"R1{ALPHA[sub]}"
        bar = make_bar(lbl, rl, 0, i, "left", False, ALPHA[sub], None, None)
        r1.append(bar); sub += 1
        if bar["cl"] is None: break

        # Right zone of span i
        rl = Hk + d + (clear_spans[i] - bot_zones[i]["right"]) + LapB
        lbl = f"R1{ALPHA[sub]}"
        bar = make_bar(lbl, rl, 0, i, "right", False, ALPHA[sub], None, None)
        r1.append(bar); sub += 1
        if bar["cl"] is None: break

    # Terminal from last valid mid bar
    last_mid = next((b for b in reversed(r1) if not b["is_terminal"] and b["cl"] is not None), None)
    if last_mid:
        lm_span = last_mid["span_idx"]; lm_side = last_mid["zone_side"]
        if lm_side == "left":
            remainder = clear_spans[lm_span] - bot_zones[lm_span]["left"]
        else:
            remainder = bot_zones[lm_span]["right"]
        d = remainder + col_widths[lm_span+1] if lm_span < last else (remainder if lm_side=="right" else clear_spans[last]-bot_zones[last]["left"])
        # Simpler: reuse helper if span < last
        if lm_span < last:
            d = _dist_from_left_of_span_p_to_right_hook(lm_span, lm_side)
        else:
            if lm_side == "left":
                d = clear_spans[last] - bot_zones[last]["left"] + Emb + Hk
            else:
                d = bot_zones[last]["right"] + Emb + Hk
        lbl = f"R1{ALPHA[sub]}"
        bar = make_bar(lbl, d, 0, last, "terminal", True, ALPHA[sub], last_mid["chain_rls"], last_mid["chain_wastes"])
        r1.append(bar)

    series = [r1]; parent_layer = r1; sn = 2
    while True:
        new = []
        for parent in parent_layer:
            if parent["is_terminal"] or parent["cl"] is None: continue
            if parent["span_idx"] == last:
                kids = bot_children_of_last_zone(parent, sn)
            else:
                kids = bot_children_of(parent, sn)
            new.extend(kids)
        if not new: break
        series.append(new); parent_layer = new; sn += 1
        if sn > 30: break
    return series

# ══════════════════════════════════════════════════════════════════════════════
# PRINT HELPER
# ══════════════════════════════════════════════════════════════════════════════
def print_all_series(all_series, zone_label_fn=None):
    for s_idx, series_bars in enumerate(all_series):
        sn = s_idx + 1
        st.markdown(f"### R{sn} Series")
        if sn == 1:
            print_table(series_bars)
        else:
            groups = {}
            for bar in series_bars:
                psuffix = bar["suffix"][:-1]
                groups.setdefault(psuffix, []).append(bar)
            for psuffix, group in groups.items():
                prev_layer = all_series[s_idx - 1]
                parent_bar = next((b for b in prev_layer if b["suffix"] == psuffix), None)
                if parent_bar:
                    zlbl = zone_label_fn(parent_bar) if zone_label_fn else ""
                    st.markdown(f"**Splicing with {parent_bar['label']}** {zlbl}")
                print_table(group)
                st.markdown("")

# ══════════════════════════════════════════════════════════════════════════════
# BUILD ALL SERIES
# ══════════════════════════════════════════════════════════════════════════════
top_series = build_top_series()
bot_series = build_bot_series()

def collect_terminals(all_series):
    t = [b for s in all_series for b in s if b["is_terminal"] and b["cl"] is not None]
    t.sort(key=lambda b: b["cum_waste"])
    return t

top_terminals = collect_terminals(top_series)
bot_terminals = collect_terminals(bot_series)

# ══════════════════════════════════════════════════════════════════════════════
# TOP-5 SUMMARY OF SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("⭐ Top 5 Best Cutting Combinations")
st.markdown("_Ranked by cumulative waste. Full details in the summary section below._")

st.markdown("**Top Bars — Best 5**")
print_summary(top_terminals, "", top_n=5)

st.markdown("**Bottom Bars — Best 5**")
print_summary(bot_terminals, "", top_n=5)

# ══════════════════════════════════════════════════════════════════════════════
# PRINT — TOP BARS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Running Length Series — Top Bars")
print_all_series(top_series, lambda b: f"*(Span {b['span_idx']+1} left zone)*")

# ══════════════════════════════════════════════════════════════════════════════
# PRINT — BOTTOM BARS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Running Length Series — Bottom Bars")
def bot_zone_lbl(b):
    side = b["zone_side"]
    if side == "terminal": return ""
    return f"*(Span {b['span_idx']+1} {side} zone)*"
print_all_series(bot_series, bot_zone_lbl)

# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Summary — All Complete Chains Ranked by Cumulative Waste")

st.markdown("#### Top Bars")
print_summary(top_terminals, "Top Bar Chains")

st.markdown("#### Bottom Bars")
print_summary(bot_terminals, "Bottom Bar Chains")

st.markdown("---")
if st.button("Confirm →"):
    st.success("Confirmed! Ready for the next step.")
