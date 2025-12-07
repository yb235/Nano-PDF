# Nano PDF Examples

Real-world examples and use cases for Nano PDF.

## Table of Contents

- [Basic Editing](#basic-editing)
- [Presentation Updates](#presentation-updates)
- [Report Generation](#report-generation)
- [Branding and Design](#branding-and-design)
- [Content Updates](#content-updates)
- [Batch Operations](#batch-operations)
- [Creative Use Cases](#creative-use-cases)
- [Workflows and Automation](#workflows-and-automation)

## Basic Editing

### Fix Typos Across Multiple Slides

**Scenario:** Found typos in your deck right before presenting.

```bash
nano-pdf edit pitch_deck.pdf \
  3 "Fix typo: change 'recieve' to 'receive'" \
  7 "Fix typo: change 'seperate' to 'separate'" \
  12 "Fix typo: change 'definately' to 'definitely'"
```

### Update Dates Throughout Document

**Scenario:** Quarterly report with old dates.

```bash
nano-pdf edit Q3_report.pdf \
  1 "Change 'Q2 2024' to 'Q3 2024' in the title" \
  5 "Update 'June 2024' to 'September 2024' in the header" \
  10 "Change date from '06/30/2024' to '09/30/2024'"
```

### Change Single Word

**Scenario:** Product name changed from "ProApp" to "SuperApp".

```bash
nano-pdf edit marketing_deck.pdf \
  1 "Change 'ProApp' to 'SuperApp' in the title" \
  3 "Change all instances of 'ProApp' to 'SuperApp'" \
  5 "Update 'ProApp' logo text to 'SuperApp'"
```

## Presentation Updates

### Create Title Slide

**Scenario:** Need a professional title slide.

```bash
nano-pdf add conference_talk.pdf 0 \
  "Create a title slide with the title 'Building Scalable Systems' and subtitle 'A Deep Dive into Microservices' with speaker name 'Dr. Jane Smith' at the bottom"
```

### Add Agenda Slide

**Scenario:** Presentation needs an overview.

```bash
nano-pdf add workshop.pdf 1 \
  "Create an agenda slide with these sections as bullet points:
  - Introduction (5 min)
  - Demo (15 min)
  - Hands-on Exercise (30 min)
  - Q&A (10 min)"
```

### Update Financial Data

**Scenario:** Revenue numbers changed.

```bash
nano-pdf edit investor_deck.pdf 8 \
  "Update the bar chart: Change Q1 revenue from $2.1M to $2.5M, Q2 from $2.3M to $2.8M, and Q3 from $2.5M to $3.2M. Keep the same colors and style."
```

### Add Thank You Slide

**Scenario:** Need a closing slide.

```bash
nano-pdf add presentation.pdf 20 \
  "Create a thank you slide with 'Thank You!' as the main text, contact email 'contact@company.com', and the company logo" \
  --style-refs "1"
```

### Update Company Logo

**Scenario:** Rebranding with new logo.

```bash
nano-pdf edit corporate_deck.pdf \
  1 "Replace the logo in the top right with the new logo" \
  5 "Update the footer logo to the new design" \
  10 "Change the logo on the contact slide"
```

## Report Generation

### Create Executive Summary

**Scenario:** Need summary page for long report.

```bash
nano-pdf add annual_report.pdf 1 \
  "Create an executive summary page with these key points as bullet points:
  - Revenue increased 25% YoY
  - Expanded to 3 new markets
  - Launched 5 new products
  - Achieved profitability in Q4" \
  --use-context \
  --style-refs "2,3"
```

### Update Charts and Graphs

**Scenario:** Data changed, charts need updating.

```bash
nano-pdf edit financial_report.pdf 12 \
  "Update the pie chart to show: Sales 45%, Marketing 25%, R&D 20%, Operations 10%. Use colors: blue, green, orange, and red respectively."
```

### Add Section Divider

**Scenario:** Multi-section document needs visual breaks.

```bash
nano-pdf add long_document.pdf 15 \
  "Create a section divider page with 'Part 2: Technical Analysis' in large text centered on the page" \
  --style-refs "1"
```

### Correct Statistical Data

**Scenario:** Survey results updated.

```bash
nano-pdf edit research_report.pdf 9 \
  "Update the survey results: Change 'Satisfied: 65%' to 'Satisfied: 72%', 'Neutral: 25%' to 'Neutral: 20%', and 'Unsatisfied: 10%' to 'Unsatisfied: 8%'"
```

## Branding and Design

### Apply New Color Scheme

**Scenario:** Corporate colors changed.

```bash
nano-pdf edit old_template.pdf \
  1 "Change the header background from blue to teal (#008080) and ensure text remains readable" \
  2 "Update the accent color in the sidebar from orange to coral (#FF7F50)" \
  3 "Change all blue elements to the new teal color"
```

### Standardize Font Style

**Scenario:** Inconsistent fonts across slides.

```bash
nano-pdf edit mixed_fonts.pdf \
  5 "Change the font of all body text to match the clean sans-serif font used in slide 1" \
  --style-refs "1"
```

### Add Watermark

**Scenario:** Mark documents as drafts.

```bash
nano-pdf edit document.pdf \
  1 "Add 'DRAFT' watermark diagonally across the page in light gray" \
  2 "Add 'DRAFT' watermark diagonally across the page in light gray" \
  3 "Add 'DRAFT' watermark diagonally across the page in light gray" \
  --resolution "2K"
```

### Update Brand Elements

**Scenario:** Consistent branding across all pages.

```bash
nano-pdf edit sales_deck.pdf \
  1 "Add company tagline 'Innovation Through Excellence' below the logo" \
  5 "Ensure the footer matches the style from slide 1" \
  10 "Add social media icons (Twitter, LinkedIn, Facebook) in the footer" \
  --style-refs "1"
```

## Content Updates

### Update Contact Information

**Scenario:** Office moved, new contact details.

```bash
nano-pdf edit business_card_pdf.pdf 1 \
  "Update address from '123 Old St' to '456 New Ave', change phone from '555-0100' to '555-0200', and update email from 'old@company.com' to 'new@company.com'"
```

### Add Disclaimer

**Scenario:** Legal requirement to add disclaimer.

```bash
nano-pdf edit investment_doc.pdf 1 \
  "Add small text at the bottom of the page: 'Past performance does not guarantee future results. Please consult a financial advisor.'"
```

### Update Product Features

**Scenario:** Product specs changed.

```bash
nano-pdf edit product_sheet.pdf 2 \
  "Update the features list: Add 'AI-powered search' as the first feature, change 'Storage: 100GB' to 'Storage: 1TB', and add 'Multi-language support' at the end"
```

### Translate Key Headings

**Scenario:** Create bilingual version.

```bash
nano-pdf edit english_doc.pdf \
  1 "Add Spanish translation under the title: 'Informe Anual 2025'" \
  3 "Add Spanish subtitle: 'Análisis Financiero' under 'Financial Analysis'"
```

## Batch Operations

### Update Footer on All Pages

**Scenario:** Change footer text across entire document.

```bash
nano-pdf edit document.pdf \
  1 "Change footer text from '© 2024 Company' to '© 2025 Company'" \
  2 "Change footer text from '© 2024 Company' to '© 2025 Company'" \
  3 "Change footer text from '© 2024 Company' to '© 2025 Company'" \
  4 "Change footer text from '© 2024 Company' to '© 2025 Company'" \
  5 "Change footer text from '© 2024 Company' to '© 2025 Company'" \
  --resolution "2K"
```

### Localize Multiple Pages

**Scenario:** Adapt presentation for different region.

```bash
nano-pdf edit us_version.pdf \
  3 "Change currency from '$' to '€' throughout" \
  5 "Change date format from MM/DD/YYYY to DD/MM/YYYY" \
  7 "Change 'color' to 'colour' and 'center' to 'centre'" \
  --resolution "2K"
```

### Progressive Refinement

**Scenario:** Iteratively improve design.

```bash
# First pass: Basic updates with 1K for speed
nano-pdf edit draft.pdf \
  1 "Update title" \
  2 "Fix chart colors" \
  3 "Add logo" \
  --resolution "1K" \
  --output "draft_v2.pdf"

# Second pass: Fine-tune specific pages with 2K
nano-pdf edit draft_v2.pdf \
  2 "Adjust chart to make labels more readable" \
  --resolution "2K" \
  --output "draft_v3.pdf"

# Final pass: High quality export
nano-pdf edit draft_v3.pdf \
  1 "Final polish on title slide" \
  --resolution "4K" \
  --output "final.pdf"
```

## Creative Use Cases

### Create Meme Slides

**Scenario:** Add humor to presentation.

```bash
nano-pdf add fun_presentation.pdf 10 \
  "Create a meme-style slide with 'One Does Not Simply' at the top in Impact font, and 'Deploy on Friday' at the bottom, with a gradient background"
```

### Design Certificates

**Scenario:** Customize certificate template.

```bash
nano-pdf edit certificate_template.pdf 1 \
  "Change the name field to 'Jane Doe', date to 'December 1, 2025', and achievement to 'Outstanding Performance Award'"
```

### Create Social Media Graphics

**Scenario:** Convert slides to social posts.

```bash
nano-pdf edit infographic.pdf 1 \
  "Optimize for Instagram: Make the layout more square, increase font sizes by 30%, and add 'Swipe up for more' at the bottom" \
  --resolution "4K"
```

### Generate Comparison Charts

**Scenario:** Create competitor analysis.

```bash
nano-pdf add analysis.pdf 5 \
  "Create a comparison table with three columns (Us, Competitor A, Competitor B) and rows for Price, Features, Support, and Performance. Use checkmarks and X marks appropriately based on: We have all features, lower price. Competitor A has higher price, fewer features. Competitor B has similar price, good support." \
  --use-context
```

### Event Posters

**Scenario:** Update event details.

```bash
nano-pdf edit event_poster.pdf 1 \
  "Change event date from 'March 15' to 'March 22', update venue from 'City Hall' to 'Convention Center', and change ticket price from '$50' to '$45 (Early Bird)'"
```

## Workflows and Automation

### Monthly Report Pipeline

**Scenario:** Automate monthly report updates.

```bash
#!/bin/bash
# monthly_report.sh

MONTH="January"
YEAR="2025"

nano-pdf edit template_report.pdf \
  1 "Change title to '$MONTH $YEAR Monthly Report'" \
  3 "Update date to $MONTH $YEAR" \
  --output "reports/${MONTH}_${YEAR}_report.pdf"
```

### Bulk Personalization

**Scenario:** Create personalized certificates for 100 people.

```bash
#!/bin/bash
# personalize_certificates.sh

while IFS=, read -r name achievement date; do
    nano-pdf edit certificate_template.pdf 1 \
      "Change recipient name to '$name', achievement to '$achievement', and date to '$date'" \
      --output "certificates/${name// /_}_certificate.pdf" \
      --resolution "2K"
done < participants.csv
```

### Version Control Integration

**Scenario:** Track document changes with git.

```bash
#!/bin/bash
# update_and_commit.sh

# Make changes
nano-pdf edit document.pdf 1 "Update version number to v2.5"

# Commit changes
git add edited_document.pdf
git commit -m "Update version to v2.5"
git tag v2.5
```

### Multi-Language Document Generator

**Scenario:** Generate translated versions.

```bash
#!/bin/bash
# translate_deck.sh

declare -A translations=(
    ["Spanish"]="Informe Anual"
    ["French"]="Rapport Annuel"
    ["German"]="Jahresbericht"
)

for lang in "${!translations[@]}"; do
    nano-pdf edit annual_report.pdf 1 \
      "Change title to '${translations[$lang]}'" \
      --output "reports/annual_report_${lang}.pdf"
done
```

### Quality Assurance Pipeline

**Scenario:** Validate changes before publishing.

```bash
#!/bin/bash
# qa_pipeline.sh

# Generate with low quality for review
nano-pdf edit presentation.pdf 1 "Update title" \
  --resolution "1K" \
  --output "review_draft.pdf"

# Manual review
echo "Review draft? (y/n)"
read approve

if [ "$approve" = "y" ]; then
    # Generate high quality final
    nano-pdf edit presentation.pdf 1 "Update title" \
      --resolution "4K" \
      --output "final_presentation.pdf"
    echo "Final version created!"
fi
```

### A/B Testing Variations

**Scenario:** Create multiple design variants.

```bash
#!/bin/bash
# create_variants.sh

# Variant A: Blue theme
nano-pdf edit landing_page.pdf 1 \
  "Change background to blue (#0066CC)" \
  --output "variant_a_blue.pdf"

# Variant B: Green theme
nano-pdf edit landing_page.pdf 1 \
  "Change background to green (#00AA66)" \
  --output "variant_b_green.pdf"

# Variant C: Gradient
nano-pdf edit landing_page.pdf 1 \
  "Change background to blue-to-purple gradient" \
  --output "variant_c_gradient.pdf"
```

### Scheduled Updates

**Scenario:** Cron job for daily updates.

```bash
# crontab entry: Run daily at 6 AM
# 0 6 * * * /path/to/daily_update.sh

#!/bin/bash
# daily_update.sh

TODAY=$(date +"%B %d, %Y")

nano-pdf edit daily_report.pdf 1 \
  "Update date to '$TODAY' and change status to 'Current'" \
  --output "reports/report_$(date +%Y%m%d).pdf"
```

## Tips for Better Results

### Start with Low Resolution

Test your prompts with 1K or 2K before committing to 4K:

```bash
# Test phase
nano-pdf edit test.pdf 1 "Try this change" --resolution "1K"

# If it works, run with high quality
nano-pdf edit test.pdf 1 "Try this change" --resolution "4K"
```

### Use Style References Consistently

Always reference the same pages for consistent styling:

```bash
# Set your style reference pages once
STYLE_REFS="1,2"

# Use for all operations
nano-pdf edit deck.pdf 5 "Update slide" --style-refs "$STYLE_REFS"
nano-pdf add deck.pdf 5 "Add slide" --style-refs "$STYLE_REFS"
```

### Combine Context and Style

For best results, use both:

```bash
nano-pdf add report.pdf 10 \
  "Create conclusion slide summarizing key findings" \
  --use-context \
  --style-refs "1,2,3"
```

### Be Specific in Prompts

Better prompts = better results:

```bash
# Vague
nano-pdf edit deck.pdf 1 "Make it look better"

# Specific
nano-pdf edit deck.pdf 1 "Increase title font size to 48pt, change color to navy blue (#001F3F), and add 20px padding"
```

## More Resources

- [User Guide](USER_GUIDE.md) - Complete beginner's guide
- [API Reference](API_REFERENCE.md) - All commands and options
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues
- [GitHub Repository](https://github.com/gavrielc/Nano-PDF) - Source code and issues
