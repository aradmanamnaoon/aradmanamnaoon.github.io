"""Generate a polished, one-page technical CV as a searchable, hyperlinked PDF.

Reproducible command: python generate_cv.py --output Profile.pdf
Requires reportlab and the Ubuntu fonts-lato package (or DejaVu fallback).
Facts are drawn from public projects; no unverified education or affiliations.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit

PAGE_W, PAGE_H = A4
LEFT, RIGHT = 45, PAGE_W - 45
TEXT_W = RIGHT - LEFT
NAVY = HexColor('#13273A')
INK = HexColor('#21344A')
MUTED = HexColor('#516575')
TEAL = HexColor('#087C83')
PALE = HexColor('#E8F5F4')
RULE = HexColor('#DBE5E8')
WHITE = HexColor('#FFFFFF')

LINKS = {
    'Website': 'https://aradmanamnaoon.github.io/',
    'GitHub': 'https://github.com/aradmanamnaoon',
    'Hugging Face': 'https://huggingface.co/aradmanamnaoon',
    'LinkedIn': 'https://www.linkedin.com/in/seyyed-arad-hosseini-moghaddam',
    'MRI project': 'https://github.com/aradmanamnaoon/medical-image-segmentation',
    'CohortSeal': 'https://github.com/aradmanamnaoon/cohortseal',
    'Holdout Ledger': 'https://github.com/aradmanamnaoon/Holdout-Ledger',
    'Persian GPT': 'https://huggingface.co/aradmanamnaoon/persian-lm-from-scratch',
    'Model audit': 'https://github.com/aradmanamnaoon/aradmanamnaoon/blob/main/audits/PERSIAN_LM_HEADER_REPORT.md',
    'Research assistant': 'https://github.com/aradmanamnaoon/ai-research-assistant-platform',
    'PsyLex Studio': 'https://github.com/aradmanamnaoon/PsyLex-Studio',
}


def register_fonts():
    choices = [
        ('/usr/share/fonts/truetype/lato/Lato-Regular.ttf',
         '/usr/share/fonts/truetype/lato/Lato-Bold.ttf',
         '/usr/share/fonts/truetype/lato/Lato-Heavy.ttf'),
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    ]
    for regular, bold, heavy in choices:
        if all(Path(x).exists() for x in (regular, bold, heavy)):
            for tag, file in [('Regular', regular), ('Bold', bold), ('Heavy', heavy)]:
                pdfmetrics.registerFont(TTFont(tag, file))
            return
    raise RuntimeError('Lato or DejaVu TTF fonts required')


def text(c, x, y, value, font='Regular', size=9, color=INK):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, value)


def lines(c, content, x, y, width=TEXT_W, size=9.1, leading=12.7,
          font='Regular', color=INK):
    for line in simpleSplit(content, font, size, width):
        text(c, x, y, line, font, size, color)
        y -= leading
    return y


def section(c, label, y):
    text(c, LEFT, y, label.upper(), 'Heavy', 9.05, TEAL)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(LEFT + max(110, pdfmetrics.stringWidth(label.upper(), 'Heavy', 9.05) + 17), y + 2.0, RIGHT, y + 2.0)
    return y - 19


def project(c, y, heading, tags, description, links, max_desc_width=TEXT_W):
    text(c, LEFT, y, heading, 'Heavy', 10.55, NAVY)
    text(c, LEFT + pdfmetrics.stringWidth(heading, 'Heavy', 10.55) + 10,
         y + 0.4, tags, 'Regular', 8.1, MUTED)
    y -= 14.6
    y = lines(c, description, LEFT, y, width=max_desc_width,
              size=9.0, leading=12.6)
    y -= 1.1
    x = LEFT
    for label in links:
        value = label + '  /  '
        size = 8.3
        text(c, x, y, value, 'Bold', size, TEAL)
        w = pdfmetrics.stringWidth(label, 'Bold', size)
        c.linkURL(LINKS[label], (x - 2, y - 2, x + w + 2, y + 9), relative=0)
        x += pdfmetrics.stringWidth(value, 'Bold', size) + 5
    return y - 23


def render(output):
    register_fonts()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=A4, pageCompression=1)
    c.setTitle('Seyyed Arad Hosseini Moghaddam | AI Engineer & Data Scientist | CV')
    c.setAuthor('Seyyed Arad Hosseini Moghaddam')
    c.setSubject('Technical CV: medical imaging, Persian NLP, research software and reproducible ML')
    c.setKeywords('CV, AI engineer, data scientist, PyTorch, MONAI, NLP, research software')

    # Header: editorial typography on restrained navy field.
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 150, PAGE_W, 150, stroke=0, fill=1)
    c.setFillColor(TEAL)
    c.rect(LEFT, PAGE_H - 36, 42, 3.0, fill=1, stroke=0)
    text(c, LEFT, PAGE_H - 62, 'SEYYED ARAD HOSSEINI MOGHADDAM', 'Heavy', 18.35, WHITE)
    text(c, LEFT, PAGE_H - 85, 'AI ENGINEER  /  DATA SCIENTIST', 'Bold', 11.2, HexColor('#86D8D1'))
    text(c, LEFT, PAGE_H - 105,
         'Medical imaging   •   Persian NLP   •   Reproducible machine learning',
         'Regular', 9.05, HexColor('#D4E2E9'))

    # Three public contact links plus LinkedIn, neatly spaced.
    x = LEFT
    for label in ['Website', 'GitHub', 'Hugging Face', 'LinkedIn']:
        value = label
        tsize = 9.15
        text(c, x, PAGE_H - 135, value, 'Bold', tsize, WHITE)
        w = pdfmetrics.stringWidth(value, 'Bold', tsize)
        c.linkURL(LINKS[label], (x - 3, PAGE_H - 140, x + w + 3, PAGE_H - 124), relative=0)
        x += w + 32
        if label != 'LinkedIn':
            c.setFillColor(HexColor('#6096A0'))
            c.circle(x - 16, PAGE_H - 132, 1.5, stroke=0, fill=1)

    y = PAGE_H - 174
    y = section(c, 'Professional profile', y)
    y = lines(c,
        'I build inspectable machine-learning systems across 3D medical imaging, Persian language models, '
        'agentic retrieval, and dataset-leakage auditing. My developing research direction connects '
        'reproducible AI engineering with psychology and neuroscience.',
        LEFT, y, size=9.35, leading=13.2)
    y -= 14
    y = section(c, 'Selected technical work', y)

    y = project(c, y,
        '3D cardiac MRI segmentation', 'PYTORCH  /  MONAI',
        'Implemented a 3D U-Net pipeline for left-atrium segmentation on MSD Task02 Heart, covering '
        'NIfTI preprocessing, patch training and sliding-window inference. Project records report '
        'Dice 0.8821; this result is author-reported, not independently or clinically validated.',
        ['MRI project'])

    y = project(c, y,
        'CohortSeal + Holdout Ledger', 'EVALUATION INTEGRITY',
        'Built open research-software tools to audit dataset splits for group leakage and exact duplicates. '
        'Documented testable, reviewable integrity checks rather than claiming clinical verification.',
        ['CohortSeal', 'Holdout Ledger'])

    y = project(c, y,
        'Persian language-model research', 'TRANSFORMERS  /  NLP',
        'Released public Persian language-model and tokenizer artifacts. Audited exported checkpoint '
        'metadata: 134.99M stored tensor elements versus a 110.4M architecture claim; runtime '
        'weight tying and reported language-model metrics remain unverified.',
        ['Persian GPT', 'Model audit'])

    y = project(c, y,
        'AI Research Assistant Platform', 'LANGGRAPH  /  FASTAPI',
        'Developed agent-based retrieval and research workflows with structured synthesis, '
        'API integration, and offline tests. Published tests do not imply externally verified answer quality.',
        ['Research assistant'])

    y = project(c, y,
        'Persian NLP + psychology-language tools', 'QLORA  /  TRANSLATION',
        'Published experimental English–Persian translation and text-to-JSON models, plus a '
        'psychology-terminology desktop workbench. Models are not clinically validated.',
        ['PsyLex Studio'])

    y += 4
    y = section(c, 'Technical toolkit', y)
    y = lines(c,
        'Python  /  PyTorch  /  MONAI  /  Transformers  /  Hugging Face  /  LoRA & QLoRA  /  '
        'LangGraph  /  RAG  /  FastAPI  /  GitHub Actions  /  Docker  /  statistical analysis',
        LEFT, y, size=9.0, leading=13.0)
    y -= 12
    y = section(c, 'Research direction', y)
    y = lines(c,
        'Computational psychology and neuroscience, transparent benchmark design, medical AI evaluation, '
        'data provenance, and reproducible scientific software. Interested in well-scoped research collaborations.',
        LEFT, y, size=9.0, leading=12.8)

    # Footer - also clarifies evidence/credentials without weakening the lead.
    c.setFillColor(PALE)
    c.roundRect(LEFT, 31, TEXT_W, 35, 5, stroke=0, fill=1)
    text(c, LEFT + 10, 50,
         'Evidence note', 'Heavy', 8.0, TEAL)
    text(c, LEFT + 87, 50,
         'Project metrics are author-reported unless explicitly audited.', 'Regular', 8.0, INK)
    text(c, LEFT + 10, 38,
         'No degrees, research affiliations, clinical credentials, or publications are asserted.',
         'Regular', 7.65, MUTED)
    if y < 75:
        raise RuntimeError(f'CV body collides with footer: last baseline at {y:.1f} pt')
    c.setFillColor(MUTED)
    text(c, LEFT, 17, 'PUBLIC TECHNICAL CV  •  OCTOBER 2026', 'Bold', 7.5, MUTED)
    c.drawRightString(RIGHT, 17, 'Linked artifacts • Clickable links • Searchable text')
    c.showPage()
    c.save()
    print(f'CV generated: {output}; bottom content baseline y={y:.1f}')


if __name__ == '__main__':
    arg = argparse.ArgumentParser()
    arg.add_argument('--output', default='Profile.pdf')
    render(arg.parse_args().output)
