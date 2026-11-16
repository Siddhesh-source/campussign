"""CampusSign pitch deck, 10 slides, theme A (Public Record). Every element is a native shape."""
import sys, math
from kit import *
from pptx.enum.shapes import MSO_SHAPE
from slides_common import title_A, slide_trust, TAGLINE

TOTAL = 10


def label(s, t, x, y, w, txt, color=None):
    """Small mono caps label above a group."""
    text(s, x, y, w, 0.28, txt, t["semi"], 12, color or t["muted"])


def clock(s, cx, cy, d, color):
    circle(s, cx, cy, d, fill=t_bg(s), line=color, lw=1.25)
    line(s, cx, cy, cx, cy - d * 0.3, color, 1.25)
    line(s, cx, cy, cx + d * 0.24, cy, color, 1.25)


def bignum(s, t, x, y, w, num, unit, color, size=48):
    runs = [(num, t["head"], size, color)]
    if unit:
        runs.append((" " + unit, t["semi"], int(size * 0.5), color))
    return text(s, x, y, w, size / 72 * 1.3, [runs], t["head"], size, color)


_BG = {}
def t_bg(s):
    return _BG["bg"]


def paper_form(s, t, x, y, w, h):
    """The paper event-permission form Riya carries, drawn with native shapes."""
    rect(s, x, y, w, h, fill=t["panel"])
    rect(s, x + 0.18, y + 0.18, w - 0.36, h - 0.36, fill="FFFFFF", line=t["rule"], lw=1.0)
    ix, iw = x + 0.4, w - 0.8
    text(s, ix, y + 0.35, iw, 0.22, "EVENT PERMISSION FORM", t["mono"], 8, t["faint"], tracking=1.0)
    rect(s, ix, y + 0.62, 1.3, 0.06, fill=t["ink"])
    fields = [("Event", "Tech fest", None), ("Date", "4 Nov", "wrong date"), ("Venue", "Hall B", None), ("Purpose", "", None)]
    for i, (lab, val, err) in enumerate(fields):
        fy = y + 0.9 + i * 0.38
        text(s, ix, fy, 0.7, 0.25, lab, t["body"], 9, t["muted"])
        line(s, ix + 0.72, fy + 0.24, ix + iw, fy + 0.24, t["rule"], 0.75)
        if val:
            text(s, ix + 0.78, fy - 0.01, 0.9, 0.25, val, t["semi"], 9.5, t["ink"])
        if err:
            line(s, ix + 0.76, fy + 0.07, ix + 1.22, fy + 0.07, t["bad"], 1.25)
            text(s, ix + 1.3, fy, iw - 1.3, 0.25, err, t["semi"], 9, t["bad"])
    gy = y + 2.5
    text(s, ix, gy, iw, 0.22, "SIGNATURES", t["mono"], 8, t["faint"], tracking=1.0)
    cw_, ch_ = (iw - 0.12) / 2, 0.66
    cells = [("Faculty coord.", "sig"), ("HoD", "away"), ("Dean SA", ""), ("Security", "")]
    for i, (lab, state) in enumerate(cells):
        cx = ix + (i % 2) * (cw_ + 0.12)
        cy = gy + 0.27 + (i // 2) * (ch_ + 0.1)
        rect(s, cx, cy, cw_, ch_, fill="FFFFFF", line=t["rule"], lw=0.75)
        text(s, cx + 0.07, cy + ch_ - 0.24, cw_ - 0.1, 0.22, lab, t["body"], 8.5, t["muted"])
        if state == "sig":
            poly(s, [(cx + 0.12, cy + 0.36), (cx + 0.27, cy + 0.16), (cx + 0.36, cy + 0.36), (cx + 0.5, cy + 0.14),
                     (cx + 0.6, cy + 0.34), (cx + 0.8, cy + 0.22)], t["ink"], 1.25)
        elif state == "away":
            text(s, cx + 0.07, cy + 0.12, cw_ - 0.1, 0.25, "come tomorrow", t["semi"], 8.5, t["bad"])
    st = rect(s, x + w - 1.55, y + 1.97, 1.05, 0.34, fill="FFFFFF", line=t["bad"], lw=1.5)
    st.rotation = -8
    tf = st.text_frame
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "REPRINT"
    r.font.name = t["mono_b"]; r.font.size = Pt(11); r.font.color.rgb = rgb(t["bad"])
    text(s, x, y + h + 0.08, w, 0.25, "The paper form Riya carries", t["body"], 10, t["faint"], align="c")


# ---------------------------------------------------------------- 2. problem
def slide_problem(d):
    t = d.t
    s = d.new_slide(
        "Meet Riya, second-year CSE. She is organising her department's tech fest and needs one permission letter. "
        "Day one: she fills and prints the form, then waits outside the faculty coordinator's cabin. He spots a wrong "
        "date, so she reprints and queues again, and misses a lecture. Day two: the HoD is away, come tomorrow. Day three: "
        "another queue at the Dean Student Affairs office, then the Security stamp. Four signatures, three days, two "
        "lectures missed, and at no point could anyone tell her where the form was. And the worst part: at the end she "
        "holds a piece of paper that anyone with a pen and a photocopier could fake, and nobody outside the college can "
        "prove it is real. Many students chase around fifteen signatures like this every month; the exact count varies "
        "from college to college.")
    header(s, d, "Problem Statement", "Four cabins, three days, and the result is a paper anyone could fake.")
    xs = [1.0, 2.95, 4.9, 6.85, 8.75]
    y = 2.75
    days = [(xs[0] - 0.25, xs[1] + 0.55, "Day 1"), (xs[2] - 0.55, xs[2] + 0.55, "Day 2"), (xs[3] - 0.55, xs[4] + 0.25, "Day 3")]
    for x1, x2, lab in days:
        line(s, x1, 2.25, x2, 2.25, t["rule"], 1.0)
        text(s, x1, 1.95, x2 - x1, 0.28, lab, t["semi"], 12, t["muted"])
    line(s, xs[0], y, xs[-1], y, t["rule"], 1.5)
    names = ["Riya", "Faculty coordinator", "HoD", "Dean Student Affairs", "Security"]
    notes = ["prints the form", "queue; wrong date", "away: come tomorrow", "another queue", "final stamp"]
    for i, (x, n, nt) in enumerate(zip(xs, names, notes)):
        circle(s, x, y, 0.26, fill=t["bg"], line=t["ink"], lw=1.5)
        al, bx = ("l", x - 0.13) if i == 0 else (("r", x - 1.87) if i == 4 else ("c", x - 0.95))
        bw = 2.0 if i in (0, 4) else 1.9
        text(s, bx, y + 0.28, bw, 0.3, n, t["semi"], 13, t["ink"], align=al)
        text(s, bx, y + 0.56, bw, 0.3, nt, t["body"], 11.5, t["bad"] if i in (1, 2, 3) else t["muted"], align=al)
    for cx in [(xs[0] + xs[1]) / 2, (xs[1] + xs[2]) / 2, (xs[2] + xs[3]) / 2, (xs[3] + xs[4]) / 2]:
        circle(s, cx, y, 0.3, fill=t["bg"], line=t["bad"], lw=1.25)
        line(s, cx, y, cx, y - 0.09, t["bad"], 1.25)
        line(s, cx, y, cx + 0.07, y, t["bad"], 1.25)
    poly(s, [(xs[1], y + 0.95), (xs[1], y + 1.22), (xs[0], y + 1.22), (xs[0], y + 0.95)], t["bad"], 1.25, dash=True, arrow=True)
    text(s, xs[0] + 0.15, y + 1.29, 3.6, 0.3, "Reprint, queue again, miss a lecture", t["body"], 11.5, t["bad"])
    # Riya's tally
    ty = 4.55
    line(s, ML, ty - 0.15, 9.05, ty - 0.15, t["rule"], 0.75)
    tally = [("4", "signatures chased"), ("3", "days"), ("2", "lectures missed"), ("0", "ways to prove it")]
    for i, (n, lab) in enumerate(tally):
        x = ML + i * 2.1
        text(s, x, ty, 2.0, 0.35, [[(n, t["head"], 18, t["bad"] if n != "0" else t["ink"]), ("  " + lab, t["body"], 12, t["muted"])]],
             t["body"], 12, t["muted"], anchor="m")
    text(s, ML, ty + 0.75, 8.4, 0.35, [[("Many students chase ", t["body"], 15, t["ink"]), ("~15 signatures a month", t["semi"], 15, t["ink"]),
                                    ("; it varies from college to college.", t["body"], 15, t["ink"])]], t["body"], 15, t["ink"])
    paper_form(s, t, 9.6, 1.95, 2.98, 4.45)
    footer(s, d, 2, TOTAL, "Riya's journey: a typical event-permission chain on our campus. ~15 signatures a month: team estimate that "
                           "varies by college, to be measured in a 50-student survey.")


# ---------------------------------------------------------------- 3. scale
def slide_scale(d):
    t = d.t
    s = d.new_slide(
        "Now multiply Riya by India. AISHE 2023-24 counts 4.5 crore students in higher education; at about fifteen forms "
        "a year each, that is roughly 67 crore paper approvals, our estimate. That is a mountain of paper, and not one "
        "sheet of it can prove itself. AuthBridge found that 1 in 20 education checks in 2025 flagged a problem, mostly "
        "fake certificates. Students queue in class hours, faculty are interrupted, the admin office keeps files that "
        "anyone with access can change, and a remote or differently-abled student must still walk to every cabin. "
        "India already has the digital rails; what is missing is proof: a signature that can defend itself.")
    header(s, d, "Scale of the Problem", "Crores of approvals a year, and not one of them can prove it is genuine.")
    cols = [("4.50", "crore", t["ink"], "students in Indian higher education", "1,289 universities · 48,246 colleges"),
            ("~67", "crore", t["ink"], "paper approvals a year (est.)", "~15 forms per student; ~200 crore sheets"),
            ("1 in 20", "", t["bad"], "education checks flag a problem", "mostly fake certificates (AuthBridge 2025)")]
    cw = CW / 3
    y = 2.2
    for i, (big, unit, col, lab, sub) in enumerate(cols):
        x = ML + i * cw + (0.35 if i else 0)
        if i:
            line(s, ML + i * cw, y + 0.1, ML + i * cw, y + 1.45, t["rule"], 0.75)
        bignum(s, t, x, y, cw - 0.4, big, unit, col, 54)
        text(s, x, y + 0.78, cw - 0.4, 0.3, lab, t["semi"], 15, t["ink"])
        text(s, x, y + 1.08, cw - 0.4, 0.3, sub, t["body"], 12.5, t["muted"])
    # who carries the manual load
    py = 3.95
    label(s, t, ML, py, 8, "Who carries the manual load today")
    parties = [("Students", "Queue in class hours, with no live status"),
               ("Faculty and HoDs", "Interrupted to sign near-identical slips"),
               ("Admin office", "Files anyone with access can quietly change"),
               ("Accessibility", "Remote and differently-abled students must reach every cabin")]
    pw = CW / 4
    line(s, ML, py + 0.38, W - MR, py + 0.38, t["rule"], 0.75)
    for i, (a, b) in enumerate(parties):
        x = ML + i * pw
        text(s, x, py + 0.5, pw - 0.3, 0.3, a, t["semi"], 14, t["ink"])
        text(s, x, py + 0.8, pw - 0.3, 0.55, b, t["body"], 12, t["muted"], spacing=1.1)
    text(s, ML, 5.55, CW, 0.4, [[("Slow is bad. ", t["semi"], 17, t["ink"]),
                                 ("Impossible to verify is worse. A signature should prove itself.", t["semi"], 17, t["accent"])]], t["semi"], 17, t["ink"])
    footer(s, d, 3, TOTAL, "AISHE 2023-24, Ministry of Education (released Jul 2026). AuthBridge Workforce Fraud Files 2025: 5% of education "
                           "checks flagged discrepancies. Est.: 15 forms × 3 sheets per student a year.")


# ---------------------------------------------------------------- 4. solution
def slide_solution(d):
    t = d.t
    s = d.new_slide(
        "Here is the same request on CampusSign. Riya fills the form once. The system sends it to the right roles, "
        "not names. Each approver taps Approve and types a PIN; that tap signs with their own digital key, like a "
        "personal seal nobody else can copy. When the last person signs, the PDF's fingerprint is locked on a "
        "blockchain. From then on, anyone can scan the QR and get the truth in seconds: Verified, Superseded, Revoked "
        "or Tampered. Three days becomes the same day, and the paper never exists.")
    header(s, d, "Proposed Solution", "Submit once. The right people sign. The blockchain remembers forever.")
    steps = [("Request", "Fill the form once"), ("Route", "By role, not by name"),
             ("Sign", "PIN + your own digital key"), ("Seal", "Locked on blockchain"),
             ("Verify", "Anyone scans the QR")]
    y = 2.55
    x0, x1 = ML + 0.2, W - MR - 0.2
    step = (x1 - x0) / 4
    line(s, x0, y, x1, y, t["rule"], 1.5)
    for i, (a, b) in enumerate(steps):
        cx = x0 + i * step
        if i < 4:
            circle(s, cx, y, 0.26, fill=t["bg"], line=t["accent"], lw=1.5)
        else:
            seal(s, cx, y, 0.34, t, ok=True)
        al = "l" if i == 0 else ("r" if i == 4 else "c")
        bx = cx - 0.13 if i == 0 else (cx - 2.37 if i == 4 else cx - 1.25)
        text(s, bx, y + 0.4, 2.5, 0.35, a, t["head"], H2, t["ok"] if i == 4 else t["ink"], align=al)
        text(s, bx, y + 0.78, 2.5, 0.3, b, t["body"], 13, t["muted"], align=al)
    # forms covered
    fy = 4.05
    label(s, t, ML, fy, 3, "Works for")
    text(s, ML, fy + 0.28, CW, 0.35,
         "Event permission   ·   On-duty   ·   Bonafide   ·   No-dues   ·   Any PDF to sign   ·   Custom request",
         t["body"], 15, t["ink"])
    # time bars
    by = 5.05
    line(s, ML, by - 0.15, W - MR, by - 0.15, t["rule"], 0.75)
    label(s, t, ML, by, 4, "Time to a signed approval")
    rows = [("Paper today", 8.0, t["rule"], "2 to 4 days", t["muted"]),
            ("CampusSign", 0.55, t["ok"], "same day (target)", t["ok"])]
    for j, (lab, bw, col, val, vcol) in enumerate(rows):
        ry = by + 0.42 + j * 0.55
        text(s, ML, ry - 0.02, 2.4, 0.3, lab, t["semi"] if j else t["body"], 14, t["ink"])
        rect(s, ML + 2.5, ry, bw, 0.24, fill=col)
        text(s, ML + 2.5 + bw + 0.18, ry - 0.02, 2.6, 0.3, val, t["semi"], 14, vcol)
    footer(s, d, 4, TOTAL, "Paper turnaround is a typical range on our campus, to be measured in the pilot; same day is the pilot target.")


# ---------------------------------------------------------------- 5. architecture
def slide_arch(d):
    t = d.t
    s = d.new_slide(
        "This is the whole system on one page. Students, approvers, the admin office and verifiers all use one web app "
        "that installs on a phone like a normal app. Behind it, our server finds the right person for each role, runs "
        "the deadlines, escalates and hands work to a delegate. The database keeps the forms, the PDFs and an audit log "
        "where every line is chained to the one before, so a quiet edit is caught. When the last approver signs, we "
        "build the PDF, take its fingerprint and send only that fingerprint, with a proof of the signers, to our smart "
        "contract on the blockchain. Think of the contract as a notary that never sleeps, never forgets and cannot be "
        "bribed. The security guard's phone can even check a pass with no internet at all.")
    header(s, d, "System Architecture", "One app does the paperwork; the blockchain is the judge nobody can bribe.")
    # people
    people = [("Students", "fill, submit, track"), ("Approvers", "faculty, HoD, Dean"),
              ("Admin office", "forms, roles, reports"), ("Verifiers", "scan the code on a PDF")]
    py0 = 2.3
    for i, (a, b) in enumerate(people):
        y = py0 + i * 0.85
        rect(s, ML, y, 1.85, 0.7, fill=t["panel"])
        text(s, ML + 0.15, y + 0.1, 1.7, 0.28, a, t["semi"], 13, t["ink"])
        text(s, ML + 0.15, y + 0.37, 1.7, 0.28, b, t["body"], 10.5, t["muted"])
        line(s, ML + 1.85, y + 0.35, 2.85, y + 0.35, t["faint"], 1.0)
    line(s, 2.85, py0 + 0.35, 2.85, py0 + 3 * 0.85 + 0.35, t["faint"], 1.0)
    # platform boundary
    bx0, by0, bx1, by1 = 3.15, 2.05, 9.95, 5.95
    rect(s, bx0, by0, bx1 - bx0, by1 - by0, fill=None, line=t["rule"], lw=1.25)
    text(s, bx0 + 0.2, by0 + 0.08, 6, 0.25, "CampusSign  ·  one open-source TypeScript app", t["semi"], 11, t["muted"])

    def box(x, y, w, h, title, detail, dashed=False, fill=None):
        sh = rect(s, x, y, w, h, fill=fill or t["bg"], line=t["accent"] if not dashed else t["faint"], lw=1.25)
        if dashed:
            etree.SubElement(sh.line._get_or_add_ln(), qn("a:prstDash")).set("val", "dash")
        text(s, x + 0.18, y + 0.12, w - 0.3, 0.28, title, t["semi"], 13, t["ink"])
        text(s, x + 0.18, y + 0.42, w - 0.3, h - 0.45, detail, t["body"], 10.5, t["muted"], spacing=1.1)

    ax = 3.4
    box(ax, 2.42, 6.3, 0.72, "Web app  ·  React, installs on a phone",
        "Forms  ·  approver inbox  ·  live tracking  ·  sign in place on any PDF  ·  verify page")
    line(s, 2.85, 2.78, ax, 2.78, t["faint"], 1.0, arrow=True)
    box(ax, 3.55, 3.05, 1.1, "Workflow  ·  Node.js server",
        "Finds who signs, deadlines, escalation, delegation, email")
    box(6.65, 3.55, 3.05, 1.1, "Sign and seal",
        "PIN + approver's own key, PDF with QR, SHA-256 fingerprint")
    box(ax, 4.95, 2.65, 0.8, "Data  ·  SQLite", "Forms, PDFs, chained audit log")
    box(6.65, 4.95, 3.05, 0.8, "Gate phone  ·  offline", "Checks the QR with no internet", dashed=True)
    # flows inside the platform
    line(s, 4.6, 3.14, 4.6, 3.55, t["accent"], 1.25, arrow=True)
    text(s, 4.72, 3.22, 1.6, 0.25, "submit, approve", t["body"], 9.5, t["faint"])
    line(s, 6.45, 4.1, 6.65, 4.1, t["accent"], 1.25, arrow=True)
    line(s, 4.6, 4.65, 4.6, 4.95, t["accent"], 1.25, arrow=True)
    text(s, 4.72, 4.69, 1.6, 0.25, "store, audit", t["body"], 9.5, t["faint"])
    poly(s, [(6.2, 4.65), (6.2, 5.35), (6.65, 5.35)], t["faint"], 1.0, dash=True, arrow=True)
    # trust layer
    cx0 = 10.45
    line(s, 9.7, 4.1, cx0, 4.1, t["accent"], 1.5, arrow=True)
    text(s, 9.73, 3.82, 0.75, 0.25, "hash", t["mono"], 9.5, t["accent"], align="c")
    rect(s, cx0, 3.55, W - MR - cx0, 1.1, fill=t["accent"])
    text(s, cx0 + 0.18, 3.67, 1.9, 0.28, "Blockchain", t["semi"], 13, "FFFFFF")
    text(s, cx0 + 0.18, 3.97, 1.9, 0.6, "Smart contract on Polygon Amoy or a college chain", t["body"], 10.5, "DCE6F2", spacing=1.1)
    text(s, cx0, 4.8, W - MR - cx0, 0.8, "Holds fingerprints, a proof of signers and status. No personal data.",
         t["semi"], 11, t["accent"], spacing=1.1)
    # external rails
    line(s, 6.55, by1, 6.55, 6.2, t["faint"], 1.0)
    rect(s, bx0, 6.2, W - MR - bx0, 0.42, fill=None, line=t["rule"], lw=1.0)
    text(s, bx0 + 0.2, 6.2, W - MR - bx0 - 0.3, 0.42,
         [[("Connects to     ", t["semi"], 11.5, t["muted"]),
           ("Public block explorer  ·  Email (AWS SES)  ·  Next: Aadhaar eSign, DigiLocker, college ERP", t["body"], 12, t["ink"])]],
         t["body"], 12, t["ink"], anchor="m")
    footer(s, d, 5, TOTAL)


# ---------------------------------------------------------------- 6. tech stack
def slide_tech(d):
    t = d.t
    s = d.new_slide(
        "This is what CampusSign is actually built with, and every piece is open source. The app is React, so it "
        "installs on a phone and even works offline at the gate. The server is Node.js, the database is SQLite, which "
        "can grow into Postgres. The shaded rows are the blockchain layer, the heart of the product: a Solidity smart "
        "contract we wrote ourselves, ethers.js to talk to it, and a chain to run it on, a private college chain or "
        "Polygon's public test network. Every approver gets their own digital key, and the college has a key that signs "
        "the QR so a guard can check it offline. PDFs are built with pdf-lib and emails go out through AWS. Nothing "
        "here locks a college in.")
    header(s, d, "Tech Stack", "Open-source from top to bottom; the blockchain layer is the heart of it.")
    rows = [("Web app", "React + Vite", "Any browser", "Student, approver, admin, verify and gate screens", "APP"),
            ("Server and workflow", "Node.js + Express", "", "Role routing, deadlines, escalation, delegation", "APP"),
            ("Data and files", "SQLite", "Postgres", "Forms, PDFs, hash-chained audit log", "DATA"),
            ("Smart contract", "Solidity", "", "Seals, versions, revocations, signer check", "CHAIN"),
            ("Chain connection", "ethers.js", "", "Sends seals, reads proofs, waits for blocks", "CHAIN"),
            ("Blockchain network", "Polygon Amoy", "College chain", "Public test network, or a private one per college", "CHAIN"),
            ("Digital signatures", "Ed25519 + wallets", "Aadhaar eSign (next)", "College key for the QR; one key per approver", "CRYPTO"),
            ("PDF and email", "pdf-lib + QR", "AWS SES", "Sealed PDF with QR code; email alerts", "APP")]
    cols = [(ML, 2.35, "Layer"), (ML + 2.45, 2.55, "Built with"), (ML + 5.1, 1.75, "Also works with"), (ML + 6.95, 3.85, "What it does")]
    y0 = 1.95
    for x, w, h in cols:
        text(s, x, y0, w, 0.28, h, t["semi"], 11.5, t["muted"])
    text(s, W - MR - 0.95, y0, 0.95, 0.28, "Type", t["semi"], 11.5, t["muted"], align="r")
    line(s, ML, y0 + 0.33, W - MR, y0 + 0.33, t["ink"], 1.0)
    rh = 0.48
    tag_col = {"APP": t["accent"], "DATA": t["accent"], "CHAIN": t["ok"], "CRYPTO": t["ok"]}
    shaded = ("CHAIN", "CRYPTO")
    for i, (layer, tool, backup, role, tag) in enumerate(rows):
        y = y0 + 0.42 + i * rh
        if tag in shaded:
            rect(s, ML, y - 0.04, CW, rh, fill=t["ok_bg"])
        text(s, ML + 0.1, y, 2.3, rh - 0.08, layer, t["semi"], 13, t["ink"], anchor="m")
        text(s, cols[1][0], y, cols[1][1], rh - 0.08, tool, t["semi"], 13, t["accent"], anchor="m")
        text(s, cols[2][0], y, cols[2][1], rh - 0.08, backup, t["body"], 12, t["muted"], anchor="m")
        text(s, cols[3][0], y, cols[3][1], rh - 0.08, role, t["body"], 12, t["muted"], anchor="m")
        text(s, W - MR - 1.0, y, 0.92, rh - 0.08, {"APP": "App", "DATA": "Data", "CHAIN": "Chain", "CRYPTO": "Crypto"}[tag],
             t["semi"], 11, tag_col[tag], align="r", anchor="m")
        if tag not in shaded:
            line(s, ML, y + rh - 0.04, W - MR, y + rh - 0.04, t["rule"], 0.75)
    fy = y0 + 0.42 + len(rows) * rh + 0.2
    text(s, ML, fy, CW, 0.35, [[("Shaded rows are the blockchain layer.  ", t["semi"], 14, t["ink"]),
                                ("Every tool is open source and free, so a college is never locked in.",
                                 t["body"], 13, t["muted"])]], t["body"], 13, t["muted"])
    footer(s, d, 6, TOTAL)


# ---------------------------------------------------------------- 7. routing + AI
def slide_routing(d):
    t = d.t
    s = d.new_slide(
        "Routing works on roles, not names, so when a HoD changes nothing breaks. An event permission goes faculty "
        "coordinator, HoD, Dean Student Affairs, with Security in parallel. Every step has a 48-hour deadline: a "
        "reminder, then escalation, and a delegate when someone is on leave. Now the blockchain part, in plain words. "
        "Every approver has their own digital key, like a personal seal only they can press. All the seals on a "
        "document are squeezed into one tiny stamp, a Merkle root, and that stamp goes on the chain. The smart contract "
        "can then check any single signer by itself. And our audit log is chained line to line, with its latest line "
        "copied to the blockchain, so if anyone edits history, the alarm goes off.")
    header(s, d, "Workflow and Blockchain Proof", "The system knows who must sign; the blockchain remembers that they did.")
    top = 2.15
    # left: role chain
    label(s, t, ML, top, 5, "Event permission, routed by role")
    nodes = [("Student submits", "Fills the form, adds files", t["muted"]), ("Faculty coordinator", "48 h deadline, then a reminder", t["muted"]),
             ("HoD", "On leave? Goes to the delegate", t["muted"]), ("Dean Student Affairs", "Too slow? Auto-escalates", t["muted"]),
             ("Sealed on the blockchain", None, t["ok"])]
    nx = ML + 0.15
    ys = [top + 0.55 + i * 0.82 for i in range(5)]
    line(s, nx, ys[0], nx, ys[-1], t["rule"], 1.5)
    for i, (n, sub, col) in enumerate(nodes):
        if i == 4:
            seal(s, nx, ys[i], 0.34, t, ok=True)
        else:
            circle(s, nx, ys[i], 0.26, fill=t["bg"], line=t["accent"], lw=1.5)
        text(s, nx + 0.35, ys[i] - 0.17, 3.0, 0.3, n, t["semi"], 14, t["ok"] if i == 4 else t["ink"])
        if sub:
            text(s, nx + 0.35, ys[i] + 0.1, 3.0, 0.3, sub, t["body"], 11.5, t["muted"])
    # parallel branch
    bx = ML + 3.55
    poly(s, [(nx + 2.35, ys[1] - 0.02), (bx - 0.4, ys[1] - 0.02), (bx - 0.4, ys[2] - 0.1)], t["faint"], 1.0, dash=True)
    circle(s, bx - 0.4, ys[2], 0.26, fill=t["bg"], line=t["accent"], lw=1.5)
    text(s, bx - 0.15, ys[2] - 0.17, 1.6, 0.3, "Security", t["semi"], 14, t["ink"])
    text(s, bx - 0.15, ys[2] + 0.1, 1.6, 0.3, "in parallel", t["body"], 11.5, t["muted"])
    # middle: what AI does
    mx = 5.85
    line(s, mx - 0.3, top, mx - 0.3, 6.45, t["rule"], 0.75)
    label(s, t, mx, top, 3.3, "Four locks on every approval")
    ai = [("Your own digital key", "Only you can unlock your key"),
          ("One stamp for all", "All signatures in one Merkle root"),
          ("The chain checks it", "The contract confirms each signer"),
          ("Tamper alarm", "Edit a record, the hash chain breaks")]
    for i, (a, b) in enumerate(ai):
        y = top + 0.45 + i * 0.82
        text(s, mx, y, 3.25, 0.3, a, t["semi"], 14, t["ink"])
        text(s, mx, y + 0.3, 3.25, 0.5, b, t["body"], 11.5, t["muted"], spacing=1.1)
    text(s, mx, top + 3.8, 3.6, 0.35, "People sign. The chain remembers.", t["semi"], 14, t["accent"])
    # right: concept phone, HoD inbox
    px, py, pw, ph = 9.75, 2.0, 2.83, 4.35
    rect(s, px, py, pw, ph, fill=t["bg"], line=t["ink"], lw=1.5, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.07)
    ix = px + 0.2
    text(s, ix, py + 0.25, 2.0, 0.3, "Approvals", t["semi"], 13, t["ink"])
    text(s, ix + 1.4, py + 0.27, 1.05, 0.3, "12 pending", t["body"], 10, t["muted"], align="r")
    cyy = py + 0.7
    rect(s, ix, cyy, pw - 0.4, 2.65, fill=t["panel"])
    text(s, ix + 0.15, cyy + 0.15, 2.2, 0.25, "EVENT PERMISSION", t["mono"], 8.5, t["faint"], tracking=0.8)
    text(s, ix + 0.15, cyy + 0.38, 2.2, 0.3, "Robotics fest, 5 Nov", t["semi"], 12, t["ink"])
    text(s, ix + 0.15, cyy + 0.65, 2.2, 0.25, "Riya · CSE, 2nd year", t["body"], 9.5, t["muted"])
    text(s, ix + 0.15, cyy + 0.98, 2.2, 0.25, "YOUR SIGNING KEY", t["mono"], 8.5, t["accent"], tracking=0.8)
    text(s, ix + 0.15, cyy + 1.2, 2.15, 0.7, "0x7a3f…c91e. Approve with your PIN; sealed on chain.", t["body"], 10, t["ink"], spacing=1.1)
    tick(s, ix + 0.23, cyy + 1.85, 0.16, t["ok"], 1.5)
    text(s, ix + 0.38, cyy + 1.74, 2.0, 0.25, "Hall B · 120 students", t["body"], 10, t["ok"])
    rect(s, ix, py + 3.5, (pw - 0.5) / 2, 0.42, fill=t["ok"])
    text(s, ix, py + 3.5, (pw - 0.5) / 2, 0.42, "Approve", t["semi"], 11, "FFFFFF", align="c", anchor="m")
    rect(s, ix + (pw - 0.5) / 2 + 0.1, py + 3.5, (pw - 0.5) / 2, 0.42, fill=t["bg"], line=t["faint"], lw=1.0)
    text(s, ix + (pw - 0.5) / 2 + 0.1, py + 3.5, (pw - 0.5) / 2, 0.42, "Return", t["semi"], 11, t["ink"], align="c", anchor="m")
    text(s, px, py + ph + 0.08, pw, 0.25, "HoD inbox", t["body"], 10, t["faint"], align="c")
    footer(s, d, 7, TOTAL)


# ---------------------------------------------------------------- 8. why we win
def slide_compare(d):
    t = d.t
    s = d.new_slide(
        "Every alternative solves one slice. Paper is familiar but slow and forgeable. Google Forms is quick but has no "
        "real signature or audit trail. ERPs like Samarth run admissions and fees, not everyday ad-hoc approvals. E-sign "
        "tools sign legally but know nothing about campus roles. We are the everyday approvals layer that plugs into what "
        "colleges already run, and pushes final documents to DigiLocker.")
    headline(s, d, "Others solve one slice; we combine all five.")
    cols = ["Role routing", "AI assist", "Legal e-sign", "Public verification", "No-code to maintain"]
    rows = [("Paper and wet ink", "nnnnn"), ("Google Forms + email", "nnnny"), ("College ERP / Samarth", "pnpnn"),
            ("Generic e-sign tools", "nnypp"), ("CampusSign", "yyyyy")]
    lw_ = 3.4
    cw = (CW - lw_) / 5
    y0 = 1.7
    for j, c in enumerate(cols):
        text(s, ML + lw_ + j * cw, y0, cw, 0.5, c, t["semi"], 13, t["ink"], align="c", anchor="b")
    line(s, ML, y0 + 0.62, W - MR, y0 + 0.62, t["ink"], 1.0)
    rh = 0.6
    for i, (name, marks) in enumerate(rows):
        y = y0 + 0.72 + i * rh
        ours = i == 4
        if ours:
            rect(s, ML, y + 0.06, CW, rh - 0.04, fill=t["ok_bg"])
        else:
            line(s, ML, y + rh + 0.02, W - MR, y + rh + 0.02, t["rule"], 0.75)
        text(s, ML + 0.2, y + 0.06, lw_ - 0.2, rh - 0.04, name, t["head"] if ours else t["body"], 15, t["ink"], anchor="m")
        for j, m in enumerate(marks):
            cx, cy = ML + lw_ + j * cw + cw / 2, y + 0.04 + rh / 2
            if m == "y":
                seal(s, cx, cy, 0.3, t, ok=True) if ours else tick(s, cx, cy, 0.24, t["ink"], 1.75)
            elif m == "p":
                circle(s, cx, cy, 0.2, fill=None, line=t["muted"], lw=1.5)
            else:
                line(s, cx - 0.09, cy, cx + 0.09, cy, t["faint"], 1.5)
    ly = y0 + 0.72 + 5 * rh + 0.15
    # legend
    lx = ML + lw_
    tick(s, lx + 0.1, ly + 0.14, 0.18, t["ink"], 1.5)
    text(s, lx + 0.3, ly, 1.0, 0.3, "built in", t["body"], 11, t["muted"])
    circle(s, lx + 1.45, ly + 0.14, 0.16, fill=None, line=t["muted"], lw=1.0)
    text(s, lx + 1.65, ly, 2.4, 0.3, "partial, needs custom setup", t["body"], 11, t["muted"])
    line(s, lx + 4.1, ly + 0.14, lx + 4.26, ly + 0.14, t["faint"], 1.5)
    text(s, lx + 4.4, ly, 1.2, 0.3, "not offered", t["body"], 11, t["muted"])
    text(s, ML, 6.05, CW, 0.35, "Complements DigiLocker and ERPs; does not replace them.", t["semi"], BODY + 2, t["ink"])
    text(s, ML, 6.42, CW, 0.3, "Final documents can still go to DigiLocker; records sync with Samarth or any ERP.", t["body"], 13, t["muted"])
    footer(s, d, 8, TOTAL, "Typical out-of-the-box use for everyday campus approvals, from our review of each category.")


# ---------------------------------------------------------------- 9. impact + SDGs
def slide_impact(d):
    t = d.t
    s = d.new_slide(
        "Every tap is a sheet not printed, and every approval is a record that can never be quietly changed. "
        "For one university of ten thousand students we estimate one and a half lakh approvals a year moved off paper, "
        "about four and a half lakh sheets, over a lakh student-hours and eight thousand faculty-hours returned. That is "
        "at least 5.7 tonnes of CO2e and about 54 trees. Across Indian higher education: at least 25,400 tonnes and "
        "2.4 lakh trees every year. Every multiplier is an assumption the pilot will measure.")
    header(s, d, "Impact and Benefits", "One campus saves lakhs of sheets; India saves tens of thousands of tonnes of CO2e.")
    top = 2.0
    tx, cw1, cw2, cw3 = ML, 3.0, 2.2, 2.2
    x2, x3 = tx + cw1, tx + cw1 + cw2
    tw = cw1 + cw2 + cw3
    rows = [("Approvals moved off paper", "1.5 lakh", "~67 crore", t["ink"]),
            ("Sheets of paper not printed", "~4.5 lakh", "~200 crore", t["ok"]),
            ("CO2e avoided", "≥5.7 t", "≥25,400 t", t["ok"]),
            ("Trees not cut", "~54", "~2.4 lakh", t["ok"]),
            ("Student-hours returned", "~1.1 lakh", "", t["ink"]),
            ("Faculty-hours returned", "~8,000", "", t["ink"])]
    rh = 0.56
    rect(s, x3, top, cw3, 0.62 + len(rows) * rh, fill=t["ok_bg"])
    text(s, tx, top + 0.1, cw1, 0.45, "Per year, estimated (one university = 10,000 students)", t["semi"], 12, t["muted"], anchor="b")
    text(s, x2, top + 0.1, cw2 - 0.2, 0.45, "One university", t["semi"], 12, t["muted"], align="r", anchor="b")
    text(s, x3, top + 0.1, cw3 - 0.2, 0.45, "All of India", t["semi"], 12, t["muted"], align="r", anchor="b")
    line(s, tx, top + 0.62, tx + tw, top + 0.62, t["ink"], 1.0)
    for i, (lab, a, b, col) in enumerate(rows):
        ry = top + 0.62 + i * rh
        text(s, tx, ry, cw1, rh, lab, t["body"], 14, t["ink"], anchor="m")
        text(s, x2, ry, cw2 - 0.2, rh, a, t["head"], 18, col, align="r", anchor="m")
        text(s, x3, ry, cw3 - 0.2, rh, b or "not estimated", t["head"] if b else t["body"], 18 if b else 11,
             col if b else t["faint"], align="r", anchor="m")
        line(s, tx, ry + rh, tx + tw, ry + rh, t["rule"], 0.75)
    # SDGs as a plain list
    sx = tx + tw + 0.55
    line(s, sx - 0.3, top, sx - 0.3, top + 0.62 + len(rows) * rh, t["rule"], 0.75)
    label(s, t, sx, top + 0.27, W - MR - sx, "UN Sustainable Development Goals")
    sdgs = [("4", "Quality Education", "class time, not queue time"), ("9", "Industry and Infrastructure", "shared digital rails"),
            ("12", "Responsible Consumption", "single-use paper removed"), ("13", "Climate Action", "live CO2-saved counter"),
            ("15", "Life on Land", "trees not cut"), ("16", "Strong Institutions", "every decision locked on chain")]
    for i, (n, nm, why) in enumerate(sdgs):
        y = top + 0.72 + i * rh
        text(s, sx, y, W - MR - sx, 0.28, [[("SDG " + n + "  ", t["semi"], 14, t["accent"]), (nm, t["semi"], 14, t["ink"])]],
             t["semi"], 14, t["ink"])
        text(s, sx, y + 0.25, W - MR - sx, 0.25, why, t["body"], 11, t["muted"])
    footer(s, d, 9, TOTAL, "Assumptions: 15 forms × 3 sheets per student; 45 min chasing per form; 2 signers, 2 min paper vs 20 s digital. "
                           "Per sheet: 12.7 g CO2e, 1/8,333 tree (Environmental Paper Network calculator v3.2, via PaperCut).")


# ---------------------------------------------------------------- 10. roadmap
def slide_roadmap(d):
    t = d.t
    s = d.new_slide(
        "The MVP is built: submit, route, sign, seal on chain, amend, revoke and verify all work today. Next, one "
        "department for a semester with a paper fallback, then university-wide once turnaround is halved, then a "
        "network of colleges on one shared chain, each writing its own records and checking everyone else's. Picture "
        "a single trust network where a degree, a NOC or an internship letter from any college can be checked in two "
        "seconds. The same engine works anywhere a request climbs a ladder of signatures, from government offices to "
        "hospitals. At fifty rupees per student a year, it costs about what a campus already spends printing these "
        "forms. CampusSign: campus approvals, locked on a blockchain, and anyone can check them.")
    header(s, d, "Roadmap and Future Scope", "From one campus chain to a nationwide network of trust.")
    # roadmap band
    y = 2.7
    phases = [("MVP built", "Sign, seal, amend, revoke, verify"), ("Department pilot", "One department, one semester"),
              ("University rollout", "Aadhaar eSign and DigiLocker"), ("College network", "Each college a chain node")]
    gates = ["Admin approves", "Turnaround halved", "3 partner colleges"]
    x0, x1 = ML + 0.15, W - MR - 2.6
    st = (x1 - x0) / 3
    line(s, x0, y, x1, y, t["rule"], 1.5)
    for i, (a, b) in enumerate(phases):
        cx = x0 + i * st
        circle(s, cx, y, 0.26, fill=t["accent"] if i == 0 else t["bg"], line=t["accent"], lw=1.5)
        text(s, cx - 0.13, y + 0.25, 2.4, 0.3, a, t["semi"], 14, t["ink"])
        text(s, cx - 0.13, y + 0.53, 2.4, 0.3, b, t["body"], 11.5, t["muted"])
        if i < 3:
            gx = cx + st / 2
            line(s, gx, y - 0.12, gx, y + 0.12, t["ink"], 1.5)
            text(s, gx - 1.0, y - 0.45, 2.0, 0.25, "Gate: " + gates[i], t["body"], 10.5, t["ink"], align="c")
    # beyond education
    line(s, ML, 3.9, W - MR, 3.9, t["rule"], 0.75)
    label(s, t, ML, 4.05, 6.5, "Same engine beyond education: roles, a sign-off chain and proof")
    sectors = ["Government offices", "Hospitals", "Banks and NBFCs", "Corporates", "Municipal and land", "Schools and boards"]
    for i, nm in enumerate(sectors):
        sx_, sy_ = ML + (i % 2) * 3.3, 4.5 + (i // 2) * 0.5
        text(s, sx_, sy_, 3.1, 0.4, nm, t["semi"], 14, t["ink"], anchor="m")
        line(s, sx_, sy_ + 0.45, sx_ + 3.0, sy_ + 0.45, t["rule"], 0.75)
    # three facts
    fx = 8.0
    line(s, fx - 0.3, 4.1, fx - 0.3, 6.6, t["rule"], 0.75)
    facts = [("₹50", "per student a year: about what a campus spends printing these forms (est.)"),
             ("NAAC 6.2.3", "accreditation already counts e-governance in administration"),
             ("19.21 lakh", "government files weeded out in one month (Special Campaign 5.0)")]
    for i, (a, b) in enumerate(facts):
        fy = 4.05 + i * 0.95
        text(s, fx, fy, 4.6, 0.4, a, t["head"], 20, t["accent"])
        text(s, fx, fy + 0.38, 4.6, 0.4, b, t["body"], 12, t["muted"], spacing=1.05)
    footer(s, d, 10, TOTAL, "Est.: 4.5 lakh sheets at ₹1-2 a page = ₹4.5-9 lakh vs ₹5 lakh at ₹50 × 10,000 students. "
                            "NAAC metric 6.2.3. Special Campaign 5.0: PIB, Oct 2025.")


def build(theme, out):
    d = Deck(theme)
    _BG["bg"] = d.t["bg"]
    title_A(d, TOTAL)
    slide_problem(d)
    slide_scale(d)
    slide_solution(d)
    slide_arch(d)
    slide_tech(d)
    slide_routing(d)
    slide_trust(d, 8, TOTAL)
    slide_impact(d)
    slide_roadmap(d)
    d.save(out)
    print("saved", out, d.count, "slides")


if __name__ == "__main__":
    build("A", sys.argv[1])
