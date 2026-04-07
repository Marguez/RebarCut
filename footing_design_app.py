"""
BEAM REBAR CUTTING OPTIMIZER — Top & Bottom Bars Running Length Series
"""
import streamlit as st
import pandas as pd

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
com_lengths   = tuple(l * 1000 for l in com_lengths_m)   # tuple for hashability
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
if "beam_depths"  not in st.session_state or len(st.session_state["beam_depths"])  != no_spans: st.session_state["beam_depths"]  = [400]  * no_spans

col_widths   = list(st.session_state["col_widths"])
span_lengths = list(st.session_state["span_lengths"])
beam_depths  = list(st.session_state["beam_depths"])

h1, h2, h3, h4 = st.columns([1, 2, 1.5, 1])
h1.markdown("**Column**"); h2.markdown("**Span Length (mm)**"); h3.markdown("**Beam Depth D (mm)**"); h4.markdown("**Column**")
for i in range(no_spans):
    c1, c2, c3, c4 = st.columns([1, 2, 1.5, 1])
    with c1: col_widths[i]   = st.number_input(f"C{i+1} (mm)", min_value=100, max_value=3000,  value=col_widths[i],   step=50,  key=f"cw_{i}")
    with c2: span_lengths[i] = st.number_input(f"L{i+1} (mm)", min_value=500, max_value=50000, value=span_lengths[i], step=100, key=f"sl_{i}")
    with c3: beam_depths[i]  = st.number_input(f"D{i+1} (mm)", min_value=100, max_value=3000,  value=beam_depths[i],  step=50,  key=f"bd_{i}")
    if i == no_spans - 1:
        with c4: col_widths[n_cols-1] = st.number_input(f"C{n_cols} (mm)", min_value=100, max_value=3000, value=col_widths[n_cols-1], step=50, key=f"cw_{n_cols-1}")

st.session_state["col_widths"]   = col_widths
st.session_state["span_lengths"] = span_lengths
st.session_state["beam_depths"]  = beam_depths

# ══════════════════════════════════════════════════════════════════════════════
# RUN BUTTON
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
if st.button("▶ Run Optimization", type="primary"):
    st.session_state["run_optimization"] = True

if not st.session_state.get("run_optimization", False):
    st.info("Fill in all inputs above, then click **▶ Run Optimization** to compute.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — CLEAR SPANS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Clear Span Lengths")
clear_spans = tuple(span_lengths[i] - 0.5*col_widths[i] - 0.5*col_widths[i+1] for i in range(no_spans))

rows_cs = {"Span": [f"S{i+1}" for i in range(no_spans)],
           "L (mm)": [f"{span_lengths[i]:,.2f}" for i in range(no_spans)],
           "− 0.5C − 0.5C (mm)": [f"− {0.5*col_widths[i]+0.5*col_widths[i+1]:,.2f}" for i in range(no_spans)],
           "Clear S (mm)": [f"{clear_spans[i]:,.2f}" for i in range(no_spans)]}
st.dataframe(pd.DataFrame(rows_cs), hide_index=True, use_container_width=False)
st.metric("Total Beam Length", f"{sum(col_widths)+sum(span_lengths):,.2f} mm")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — SPLICE ZONES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Splice Zones")

top_zones = []
bot_zones = []
for i in range(no_spans):
    S = clear_spans
    tl = SplTEx*S[0]          if i==0          else SplTIn*max(S[i-1],S[i])
    tr = SplTEx*S[no_spans-1] if i==no_spans-1 else SplTIn*max(S[i],  S[i+1])
    bl = SplBEx*S[0]          if i==0          else SplBIn*max(S[i-1],S[i])
    br = SplBEx*S[no_spans-1] if i==no_spans-1 else SplBIn*max(S[i],  S[i+1])
    top_zones.append({"left": tl, "right": tr})
    bot_zones.append({"left": bl, "right": br})

top_zones = tuple(top_zones)
bot_zones = tuple(bot_zones)

st.markdown("**Top Bars**")
st.dataframe(pd.DataFrame({
    "Span":       [f"S{i+1}" for i in range(no_spans)],
    "Left (mm)":  [f"{top_zones[i]['left']:,.2f}"  for i in range(no_spans)],
    "Right (mm)": [f"{top_zones[i]['right']:,.2f}" for i in range(no_spans)],
}), hide_index=True, use_container_width=False)

st.markdown("**Bottom Bars**")
st.dataframe(pd.DataFrame({
    "Span":       [f"S{i+1}" for i in range(no_spans)],
    "Left (mm)":  [f"{bot_zones[i]['left']:,.2f}"  for i in range(no_spans)],
    "Right (mm)": [f"{bot_zones[i]['right']:,.2f}" for i in range(no_spans)],
}), hide_index=True, use_container_width=False)

# ══════════════════════════════════════════════════════════════════════════════
# PURE COMPUTATION HELPERS  (no st.* calls — safe to cache)
# ══════════════════════════════════════════════════════════════════════════════
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def _ceiling_com(rl, com_lengths):
    for cl in com_lengths:
        if cl >= rl: return cl
    return None

def _get_waste(rl, com_lengths):
    cl = _ceiling_com(rl, com_lengths)
    return cl, (cl - rl) if cl is not None else None

def _make_bar(label, rl, pcw, span_idx, zone_side, is_terminal, suffix,
              com_lengths, parent_chain_rls=None, parent_chain_wastes=None):
    cl, w = _get_waste(rl, com_lengths)
    cum_w = (pcw + w) if (pcw is not None and w is not None) else None
    chain_rls    = (parent_chain_rls    or ()) + (rl,)
    chain_wastes = (parent_chain_wastes or ()) + (w,)
    return {"label": label, "rl": rl, "cl": cl, "waste": w,
            "cum_waste": cum_w, "span_idx": span_idx, "zone_side": zone_side,
            "is_terminal": is_terminal, "parent_cum_waste": pcw,
            "suffix": suffix, "chain_rls": chain_rls, "chain_wastes": chain_wastes}

# ── Top bar engine ─────────────────────────────────────────────────────────────
def _top_children_of(parent, sn, no_spans, last, clear_spans, col_widths,
                     top_zones, LapT, Emb, Hk, com_lengths):
    if parent["is_terminal"] or parent["cl"] is None: return []
    p=parent["span_idx"]; pcw=parent["cum_waste"]; psuffix=parent["suffix"]
    prl=parent["chain_rls"]; pwt=parent["chain_wastes"]
    result=[]; sub=0
    for q in range(p+1, no_spans):
        d = clear_spans[p] - top_zones[p]["left"] + col_widths[p+1]
        for k in range(p+1, q): d += clear_spans[k] + col_widths[k+1]
        d += top_zones[q]["left"] + LapT
        bar = _make_bar(f"R{sn}{psuffix}{ALPHA[sub]}", d, pcw, q, "left",
                        False, psuffix+ALPHA[sub], com_lengths, prl, pwt)
        result.append(bar); sub+=1
        if bar["cl"] is None: return result
    # Terminal
    d = clear_spans[p] - top_zones[p]["left"] + col_widths[p+1]
    for k in range(p+1, last): d += clear_spans[k] + col_widths[k+1]
    d += clear_spans[last] + Emb + Hk
    bar = _make_bar(f"R{sn}{psuffix}{ALPHA[sub]}", d, pcw, last, "terminal",
                    True, psuffix+ALPHA[sub], com_lengths, prl, pwt)
    result.append(bar)
    return result

def _top_children_last_mid(parent, sn, last, clear_spans, top_zones, Emb, Hk, com_lengths):
    if parent["is_terminal"] or parent["cl"] is None or parent["span_idx"]!=last: return []
    pcw=parent["cum_waste"]; psuffix=parent["suffix"]
    prl=parent["chain_rls"]; pwt=parent["chain_wastes"]
    d = clear_spans[last] - top_zones[last]["left"] + Emb + Hk
    return [_make_bar(f"R{sn}{psuffix}A", d, pcw, last, "terminal",
                      True, psuffix+"A", com_lengths, prl, pwt)]

@st.cache_data(show_spinner="Computing top bar series…")
def build_top_series(no_spans, clear_spans, col_widths, top_zones,
                     LapT, Emb, Hk, com_lengths):
    last = no_spans - 1
    r1=[]; sub=0
    for j in range(no_spans):
        d = Emb
        for k in range(j): d += clear_spans[k] + col_widths[k+1]
        rl = Hk + d + top_zones[j]["left"] + LapT
        bar = _make_bar(f"R1{ALPHA[sub]}", rl, 0, j, "left", False,
                        ALPHA[sub], com_lengths, None, None)
        r1.append(bar); sub+=1
        if bar["cl"] is None: break
    last_mid = next((b for b in reversed(r1) if not b["is_terminal"]), None)
    if last_mid and last_mid["cl"] is not None and last_mid["span_idx"]==last:
        d = Emb
        for k in range(last): d += clear_spans[k] + col_widths[k+1]
        rl = Hk + d + clear_spans[last] + Emb + Hk
        bar = _make_bar(f"R1{ALPHA[sub]}", rl, 0, last, "terminal", True,
                        ALPHA[sub], com_lengths, last_mid["chain_rls"], last_mid["chain_wastes"])
        r1.append(bar)
    series=[r1]; parent_layer=r1; sn=2
    while True:
        new=[]
        for parent in parent_layer:
            if parent["is_terminal"] or parent["cl"] is None: continue
            if parent["span_idx"]==last:
                kids = _top_children_last_mid(parent, sn, last, clear_spans,
                                              top_zones, Emb, Hk, com_lengths)
            else:
                kids = _top_children_of(parent, sn, no_spans, last, clear_spans,
                                        col_widths, top_zones, LapT, Emb, Hk, com_lengths)
            new.extend(kids)
        if not new: break
        series.append(new); parent_layer=new; sn+=1
        if sn > 8: break   # cap at 8 series
    return series

# ── Bottom bar engine ──────────────────────────────────────────────────────────
def _right_stop_fn(i, clear_spans, bot_zones, beam_depths, LapB):
    zone_stop = bot_zones[i]["right"] - LapB
    two_d     = 2 * beam_depths[i]
    remainder = max(zone_stop, two_d)
    return clear_spans[i] - remainder, remainder

def _right_remainder_fn(i, bot_zones, beam_depths, LapB):
    return max(bot_zones[i]["right"] - LapB, 2 * beam_depths[i])

def _dist_bot_to_hook(p_span, p_remainder, col_widths, clear_spans, last, Emb, Hk):
    d = p_remainder + col_widths[p_span+1]
    for k in range(p_span+1, last): d += clear_spans[k] + col_widths[k+1]
    d += clear_spans[last] + Emb + Hk
    return d

def _dist_between_bot(p_span, p_side, p_rem, q_span, q_side,
                      clear_spans, col_widths, bot_zones, beam_depths, LapB):
    if q_span==p_span and p_side=="left" and q_side=="right":
        stop_dist, _ = _right_stop_fn(p_span, clear_spans, bot_zones, beam_depths, LapB)
        return stop_dist - 2*beam_depths[p_span]
    d = p_rem + col_widths[p_span+1]
    for k in range(p_span+1, q_span): d += clear_spans[k] + col_widths[k+1]
    if q_side=="left":
        d += 2*beam_depths[q_span] + LapB
    else:
        stop_dist, _ = _right_stop_fn(q_span, clear_spans, bot_zones, beam_depths, LapB)
        d += stop_dist
    return d

def _bot_children_of(parent, sn, no_spans, last, clear_spans, col_widths,
                     bot_zones, beam_depths, LapB, Emb, Hk, com_lengths):
    if parent["is_terminal"] or parent["cl"] is None: return []
    p_span=parent["span_idx"]; p_side=parent["zone_side"]
    pcw=parent["cum_waste"]; psuffix=parent["suffix"]
    prl=parent["chain_rls"]; pwt=parent["chain_wastes"]
    p_rem = (clear_spans[p_span] - 2*beam_depths[p_span] if p_side=="left"
             else _right_remainder_fn(p_span, bot_zones, beam_depths, LapB))
    result=[]; sub=0
    points=[]
    if p_side=="left": points.append((p_span,"right"))
    for q in range(p_span+1, no_spans):
        points.append((q,"left")); points.append((q,"right"))
    for (q_span, q_side) in points:
        d = _dist_between_bot(p_span, p_side, p_rem, q_span, q_side,
                              clear_spans, col_widths, bot_zones, beam_depths, LapB)
        bar = _make_bar(f"R{sn}{psuffix}{ALPHA[sub]}", d, pcw, q_span, q_side,
                        False, psuffix+ALPHA[sub], com_lengths, prl, pwt)
        result.append(bar); sub+=1
        if bar["cl"] is None: return result
    if p_span < last:
        d = _dist_bot_to_hook(p_span, p_rem, col_widths, clear_spans, last, Emb, Hk)
        bar = _make_bar(f"R{sn}{psuffix}{ALPHA[sub]}", d, pcw, last, "terminal",
                        True, psuffix+ALPHA[sub], com_lengths, prl, pwt)
        result.append(bar)
    return result

def _bot_children_last(parent, sn, last, clear_spans, col_widths,
                       bot_zones, beam_depths, LapB, Emb, Hk, com_lengths):
    if parent["is_terminal"] or parent["cl"] is None or parent["span_idx"]!=last: return []
    p_side=parent["zone_side"]; pcw=parent["cum_waste"]; psuffix=parent["suffix"]
    prl=parent["chain_rls"]; pwt=parent["chain_wastes"]
    p_rem = (clear_spans[last] - 2*beam_depths[last] if p_side=="left"
             else _right_remainder_fn(last, bot_zones, beam_depths, LapB))
    result=[]; sub=0
    if p_side=="left":
        d = _dist_between_bot(last, "left", p_rem, last, "right",
                              clear_spans, col_widths, bot_zones, beam_depths, LapB)
        bar = _make_bar(f"R{sn}{psuffix}{ALPHA[sub]}", d, pcw, last, "right",
                        False, psuffix+ALPHA[sub], com_lengths, prl, pwt)
        result.append(bar); sub+=1
        if bar["cl"] is None: return result
    term_d = p_rem + Emb + Hk
    bar = _make_bar(f"R{sn}{psuffix}{ALPHA[sub]}", term_d, pcw, last, "terminal",
                    True, psuffix+ALPHA[sub], com_lengths, prl, pwt)
    result.append(bar)
    return result

@st.cache_data(show_spinner="Computing bottom bar series…")
def build_bot_series(no_spans, clear_spans, col_widths, bot_zones, beam_depths,
                     LapB, Emb, Hk, com_lengths):
    last=no_spans-1; r1=[]; sub=0
    for i in range(no_spans):
        d = Emb
        for k in range(i): d += clear_spans[k] + col_widths[k+1]
        rl = Hk + d + 2*beam_depths[i] + LapB
        bar = _make_bar(f"R1{ALPHA[sub]}", rl, 0, i, "left", False,
                        ALPHA[sub], com_lengths, None, None)
        r1.append(bar); sub+=1
        if bar["cl"] is None: break
        stop_dist, _ = _right_stop_fn(i, clear_spans, bot_zones, beam_depths, LapB)
        rl = Hk + d + stop_dist
        bar = _make_bar(f"R1{ALPHA[sub]}", rl, 0, i, "right", False,
                        ALPHA[sub], com_lengths, None, None)
        r1.append(bar); sub+=1
        if bar["cl"] is None: break
    last_mid = next((b for b in reversed(r1) if not b["is_terminal"] and b["cl"] is not None), None)
    if last_mid:
        lm_span=last_mid["span_idx"]; lm_side=last_mid["zone_side"]
        p_rem = (clear_spans[lm_span] - 2*beam_depths[lm_span] if lm_side=="left"
                 else _right_remainder_fn(lm_span, bot_zones, beam_depths, LapB))
        d = (_dist_bot_to_hook(lm_span, p_rem, col_widths, clear_spans, last, Emb, Hk)
             if lm_span < last else p_rem + Emb + Hk)
        bar = _make_bar(f"R1{ALPHA[sub]}", d, 0, last, "terminal", True,
                        ALPHA[sub], com_lengths, last_mid["chain_rls"], last_mid["chain_wastes"])
        r1.append(bar)
    series=[r1]; parent_layer=r1; sn=2
    while True:
        new=[]
        for parent in parent_layer:
            if parent["is_terminal"] or parent["cl"] is None: continue
            if parent["span_idx"]==last:
                kids = _bot_children_last(parent, sn, last, clear_spans, col_widths,
                                          bot_zones, beam_depths, LapB, Emb, Hk, com_lengths)
            else:
                kids = _bot_children_of(parent, sn, no_spans, last, clear_spans, col_widths,
                                        bot_zones, beam_depths, LapB, Emb, Hk, com_lengths)
            new.extend(kids)
        if not new: break
        series.append(new); parent_layer=new; sn+=1
        if sn > 8: break
    return series

# ══════════════════════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def series_to_df(rows):
    """Convert a list of bar dicts to a display DataFrame."""
    data = []
    for r in rows:
        lbl = f"{r['label']}*" if r["is_terminal"] else r["label"]
        if r["cl"] is None:
            data.append({"Label": lbl, "Length (mm)": f"{r['rl']:,.2f}",
                         "Com. Length (mm)": "EXCEEDED", "Waste (mm)": "—", "Cumul. Waste (mm)": "—"})
        else:
            data.append({"Label": lbl, "Length (mm)": f"{r['rl']:,.2f}",
                         "Com. Length (mm)": f"{r['cl']:,.2f}",
                         "Waste (mm)": f"{r['waste']:,.2f}",
                         "Cumul. Waste (mm)": f"{r['cum_waste']:,.2f}"})
    return pd.DataFrame(data)

def print_all_series(all_series, zone_label_fn=None):
    for s_idx, series_bars in enumerate(all_series):
        sn = s_idx + 1
        st.markdown(f"### R{sn} Series")
        if sn == 1:
            st.dataframe(series_to_df(series_bars), hide_index=True, use_container_width=True)
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
                st.dataframe(series_to_df(group), hide_index=True, use_container_width=True)
                st.markdown("")

def optimize_chain(chain_rls, chain_wastes):
    best = None
    for i, wi in enumerate(chain_wastes):
        if wi is None or wi <= 0: continue
        for j, lj in enumerate(chain_rls):
            if j == i: continue
            wj = chain_wastes[j]
            if wj is None: continue
            if wi >= lj:
                saving = lj + wj
                if best is None or saving > best["saving"]:
                    best = {"i": i, "j": j, "wi_original": wi, "lj": lj,
                            "wj": wj, "remainder": wi - lj, "saving": saving}
    return best

def print_summary(terminals, title, top_n=None):
    if title: st.markdown(f"**{title}**")
    st.markdown("_\\* = terminal bar. All values in metres (m)._")
    if not terminals:
        st.info("No complete chains found."); return
    enhanced = []
    for bar in terminals:
        reuse   = optimize_chain(bar["chain_rls"], bar["chain_wastes"])
        opt_cum = bar["cum_waste"] - reuse["saving"] if reuse else bar["cum_waste"]
        enhanced.append({**bar, "reuse": reuse, "opt_cum_waste": opt_cum})
    enhanced.sort(key=lambda b: b["opt_cum_waste"])
    rows = enhanced[:top_n] if top_n else enhanced

    data = []
    for b in rows:
        rls=b["chain_rls"]; wastes=b["chain_wastes"]; reuse=b["reuse"]
        len_str  = " — ".join(f"{rl/1000:.2f}" for rl in rls)
        orig_str = " — ".join(f"{w/1000:.2f}" if w is not None else "—" for w in wastes)
        if reuse:
            i,j = reuse["i"], reuse["j"]
            red_parts = []
            for k, w in enumerate(wastes):
                if k==i:   red_parts.append(f"WR{i+1}={reuse['remainder']/1000:.2f}")
                elif k==j: red_parts.append(f"W{j+1} elim.")
                else:      red_parts.append(f"{w/1000:.2f}" if w is not None else "—")
            red_str = " — ".join(red_parts)
        else:
            red_str = orig_str
        data.append({"Label": f"{b['label']}*",
                     "Component Lengths (m)": len_str,
                     "Original Wastes (m)": orig_str,
                     "Reduced Wastes (m)": red_str,
                     "Opt. Cum. Waste (m)": f"{b['opt_cum_waste']/1000:.2f}"})
    st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# BUILD
# ══════════════════════════════════════════════════════════════════════════════
# Pass all inputs explicitly as tuples/scalars so cache keys work correctly
top_series = build_top_series(
    no_spans, clear_spans, tuple(col_widths), top_zones,
    LapT, Emb, Hk, com_lengths)

bot_series = build_bot_series(
    no_spans, clear_spans, tuple(col_widths), bot_zones,
    tuple(beam_depths), LapB, Emb, Hk, com_lengths)

def collect_terminals(all_series):
    t = [b for s in all_series for b in s if b["is_terminal"] and b["cl"] is not None]
    t.sort(key=lambda b: b["cum_waste"])
    return t

top_terminals = collect_terminals(top_series)
bot_terminals = collect_terminals(bot_series)

# ══════════════════════════════════════════════════════════════════════════════
# TOP-5 SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("⭐ Top 5 Best Cutting Combinations")
st.markdown("_Ranked by optimised cumulative waste._")
st.markdown("**Top Bars — Best 5**")
print_summary(top_terminals, "", top_n=5)
st.markdown("**Bottom Bars — Best 5**")
print_summary(bot_terminals, "", top_n=5)

# ══════════════════════════════════════════════════════════════════════════════
# FULL SERIES — TOP BARS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Running Length Series — Top Bars")
print_all_series(top_series, lambda b: f"*(Span {b['span_idx']+1} left zone)*")

# ══════════════════════════════════════════════════════════════════════════════
# FULL SERIES — BOTTOM BARS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Running Length Series — Bottom Bars")
def bot_zone_lbl(b):
    side = b["zone_side"]
    if side == "terminal": return ""
    return f"*(Span {b['span_idx']+1} {side} zone)*"
print_all_series(bot_series, bot_zone_lbl)

# ══════════════════════════════════════════════════════════════════════════════
# FULL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("Summary — All Complete Chains Ranked by Cumulative Waste")
st.markdown("#### Top Bars")
print_summary(top_terminals, "Top Bar Chains")
st.markdown("#### Bottom Bars")
print_summary(bot_terminals, "Bottom Bar Chains")

st.markdown("---")
if st.button("🔄 Reset — Change Inputs"):
    st.session_state["run_optimization"] = False
    st.rerun()
