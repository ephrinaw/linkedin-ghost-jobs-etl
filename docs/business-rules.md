# Ghost Job Detection Business Rules

## Definition of a Ghost Job

A "ghost job" is a job posting that remains published for an extended period without the company having a real intention to fill the position.

## Detection Algorithm

The system uses a weighted scoring approach with 10 detection rules. Jobs scoring ≥40 points (out of 165 possible) are classified as ghost jobs.

## Detection Rules

### 1. Job Age Analysis (30 points)
- **Rule**: Flag jobs older than 45 days
- **Rationale**: Most genuine job postings are filled within 30-45 days
- **Implementation**: Calculate days between current date and posted_date

### 2. Description Quality (20 points)
- **Rule**: Flag jobs with descriptions shorter than 30 words
- **Rationale**: Legitimate job postings typically have detailed descriptions
- **Implementation**: Count words in description field

### 3. Suspicious Company Patterns (25 points)
- **Rule**: Flag jobs from staffing agencies or generic company names
- **Patterns**: "staffing", "recruitment", "talent", "consulting", "solutions"
- **Rationale**: Staffing agencies often post ghost jobs for talent pipeline building

### 4. Vague Salary Information (15 points)
- **Rule**: Flag jobs with no specific salary ranges
- **Vague Terms**: "competitive", "negotiable", "commensurate", "DOE"
- **Rationale**: Real jobs typically provide salary transparency

### 5. Red Flag Keywords (15 points)
- **Rule**: Flag jobs with 2+ suspicious keywords
- **Keywords**: "urgently hiring", "immediate start", "no experience required", "easy money"
- **Rationale**: These phrases often indicate low-quality or fake postings

### 6. Few Technical Keywords (10 points)
- **Rule**: Flag jobs with fewer than 2 technical keywords
- **Keywords**: python, sql, java, aws, azure, machine learning, etc.
- **Rationale**: Real technical jobs mention specific technologies

### 7. Generic Job Titles (10 points)
- **Rule**: Flag overly generic titles
- **Examples**: "Software Developer", "Manager", "Consultant"
- **Rationale**: Legitimate jobs have specific, descriptive titles

### 8. Stagnant Postings (20 points)
- **Rule**: Flag jobs not updated in 30+ days despite being old
- **Implementation**: Compare created_at and updated_at fields
- **Rationale**: Active hiring processes involve regular updates

### 9. Vague Location Information (5 points)
- **Rule**: Flag jobs with unclear location details
- **Patterns**: "Remote", "Multiple locations", "Flexible"
- **Rationale**: Real jobs typically specify work location

### 10. Suspicious Posting Patterns (15 points)
- **Rule**: Flag companies with unusual posting behavior
- **Patterns**: High frequency posting, bulk posting, frequent reposts
- **Rationale**: Ghost job companies often post in bulk or repost frequently

## Confidence Levels

- **Very High (70+ points)**: Almost certainly a ghost job
- **High (50-69 points)**: Likely a ghost job
- **Medium (40-49 points)**: Possibly a ghost job (threshold for classification)
- **Low (20-39 points)**: Probably legitimate
- **Very Low (<20 points)**: Likely legitimate

## Data Sources

### Primary Sources

1. **LinkedIn Scraping**: Broad coverage but less reliable data
2. **ATS APIs (Greenhouse, Lever)**: High-quality structured data
3. **Job Aggregators (Adzuna)**: Supplementary data

### Data Quality Rules

1. All jobs must have: job_id, title, job_url
2. job_id must be unique
3. job_url must be a valid URL
4. Dates must be in ISO format or parseable

## Finnish Market Specialization

### Trusted Companies (Lower ghost job probability)
- Nokia, Supercell, Wolt, Rovio, Kone, Fortum, Neste, Elisa, Telia

### Salary Ranges (EUR)
- Junior: €35,000 - €50,000
- Mid-level: €50,000 - €80,000
- Senior: €80,000 - €120,000
- Lead: €100,000 - €150,000

### Finnish Job Boards
- Duunitori.fi, Monster.fi, Oikotie.fi, TE-palvelut.fi