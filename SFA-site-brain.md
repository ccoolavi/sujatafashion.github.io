# SFA-Project-Brain

## Project Context
- **Name:** Sujata Fashion (SFA)
- **Directory:** `/home/ubuntu/sujata-fashion-test-stylist/`
- **Primary Repo:** `git@github.com:ccoolavi/sujatafashion.github.io.git`
- **Secondary/Backup Repo:** `git@github.com:ccoolavi/sfa-phase6.git`
- **Auth:** SSH-based deployment.

## Technical Architecture
- **Data Source:** Public CSV export links (Sales, Rent, Testimonials), bypassing Google Sheets API.
- **Logic Location:** Inline `<script>` block within `index.html` (lines 1575+). 
- **Dependencies:** None (self-contained, no external JS dependencies currently in use).

## Workflow Instructions
- **Branch Management:** Use `git fetch --all` to sync; feature branches include `I1site`, `feature/academy`, `feature/phase6`, `feature/product-pages`.
- **Deployment:** Push to `main` branch of `sfa-phase6` using force push if history diverges.
- **Rules:** Never use API keys, always prefer public CSV exports. Always inspect inline JS in `index.html` before modifying external files.
