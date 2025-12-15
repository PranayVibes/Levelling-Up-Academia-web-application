import streamlit as st
import requests
import time
from datetime import datetime
from collections import defaultdict
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm

#  CONFIG & CSS 
st.set_page_config(page_title="Levelling Up Academia", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap');
    html, body, .main {background: linear-gradient(135deg, #fdf2fb, #f8f0ff); font-family: 'Poppins', sans-serif;}
    
    .big-title {
        font-size: 68px !important; font-weight: 900 !important; text-align: center; margin: 40px 0 10px 0;
        background: linear-gradient(90deg, #d946ef, #a855f7, #7c3aed);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        letter-spacing: -2px;
    }
    .subtitle {text-align: center; color: #6b7280; font-size: 26px; font-weight: 500; margin-bottom: 60px;}

    .content-box {
        background: white; padding: 50px; border-radius: 28px; margin: 30px auto; max-width: 950px;
        box-shadow: 0 15px 45px rgba(168,85,247,0.18); line-height: 1.9; font-size: 18px;
    }
    .content-box h2 {color: #7c3aed; font-size: 36px; font-weight: 800; text-align: center; margin-bottom: 35px;}
    .content-box strong {color: #a855f7;}

    .input-label {
        font-size: 34px !important; font-weight: 800 !important; color: #7c3aed !important;
        text-align: center; margin: 40px 0 20px 0;
    }
    .stTextInput > div > div > input {
        border: 3px solid #7c3aed !important; border-radius: 16px !important;
        padding: 16px 20px !important; text-align: center; font-size: 18px;
    }
    .stButton>button, .stDownloadButton>button {
        background: linear-gradient(90deg, #de6ddf, #a855f7) !important; color: white !important;
        border: none !important; border-radius: 60px !important; padding: 18px 90px !important;
        font-size: 21px !important; font-weight: 800 !important; margin: 40px auto !important;
        display: block !important; box-shadow: 0 10px 30px rgba(168,85,247,0.35);
    }
    .metric-card {
        background: white; padding: 32px; border-radius: 24px; text-align: center; margin-bottom: 18px;
        box-shadow: 0 12px 35px rgba(167,139,250,0.1); border: 1px solid #f0e5ff; min-height: 170px;
    }
    .metric-label {color: #8b5cf6; font-size: 19px; font-weight: 700; margin-bottom: 8px;}
    .metric-value {font-size: 46px; font-weight: 900; color: #7c3aed;}
    .researcher-name {
        font-size: 48px; font-weight: 900; color: #a855f7; text-align: center; margin: 60px 0 40px;
    }
</style>
""", unsafe_allow_html=True)

#  HELPER FUNCTIONS 
def safe_get_json(r):
    try: return r.json()
    except: return {}

def h_index(cits):
    c = sorted([x for x in cits if x > 0], reverse=True)
    for i in range(1, len(c) + 1):
        if i > c[i-1]:
            return i - 1
    return len(c)

def freshness_h(papers_list):
    current = datetime.now().year
    weighted = []
    for p in papers_list:
        y = p.get("year")
        c = p.get("citationCount", 0) or 0
        if y and isinstance(y, int) and y >= 1950:
            age = current - y
            weighted.append(c / (1 + 0.15 * age))
    return h_index(weighted)

def cri(papers_list):
    adjusted = []
    for p in papers_list:
        c = p.get("citationCount", 0) or 0
        n_authors = len(p.get("authors", []) or [])
        n = max(n_authors, 1)
        adjusted.append(c * (1 / (1 + 0.05 * (n - 1))))
    return h_index(adjusted)

def cls(papers_list):
    yearly = defaultdict(int)
    for p in papers_list:
        y = p.get("year")
        if y and 1950 <= y <= datetime.now().year:
            yearly[y] += p.get("citationCount", 0) or 0
    years = sorted(yearly.keys())
    if len(years) < 5: return 0
    cites_per_year = [yearly[y] for y in years]
    avg = sum(cites_per_year) / len(cites_per_year)
    if avg == 0: return 0
    cv = (sum((x - avg)**2 for x in cites_per_year) / len(cites_per_year))**0.5 / avg
    base = avg / (1 + cv)
    longevity_bonus = max(0, (len(years) - 5) * 2)
    return round(base + longevity_bonus, 1)

#  HEADER 
st.markdown('<h1 class="big-title">Levelling Up Academia</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">A fairer, smarter way to measure research impact</p>', unsafe_allow_html=True)

#  NAVIGATION 
tabs = ["Home", "About", "How It Works", "Values", "Developer"]
if "page" not in st.session_state:
    st.session_state.page = "Home"

cols = st.columns(len(tabs))
for i, tab in enumerate(tabs):
    if cols[i].button(tab, use_container_width=True, key=f"nav_{tab}"):
        st.session_state.page = tab
        st.rerun()

#  PAGES 
if st.session_state.page == "About":
    st.markdown("""
    <div class="content-box">
        <h2>About This Project</h2>
        <p><strong>Levelling Up Academia</strong> fixes the biggest flaws in traditional metrics like h-index and total citations.</p>
        <p>Classic systems suffer from:</p>
        <ul style="max-width: 750px; margin: 30px auto; font-size: 19px; line-height: 2;">
            <li><strong>Recency bias</strong> — old groundbreaking work is forgotten</li>
            <li><strong>Collaboration inflation</strong> — mega-author papers inflate scores</li>
            <li><strong>Lack of consistency</strong> — one viral paper can beat decades of excellence</li>
        </ul>
        <p>We created three brand-new metrics:</p>
        <ol style="max-width: 800px; margin: 35px auto; font-size: 19px; line-height: 2.2;">
            <li><strong>Freshness-Weighted h-index</strong> → rewards recent impact fairly</li>
            <li><strong>Collaboration-Resilient Index (CRI)</strong> → removes mega-collaboration boost</li>
            <li><strong>Consistency & Longevity Score (CLS)</strong> → celebrates sustained excellence</li>
        </ol>
        <p style="text-align:center; font-size:22px; font-weight:700; margin-top:40px;">
            Fairer • Transparent • Future-ready
        </p>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "How It Works":
    st.markdown("""
    <div class="content-box">
        <h2>How It Works</h2>
        <p>
            <strong>1. Enter a name or Semantic Scholar ID</strong><br>
            Type any researcher’s name (e.g., “Yoshua Bengio”, “Terence Tao”) or paste their ID.<br>
                <b>Semantic scholar :</b><a href=" https://www.semanticscholar.org/"> https://www.semanticscholar.org/</a> <br><br>
            <strong>2. Real-time search on Semantic Scholar</strong><br>
            We find the exact profile — you choose if there are multiple matches.<br><br>
            <strong>3. All papers fetched instantly</strong><br>
            Title, year, citations, full author list — everything.<br><br>
            <strong>4. Four advanced metrics computed live</strong><br>
            • Classic h-index<br>
            • Freshness-Weighted h-index<br>
            • Collaboration-Resilient Index (CRI)<br>
            • Consistency & Longevity Score (CLS)<br><br>
            <strong>5. Beautiful results + one-click PDF</strong><br>
            Clean cards + downloadable report with top 10 papers.
        </p>
        <p style="text-align:center; font-size:24px; font-weight:700; color:#a855f7; margin-top:40px;">
            Fast • Accurate • Research-Ready
        </p>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "Values":
    st.markdown("""
    <div class="content-box">
        <h2>Our Values</h2>
        <p style="font-size:28px; text-align:center;">
            <strong>Fairness</strong> • <strong>Transparency</strong> • <strong>Merit</strong> • <strong>Accessibility</strong> • <strong>Future</strong>
        </p>
        <p style="text-align:center; font-style:italic; margin-top:20px;">Simple. Honest. Impact-first.</p>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "Developer":
    st.markdown("""
    <div class="content-box">
        <h2>Meet The Developer</h2>
        <p>A developer passionate about building clean, impactful tools that make research more accessible. I designed this entire project end-to-end, from API integration to UI, focusing on speed, clarity, and real-world usefulness.</p>
        <h3 style="color:#a855f7; text-align:center;"> Pranay Tanaji Bhandare </h3>
        <p style="text-align:center;">
            Email: pranaybhandare765@gmail.com<br>
            LinkedIn: <a href="https://www.linkedin.com/in/pranay-bhandare-4a31762ba" target="_blank">linkedin.com</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

#  HOME / ANALYZER 
else:
    st.markdown('<div class="input-label">Enter Researcher Name or Semantic Scholar ID :</div>', unsafe_allow_html=True)
    query = st.text_input("", placeholder="e.g. Yoshua Bengio or 1741105", label_visibility="collapsed")

    if st.button("Analyze Researcher"):
        if not query.strip():
            st.warning("Please enter a name or ID")
        else:
            with st.spinner("Searching & fetching papers..."):
                author_id = None
                author_name = "Unknown Researcher"
                try:
                    if query.strip().isdigit():
                        author_id = query.strip()
                        r = requests.get(f"https://api.semanticscholar.org/graph/v1/author/{author_id}", params={"fields":"name"}, timeout=15)
                        author_name = safe_get_json(r).get("name", author_name)
                    else:
                        r = requests.get("https://api.semanticscholar.org/graph/v1/author/search", params={"query":query,"limit":10}, timeout=15)
                        data = safe_get_json(r).get("data", [])
                        if not data:
                            st.error("Researcher not found!")
                            st.stop()
                        if len(data) == 1:
                            author_id = data[0]["authorId"]
                            author_name = data[0]["name"]
                        else:
                            choice = st.radio("Multiple researchers found. Please select:", 
                                            [f"{d['name']} ({d['authorId']})" for d in data], 
                                            index=0)
                            author_id = choice.split("(")[-1].rstrip(")")
                            author_name = next(d["name"] for d in data if d["authorId"] == author_id)
                except Exception:
                    st.error("Network error. Please try again.")
                    st.stop()

                # Fetch all papers
                papers = []
                offset = 0
                limit = 100
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    while True:
                        r = requests.get(f"https://api.semanticscholar.org/graph/v1/author/{author_id}/papers",
                                        params={"fields":"title,year,citationCount,authors","limit":limit,"offset":offset}, 
                                        timeout=20)
                        batch = safe_get_json(r).get("data", [])
                        if not batch: break
                        papers.extend(batch)
                        offset += limit
                        progress_bar.progress(min(offset / 3000, 1.0))
                        status_text.text(f"Fetched {len(papers)} papers...")
                        time.sleep(0.1)
                        if offset >= 5000: break
                except:
                    pass
                finally:
                    progress_bar.empty()
                    status_text.empty()

                if not papers:
                    st.error("No publications found for this researcher.")
                else:
                    citations = [p.get("citationCount", 0) or 0 for p in papers]

                    metrics = {
                        "Total Papers": len(papers),
                        "Total Citations": sum(citations),
                        "Classic h-index": h_index(citations),
                        "Freshness-Weighted h": freshness_h(papers),
                        "CRI (Collab-Resilient)": cri(papers),
                        "CLS Score": cls(papers),
                    }

                    st.markdown(f"<h2 class='researcher-name'>{author_name}</h2>", unsafe_allow_html=True)

                    cols = st.columns(3)
                    for i, (label, value) in enumerate(metrics.items()):
                        with cols[i % 3]:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">{label}</div>
                                <div class="metric-value">{value}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    # PDF Report
                    buffer = io.BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30*mm, leftMargin=20*mm, rightMargin=20*mm)
                    styles = getSampleStyleSheet()
                    story = []

                    story.append(Paragraph("Levelling Up Academia – Research Impact Report", styles["Title"]))
                    story.append(Spacer(1, 12))
                    story.append(Paragraph(f"<b>Researcher:</b> {author_name}", styles["Heading2"]))
                    story.append(Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles["Normal"]))
                    story.append(Spacer(1, 20))

                    table_data = [["Metric", "Value"]] + [[k, str(v)] for k, v in metrics.items()]
                    table = Table(table_data, colWidths=[360, 140])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#c084fc")),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                        ('GRID', (0,0), (-1,-1), 0.8, colors.HexColor("#e9d5ff")),
                        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#faf5ff")),
                        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0,0), (-1,-1), 12),
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 20))

                    top_papers = sorted(papers, key=lambda x: x.get("citationCount", 0) or 0, reverse=True)[:10]
                    if top_papers:
                        story.append(Paragraph("<b>Top 10 Most Cited Papers</b>", styles["Heading3"]))
                        story.append(Spacer(1, 8))
                        for idx, p in enumerate(top_papers, 1):
                            title = p.get("title", "Untitled")
                            year = p.get("year", "n/a")
                            cites = p.get("citationCount", 0) or 0
                            authors = ", ".join(a.get("name", "") for a in p.get("authors", [])[:6])
                            if len(p.get("authors", [])) > 6:
                                authors += " et al."
                            story.append(Paragraph(f"{idx}. <b>{title}</b> ({year}) — <font color='#7c3aed'>{cites}</font> citations", styles["Normal"]))
                            story.append(Paragraph(f"    <i>{authors}</i>", styles["Normal"]))
                            story.append(Spacer(1, 6))

                    doc.build(story)
                    buffer.seek(0)

                    st.download_button(
                        label="Download Professional PDF Report",
                        data=buffer,
                        file_name=f"{author_name.replace(' ', '_')}_Research_Impact_Report.pdf",
                        mime="application/pdf"
                    )