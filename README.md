# AI Presentation Generator

An AI-powered tool that extracts brand profiles from reference materials and generates fully-branded, editable `.pptx` presentations from content.

## Features

### Brand Extraction Engine
Extracts structured brand profiles from multiple input types:
- **Brand Guide PDFs** — colors, fonts, layout rules, tone of voice
- **Existing Presentations** (.pptx) — reverse-engineers visual identity
- **Screenshots / Images** — visual style extraction via Claude Vision
- **Logo Files** — dominant color extraction
- **Website URLs** — palette and typography from live CSS
- **Manual Input** — direct hex/font entry

### Brand Profile Management
- Create, edit, merge, duplicate, archive, export, import profiles
- Multi-source reconciliation with priority hierarchy (brand guide > existing deck > website > logo)
- Conflict detection and surfacing for user review
- JSON export/import for portability

### Content Input Module
Multiple content input methods:
- Structured markdown outline
- Free-form text / brain dump
- Document upload (.docx, .pdf, .md, .txt)
- CSV / XLSX data files → auto chart slides
- Web URL scraping
- Conversational (chat history)

### Slide Generation Engine
10 slide types with brand-consistent layouts:
- Title, Section Divider
- Content (Text), Content (Visual)
- Data/Chart (native PowerPoint charts)
- Comparison, Timeline
- Quote/Callout, Team/Bio
- Thank You/CTA

All output is fully editable `.pptx`.

## Installation

```bash
pip install -r requirements.txt
```

Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

## Usage

### Extract a brand profile

```bash
# From a brand guide PDF
python main.py extract --input brand_guide.pdf --name "Acme Corp"

# From an existing presentation
python main.py extract --input existing_deck.pptx --name "Acme Corp"

# From a logo
python main.py extract --input logo.png --type logo --name "Acme Corp"

# From a website
python main.py extract --input https://example.com --name "Acme Corp"
```

### Generate a presentation

```bash
# From a markdown outline
python main.py generate \
  --profile <profile-id> \
  --content outline.md \
  --output deck.pptx \
  --purpose Pitch \
  --audience "Executive"

# From free-form text inline
python main.py generate \
  --profile <profile-id> \
  --text "Q3 results were strong. Revenue up 23%..." \
  --output quarterly_review.pptx

# From a Word document
python main.py generate \
  --profile <profile-id> \
  --content proposal.docx \
  --output client_proposal.pptx

# From CSV data
python main.py generate \
  --profile <profile-id> \
  --content sales_data.csv \
  --output data_deck.pptx
```

### Manage profiles

```bash
# List all profiles
python main.py profiles list

# Show profile details
python main.py profiles show <id>

# Edit a field
python main.py profiles edit <id> colors.primary "#FF5500"
python main.py profiles edit <id> typography.heading_font "Montserrat"

# Export
python main.py profiles export <id> --output profile.json
python main.py profiles export <id> --format summary --output profile.txt

# Import
python main.py profiles import profile.json

# Merge (priority: brand_guide_pdf > website)
python main.py profiles merge <id1> <id2> \
  --types brand_guide_pdf --types website \
  --name "Acme Merged"

# Duplicate for sub-brand
python main.py profiles duplicate <id> --name "Acme Events Theme"

# Archive
python main.py profiles archive <id>
```

### Regenerate a single slide

```bash
# Regenerate slide index 3 with new content
python main.py slide regenerate deck.pptx 3 \
  --profile <id> \
  --content new_slide.json \
  --output updated_deck.pptx
```

The `new_slide.json` format:
```json
{
  "slide_type": "content_text",
  "title": "New Slide Title",
  "body_bullets": ["Point one", "Point two", "Point three"],
  "speaker_notes": "Talk through each bullet..."
}
```

## Content Outline Format

```markdown
# Deck Title

## Slide Title
- Bullet point one
- Bullet point two

### Section Break Title

## Another Slide
Paragraph text goes here directly.

> Featured quote text

## Thank You
- contact@example.com
- +1 555 000 0000
```

## Brand Profile Schema

Profiles are stored as JSON with sections:
- `colors` — primary, secondary (×4), accent (×2), background, text
- `typography` — heading/body fonts, size hierarchy (title→footnote), alignment
- `layout` — aspect ratio, margins, density, white space philosophy
- `visuals` — logo placement, icon style, shape language, chart style
- `content_style` — writing tone, headline style, bullet conventions

Each extracted field includes a confidence score (High/Medium/Low). Low-confidence fields are flagged for review.

## Architecture

```
src/
├── brand_profile.py      # Data models and schema
├── brand_extractor.py    # Multi-source brand extraction (Claude AI)
├── profile_manager.py    # CRUD, merge, export/import
├── content_input.py      # Content processing (Claude AI)
└── slide_generator.py    # .pptx generation (python-pptx)
main.py                   # CLI entry point (click + rich)
```

## Source Priority for Merging

When multiple sources are merged, conflicts are resolved by:

1. Manual overrides (always wins)
2. Brand guide PDF
3. Most recent existing presentation
4. Website
5. Logo / screenshot (least context)

Conflicts are surfaced with side-by-side values and a recommended resolution.
