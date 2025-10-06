import difflib
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import sessionmaker, declarative_base

# ======================
# FastAPI Setup
# ======================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# Database Setup
# ======================
DATABASE_URL = "postgresql+psycopg2://postgres:Cvhs12345@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class PDFComparison(Base):
    __tablename__ = "pdf_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    filename1 = Column(String, nullable=False)
    filename2 = Column(String, nullable=False)
    differences = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

Base.metadata.create_all(bind=engine)

# ======================
# PDF Extract Function
# ======================
def extract_text_from_pdf(file) -> str:
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ======================
# Clear Diff Formatter
# ======================
def pretty_diff(text1: str, text2: str) -> str:
    diff = difflib.ndiff(text1.splitlines(), text2.splitlines())
    changes = []
    line_num = 0
    for line in diff:
        if line.startswith("  "):  # same line
            line_num += 1
        elif line.startswith("- "):  # removed
            changes.append(f"❌ Line {line_num}: {line[2:]}")
            line_num += 1
        elif line.startswith("+ "):  # added
            changes.append(f"✅ Line {line_num}: {line[2:]}")
    return "\n".join(changes) if changes else "No differences found!"

# ======================
# API Endpoint
# ======================
@app.post("/compare-pdfs/")
async def compare_pdfs(pdf1: UploadFile = File(...), pdf2: UploadFile = File(...)):
    # Extract text
    text1 = extract_text_from_pdf(pdf1.file)
    text2 = extract_text_from_pdf(pdf2.file)

    # Get structured differences
    differences = pretty_diff(text1, text2)

    # Save to DB
    db = SessionLocal()
    record = PDFComparison(
        filename1=pdf1.filename,
        filename2=pdf2.filename,
        differences=differences
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    db.close()

    return {
        "message": "Comparison stored successfully!",
        "id": record.id,
        "differences": differences
    }
