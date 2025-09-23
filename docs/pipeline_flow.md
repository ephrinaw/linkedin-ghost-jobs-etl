# ETL Pipeline Flow

## 1. Extraction Phase

- **Input**: Configuration parameters (search terms, companies, etc.)
- **Process**:
  - Scrape LinkedIn job search results
  - Fetch from ATS APIs (Greenhouse, Lever)
  - Fetch from Adzuna API
- **Output**: Raw JSON files in data/raw/

## 2. Transformation Phase

- **Input**: Raw job data from extraction phase
- **Process**:
  - Clean and standardize data
  - Calculate features (days since posted, word count, etc.)
  - Apply ghost job detection rules
  - Validate data quality
- **Output**: Transformed JSON files in data/transformed/

## 3. Loading Phase

- **Input**: Transformed job data
- **Process**:
  - Connect to PostgreSQL database
  - Load data into job_postings table
  - Handle duplicates and conflicts
- **Output**: Data in database table

## 4. Monitoring and Validation

- Data quality checks at each stage
- Logging of operations and errors
- Validation reports saved to files
