# Database Schema

## Table: job_postings

| Column                 | Type                     | Description                                        |
| ---------------------- | ------------------------ | -------------------------------------------------- |
| job_id                 | VARCHAR(255) PRIMARY KEY | Unique job identifier                              |
| source                 | VARCHAR(100)             | Data source (linkedin, greenhouse, lever, adzuna)  |
| source_company         | VARCHAR(255)             | Company name as used in source API                 |
| title                  | VARCHAR(255)             | Job title                                          |
| company                | VARCHAR(255)             | Company name                                       |
| location               | VARCHAR(255)             | Job location                                       |
| location_type          | VARCHAR(50)              | Type of location (remote, hybrid, onsite, unknown) |
| posted_date            | DATE                     | Date job was posted                                |
| created_at             | DATETIME                 | When job was created (from ATS)                    |
| updated_at             | DATETIME                 | When job was last updated (from ATS)               |
| extracted_at           | DATETIME                 | When job was extracted by our system               |
| description            | TEXT                     | Job description                                    |
| job_url                | TEXT                     | URL to job posting                                 |
| is_ghost_job           | BOOLEAN                  | Whether job is flagged as ghost job                |
| ghost_job_reason       | TEXT                     | Reason for ghost job flag                          |
| ghost_score            | INTEGER                  | Ghost job detection score (0-165)                 |
| confidence             | VARCHAR(20)              | Confidence level (Very Low to Very High)          |
| days_since_posted      | INTEGER                  | Days since job was posted                          |
| description_word_count | INTEGER                  | Number of words in description                     |
| keyword_count          | INTEGER                  | Number of technical keywords found                 |
| detected_keywords      | VARCHAR(1000)            | JSON string of detected keywords                   |
| posts_per_week         | FLOAT                    | Company posting frequency                          |
| is_repost              | INTEGER                  | Whether job is a repost (0/1)                     |
| posting_velocity       | FLOAT                    | Company posting velocity                           |
| metadata               | JSON                     | Additional metadata from source                    |
| active                 | BOOLEAN                  | Whether job is active (from ATS)                   |

## Implementation Notes

### SQLite Specific
- JSON columns stored as TEXT with JSON validation
- BOOLEAN columns stored as INTEGER (0/1)
- DATETIME columns stored as TEXT in ISO format

### Data Types
- All VARCHAR fields have specified lengths for compatibility
- TEXT fields for unlimited length content
- INTEGER for numeric values and flags
- FLOAT for decimal calculations

## Indexes

```sql
CREATE INDEX idx_job_postings_company ON job_postings(company);
CREATE INDEX idx_job_postings_ghost_jobs ON job_postings(is_ghost_job);
CREATE INDEX idx_job_postings_posted_date ON job_postings(posted_date);
CREATE INDEX idx_job_postings_source ON job_postings(source);
CREATE INDEX idx_job_postings_ghost_score ON job_postings(ghost_score);
```

## Sample Data

```json
{
  "job_id": "linkedin_12345",
  "source": "linkedin",
  "title": "Senior Data Scientist",
  "company": "Tech Corp",
  "location": "Helsinki, Finland",
  "location_type": "hybrid",
  "posted_date": "2024-01-15",
  "description": "We are looking for an experienced data scientist...",
  "is_ghost_job": false,
  "ghost_score": 25,
  "confidence": "Low",
  "days_since_posted": 5,
  "description_word_count": 150,
  "keyword_count": 8,
  "detected_keywords": "[\"python\", \"sql\", \"machine learning\", \"aws\"]"
}
```