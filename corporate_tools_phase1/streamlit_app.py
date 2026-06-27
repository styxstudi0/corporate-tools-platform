"""Streamlit test bench for the corporate tools platform."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from activity_to_training import training_material
from audit_engine import audit_package
from category_lister import list_categories
from company_finance_lookup import lookup_company
from contract_analyzer import analyze_contract
from csv_cleaner import clean_csv
from data_cleanup_advanced import cleanup_csv
from data_extractor import extract_data
from email_template_generator import TEMPLATES, generate_email
from email_to_workflow import email_workflow
from excel_reverse_engineering import analyze_workbook
from excel_flattener import flatten_workbook
from excel_splitter import split_excel
from excel_to_system import plan_system
from folder_to_knowledge_base import build_kb_plan
from government_forms import generate_forms_packet
from grammar_checker import grammar_check
from hr_toolkit import (
    employee_evaluation_template,
    generate_job_description,
    generate_questions,
    parse_resume,
)
from invoice_generator import generate_invoice, generate_invoice_pdf
from invoice_matcher import invoice_match
from invoice_to_accounting import accounting_entries
from knowledge_assistant import answer_question, build_index
from meeting_notes_generator import generate_notes
from news_search import search_news
from patent_intelligence import fetch_patents
from pdf_suite import compress, extract_text, merge, rotate, split
from policy_impact_analyzer import policy_impact
from process_recorder import process_document
from pubmed_research import search_pubmed
from resume_formatter import resume_to_html
from rfp_generator import rfp_response
from sop_to_automation import sop_automation
from vendor_comparison import compare_vendors


st.set_page_config(page_title="Corporate Tools Lab", page_icon="CT", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #f4f6f8; color: #17212b; }
    [data-testid="stSidebar"] { background: #152238; }
    [data-testid="stSidebar"] * { color: #f7f9fb; }
    .tool-header { border-left: 5px solid #e35d36; padding: .2rem 0 .2rem 1rem; margin-bottom: 1rem; }
    .tool-header h1 { font-size: 2rem; margin: 0; letter-spacing: 0; }
    .tool-header p { color: #5d6975; margin: .35rem 0 0; }
    .status-note { background: #e8f4ee; border: 1px solid #b7dcc7; padding: .7rem .9rem; border-radius: 6px; }
    div[data-testid="stMetric"] { background: white; border: 1px solid #d9e0e6; padding: .8rem; border-radius: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)


TEXT_TOOLS = {
    "Vendor Comparison": ("Procurement", "Compare proposals, pricing, features, and risks.", compare_vendors),
    "Government Forms": ("Compliance", "Create a filing preparation packet from business details.", generate_forms_packet),
    "Audit Engine": ("Compliance", "Turn audit notes into an evidence and control package.", audit_package),
    "RFP Generator": ("Sales", "Structure an RFP response from requirements and company knowledge.", rfp_response),
    "Process Recorder": ("Operations", "Convert recorded actions into an SOP and checklist.", process_document),
    "Email-to-Workflow": ("Automation", "Convert an email into tasks, approvals, and workflow steps.", email_workflow),
    "Contract Analyzer": ("Legal", "Extract obligations, dates, risks, and renewal signals.", analyze_contract),
    "Invoice-to-Accounting": ("Finance", "Create an accounting-entry plan from invoice text.", accounting_entries),
    "SOP-to-Automation": ("Automation", "Convert a procedure into an executable automation blueprint.", sop_automation),
    "Policy Impact Analyzer": ("Compliance", "Identify affected teams, systems, documents, and controls.", policy_impact),
    "Activity-to-Training": ("HR", "Generate onboarding and training material from employee activity.", training_material),
}

TOOLS = {
    "CSV Cleaner": ("Data", "Normalize headers, trim values, remove blank rows, and deduplicate."),
    "Advanced Data Cleanup": ("Data", "Validate, normalize, deduplicate, and review business data."),
    "Excel Splitter": ("Spreadsheets", "Split one workbook into a file for every worksheet."),
    "Excel Reverse Engineering": ("Spreadsheets", "Explain formulas, dependencies, errors, and workbook structure."),
    "Excel-to-System": ("Spreadsheets", "Turn a workbook into a database and workflow blueprint."),
    "PDF Suite": ("Documents", "Merge, split, compress, rotate, or extract text from PDFs."),
    "Data Extractor": ("Documents", "Extract structured data from PDFs, images, receipts, and statements."),
    "Knowledge Assistant": ("Knowledge", "Ask questions across uploaded documents using local retrieval."),
    "Folder-to-Knowledge Base": ("Knowledge", "Inventory uploaded files and plan a searchable knowledge base."),
    "Meeting Notes Generator": ("Writing", "Create structured notes, decisions, and actions from a transcript."),
    "Grammar Checker": ("Writing", "Apply lightweight grammar, capitalization, and spacing fixes."),
    "Resume Formatter": ("HR", "Convert a plain-text resume into a polished HTML document."),
    "HR Toolkit": ("HR", "Parse resumes, generate job descriptions, questions, and evaluations."),
    "Invoice Generator": ("Finance", "Create a downloadable HTML invoice."),
    "Invoice Matcher": ("Finance", "Compare invoice, purchase order, and receipt values."),
    "Email Template Generator": ("Writing", "Generate reusable business email templates."),
    "File Organizer & Renamer": ("Files", "Preview organized folders and batch-renamed files."),
    "PubMed Research Extractor": ("Research", "Find publications and institutional author contacts from PubMed."),
    "Google News Search": ("Research", "Find recent topic and company coverage through Google News RSS."),
    "Company Finance Lookup": ("Research", "Look up public-company symbols, exchanges, and profiles."),
    "Patent Intelligence": ("Research", "Collect inventor, assignee, status, and PDF metadata for patents."),
    "Excel Merge Flattener": ("Spreadsheets", "Unmerge Excel ranges and fill every cell with the merged value."),
    "Category Lister": ("Spreadsheets", "Extract a clean, unique category list from an Excel workbook."),
    **{name: (category, description) for name, (category, description, _) in TEXT_TOOLS.items()},
}


def save_upload(upload, folder: Path) -> Path:
    path = folder / Path(upload.name).name
    path.write_bytes(upload.getvalue())
    return path


def download_json(data: object, name: str = "result.json") -> None:
    st.download_button("Download JSON", json.dumps(data, indent=2, default=str), name, "application/json")


def render_result(data: object) -> None:
    if isinstance(data, (dict, list)):
        st.json(data, expanded=True)
        download_json(data)
    else:
        st.text_area("Result", str(data), height=360)
        st.download_button("Download result", str(data), "result.txt", "text/plain")


def text_tool(name: str) -> None:
    _, _, runner = TEXT_TOOLS[name]
    sample = st.text_area("Business input", height=280, placeholder="Paste source text, notes, requirements, or document content here...")
    if st.button("Run tool", type="primary", disabled=not sample.strip()):
        with st.spinner("Building structured result..."):
            render_result(runner(sample))


def csv_tools(name: str) -> None:
    upload = st.file_uploader("Upload CSV", type=["csv"])
    dedupe = st.checkbox("Remove duplicate rows", value=True)
    if upload and st.button("Clean data", type="primary"):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = save_upload(upload, folder)
            if name == "Advanced Data Cleanup":
                render_result(cleanup_csv(source))
            else:
                output = folder / "cleaned.csv"
                clean_csv(source, output, dedupe=dedupe)
                st.success("CSV cleaned successfully.")
                st.download_button("Download cleaned CSV", output.read_bytes(), "cleaned.csv", "text/csv")


def excel_tools(name: str) -> None:
    upload = st.file_uploader("Upload Excel workbook", type=["xlsx"])
    if upload and st.button("Analyze workbook" if name != "Excel Splitter" else "Split workbook", type="primary"):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = save_upload(upload, folder)
            if name == "Excel Reverse Engineering":
                render_result(analyze_workbook(source))
            elif name == "Excel-to-System":
                render_result(plan_system(source))
            else:
                outputs = split_excel(source, folder / "sheets")
                bundle = io.BytesIO()
                with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
                    for output in outputs:
                        archive.write(output, output.name)
                st.success(f"Created {len(outputs)} worksheet files.")
                st.download_button("Download worksheet ZIP", bundle.getvalue(), "split_workbook.zip", "application/zip")


def pdf_tool() -> None:
    action = st.segmented_control("Operation", ["Merge", "Split", "Compress", "Rotate", "Extract text"], default="Merge")
    multiple = action == "Merge"
    uploads = st.file_uploader("Upload PDF files" if multiple else "Upload PDF", type=["pdf"], accept_multiple_files=multiple)
    degrees = st.selectbox("Rotation", [90, 180, 270], disabled=action != "Rotate")
    ready = bool(uploads)
    if st.button("Process PDF", type="primary", disabled=not ready):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            files = [save_upload(item, folder) for item in uploads] if multiple else [save_upload(uploads, folder)]
            if action == "Merge":
                output = merge(files, folder / "merged.pdf")
            elif action == "Compress":
                output = compress(files[0], folder / "compressed.pdf")
            elif action == "Rotate":
                output = rotate(files[0], folder / "rotated.pdf", degrees)
            elif action == "Extract text":
                output = extract_text(files[0], folder / "extracted.txt")
            else:
                pages = split(files[0], folder / "pages")
                bundle = io.BytesIO()
                with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
                    for page in pages:
                        archive.write(page, page.name)
                st.download_button("Download pages ZIP", bundle.getvalue(), "pdf_pages.zip", "application/zip")
                return
            mime = "text/plain" if output.suffix == ".txt" else "application/pdf"
            st.download_button(f"Download {output.name}", output.read_bytes(), output.name, mime)


def extraction_tool() -> None:
    uploads = st.file_uploader("Upload business documents", type=["pdf", "png", "jpg", "jpeg", "txt"], accept_multiple_files=True)
    output_format = st.selectbox("Output format", ["json", "csv", "xlsx"])
    if st.button("Extract data", type="primary", disabled=not uploads):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            inputs = [save_upload(item, folder) for item in uploads]
            output = folder / f"extracted.{output_format}"
            extract_data(inputs, output, output_format)
            mime = {"json": "application/json", "csv": "text/csv", "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}[output_format]
            if output_format == "json":
                st.json(json.loads(output.read_text(encoding="utf-8")))
            st.download_button("Download extracted data", output.read_bytes(), output.name, mime)


def knowledge_tool(plan_only: bool = False) -> None:
    uploads = st.file_uploader("Upload documents", type=["txt", "md", "pdf"], accept_multiple_files=True)
    question = st.text_input("Question", disabled=plan_only, placeholder="What do these documents say about...")
    label = "Build knowledge-base plan" if plan_only else "Ask documents"
    if st.button(label, type="primary", disabled=not uploads or (not plan_only and not question.strip())):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            paths = [save_upload(item, folder) for item in uploads]
            if plan_only:
                render_result(build_kb_plan(folder))
            else:
                st.markdown(answer_question(build_index(paths), question))


def writing_tool(name: str) -> None:
    text = st.text_area("Source text", height=300)
    if st.button("Generate", type="primary", disabled=not text.strip()):
        if name == "Grammar Checker":
            result = grammar_check(text)
            render_result(result)
        elif name == "Meeting Notes Generator":
            render_result(generate_notes(text))
        else:
            html = resume_to_html(text)
            st.components.v1.html(html, height=500, scrolling=True)
            st.download_button("Download formatted resume", html, "resume.html", "text/html")


def hr_tool() -> None:
    action = st.segmented_control("HR workflow", ["Resume parser", "Job description", "Interview questions", "Evaluation"], default="Resume parser")
    if action == "Resume parser":
        text = st.text_area("Resume text", height=300)
        if st.button("Parse resume", type="primary", disabled=not text.strip()):
            render_result(parse_resume(text))
        return
    role = st.text_input("Role", "Data Analyst")
    skills = st.text_input("Skills, comma separated", "SQL, Excel, Python")
    level = st.selectbox("Level", ["Junior", "Mid-level", "Senior", "Lead"], disabled=action != "Job description")
    if st.button("Generate", type="primary", disabled=not role.strip()):
        skill_list = [item.strip() for item in skills.split(",") if item.strip()]
        if action == "Job description":
            render_result(generate_job_description(role, level, skill_list))
        elif action == "Interview questions":
            render_result(generate_questions(role, skill_list, 12))
        else:
            render_result(employee_evaluation_template(role))


def invoice_generator_tool() -> None:
    left, right = st.columns(2)
    with left:
        number = st.text_input("Invoice number", "INV-1001")
        business = st.text_input("Business name", "Your Company")
        client = st.text_input("Client", "Acme Corp")
        date = st.date_input("Invoice date")
    with right:
        description = st.text_input("Item description", "Consulting services")
        quantity = st.number_input("Quantity", min_value=1.0, value=1.0)
        price = st.number_input("Unit price", min_value=0.0, value=1000.0)
        tax = st.number_input("Tax rate", min_value=0.0, max_value=1.0, value=0.18, step=0.01)
    if st.button("Generate invoice", type="primary"):
        data = {"invoice_number": number, "date": str(date), "business_name": business, "client_name": client, "tax_rate": tax, "items": [{"description": description, "quantity": quantity, "unit_price": price}]}
        html = generate_invoice(data)
        pdf = generate_invoice_pdf(data)
        st.components.v1.html(html, height=620, scrolling=True)
        html_col, pdf_col = st.columns(2)
        html_col.download_button("Download HTML", html, f"{number}.html", "text/html")
        pdf_col.download_button("Download PDF", pdf, f"{number}.pdf", "application/pdf")


def invoice_matcher_tool() -> None:
    invoice = st.text_area("Invoice", height=160)
    po = st.text_area("Purchase order", height=160)
    receipt = st.text_area("Delivery receipt", height=160)
    if st.button("Match documents", type="primary", disabled=not (invoice and po and receipt)):
        render_result(invoice_match(invoice, po, receipt))


def email_tool() -> None:
    template = st.selectbox("Template", sorted(TEMPLATES))
    name = st.text_input("Recipient", "Alex")
    company = st.text_input("Company", "Acme")
    topic = st.text_input("Topic", "our proposal")
    sender = st.text_input("Sender", "Team")
    if st.button("Generate email", type="primary"):
        result = generate_email(template, {"name": name, "company": company, "topic": topic, "sender": sender, "invoice_number": "INV-1001", "due_date": "Friday", "time_option": "Tuesday at 2 PM"})
        render_result(result)


def file_preview_tool() -> None:
    uploads = st.file_uploader("Choose files", accept_multiple_files=True)
    pattern = st.text_input("Rename pattern", "Document_{num}{ext}")
    if uploads:
        categories = {"pdf": "Documents", "docx": "Documents", "xlsx": "Spreadsheets", "csv": "Spreadsheets", "png": "Images", "jpg": "Images", "zip": "Archives"}
        preview = []
        for index, item in enumerate(uploads, 1):
            suffix = Path(item.name).suffix
            target = pattern.replace("{num}", str(index)).replace("{ext}", suffix)
            preview.append({"original": item.name, "category": categories.get(suffix.lstrip(".").lower(), "Other"), "new_name": target})
        st.dataframe(preview, use_container_width=True)
        st.caption("Preview mode keeps browser uploads unchanged. Server deployment can enable direct folder operations.")


def research_tool(name: str) -> None:
    if name == "PubMed Research Extractor":
        query = st.text_area("PubMed query", value='("workflow automation") AND 2024:2026[Date - Publication]', height=120)
        email = st.text_input("Contact email required by NCBI", placeholder="you@company.com")
        countries = st.multiselect("Affiliation countries", ["United States", "USA", "United Kingdom", "India", "Canada", "Australia", "Germany", "France", "China", "Japan"], default=[])
        limit = st.number_input("Maximum publications", min_value=10, max_value=1000, value=100, step=10)
        if st.button("Search PubMed", type="primary", disabled=not (query.strip() and email.strip())):
            render_result(search_pubmed(query, email, countries, limit=int(limit)))
    elif name == "Google News Search":
        query = st.text_input("Topic, company, or keyword", "business automation")
        limit = st.slider("Maximum articles", 1, 30, 10)
        if st.button("Search news", type="primary", disabled=not query.strip()):
            render_result(search_news(query, limit))
    elif name == "Company Finance Lookup":
        company = st.text_input("Company name", "Microsoft")
        if st.button("Look up company", type="primary", disabled=not company.strip()):
            render_result(lookup_company(company))
    else:
        raw = st.text_area("Patent document numbers", placeholder="US12345678B2\nEP1234567A1", height=180)
        numbers = [value.strip() for value in raw.replace(",", "\n").splitlines() if value.strip()]
        if st.button("Fetch patents", type="primary", disabled=not numbers):
            render_result(fetch_patents(numbers))


def spreadsheet_discovery_tool(name: str) -> None:
    upload = st.file_uploader("Upload Excel workbook", type=["xlsx"])
    if upload and st.button("Flatten workbook" if name == "Excel Merge Flattener" else "Extract categories", type="primary"):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = save_upload(upload, folder)
            if name == "Excel Merge Flattener":
                output = folder / "flattened_workbook.xlsx"
                result = flatten_workbook(source, output)
                st.json(result)
                st.download_button("Download flattened workbook", output.read_bytes(), output.name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                result = list_categories(source)
                st.metric("Unique categories", result["category_count"])
                st.dataframe({"Category": result["categories"]}, use_container_width=True)
                st.download_button("Download category list", "Category\n" + "\n".join(result["categories"]), "categories.csv", "text/csv")


with st.sidebar:
    st.title("Corporate Tools")
    st.caption("Unified testing workspace")
    search = st.text_input("Search tools", placeholder="invoice, PDF, HR...")
    categories = ["All"] + sorted({category for category, _ in TOOLS.values()})
    category = st.selectbox("Category", categories)
    filtered = [name for name, (group, _) in TOOLS.items() if (category == "All" or group == category) and search.lower() in name.lower()]
    if not filtered:
        st.warning("No matching tools")
        filtered = list(TOOLS)
    selection_key = f"tool_{category}_{search.strip().lower()}"
    selected = st.selectbox("Tool", filtered, key=selection_key)
    st.divider()
    st.markdown("<div class='status-note'>Local MVP<br><strong>No customer data is uploaded to a cloud service.</strong></div>", unsafe_allow_html=True)

group, description = TOOLS[selected]
st.markdown(f"<div class='tool-header'><h1>{selected}</h1><p>{description}</p></div>", unsafe_allow_html=True)
metric1, metric2, metric3 = st.columns(3)
metric1.metric("Available tools", len(TOOLS))
metric2.metric("Category", group)
metric3.metric("Runtime", "Local Python")
st.divider()

try:
    if selected in TEXT_TOOLS:
        text_tool(selected)
    elif selected in {"CSV Cleaner", "Advanced Data Cleanup"}:
        csv_tools(selected)
    elif selected in {"Excel Splitter", "Excel Reverse Engineering", "Excel-to-System"}:
        excel_tools(selected)
    elif selected == "PDF Suite":
        pdf_tool()
    elif selected == "Data Extractor":
        extraction_tool()
    elif selected == "Knowledge Assistant":
        knowledge_tool()
    elif selected == "Folder-to-Knowledge Base":
        knowledge_tool(plan_only=True)
    elif selected in {"Meeting Notes Generator", "Grammar Checker", "Resume Formatter"}:
        writing_tool(selected)
    elif selected == "HR Toolkit":
        hr_tool()
    elif selected == "Invoice Generator":
        invoice_generator_tool()
    elif selected == "Invoice Matcher":
        invoice_matcher_tool()
    elif selected == "Email Template Generator":
        email_tool()
    elif selected == "File Organizer & Renamer":
        file_preview_tool()
    elif selected in {"PubMed Research Extractor", "Google News Search", "Company Finance Lookup", "Patent Intelligence"}:
        research_tool(selected)
    elif selected in {"Excel Merge Flattener", "Category Lister"}:
        spreadsheet_discovery_tool(selected)
except Exception as exc:
    st.error(f"The tool could not complete this test: {exc}")
    st.caption("Check optional PDF, Excel, or OCR dependencies when processing those file types.")
