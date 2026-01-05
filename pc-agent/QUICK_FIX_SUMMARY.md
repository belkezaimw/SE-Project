# Quick Fix Summary - PC Build Agent

## 🚨 IMMEDIATE FIXES NEEDED (Application Won't Run)

### 1. Delete/Fix Broken File
**File**: `app/engine/builder.py`
- **Problem**: Imports non-existent `gpu_scraper` module
- **Fix**: Delete this file or remove the broken imports

### 2. Fix Together AI Import
**File**: `app/agent/pc_agent.py` (lines 61-66)
```python
# WRONG:
from langchain_community.llms import Together

# CORRECT (if using langchain-community):
from langchain_community.chat_models import ChatTogether

# OR (if using langchain-together package):
from langchain_together import ChatTogether
```

### 3. Fix Async Cache Decorator
**File**: `app/core/cache.py` (line 102-130)
- **Problem**: `@cached` decorator doesn't work with async functions
- **Fix**: Make it async-compatible or use `functools.wraps` with async support

### 4. Fix Database Query
**File**: `app/api/routes.py` (line 211)
```python
# WRONG:
db.execute("SELECT 1")

# CORRECT:
from sqlalchemy import text
db.execute(text("SELECT 1"))
```

### 5. Fix Deprecated Pydantic Method
**File**: `app/api/routes.py` (line 149)
```python
# WRONG:
ComponentResponse.from_orm(c)

# CORRECT:
ComponentResponse.model_validate(c)
```

### 6. Fix Component Type Validation
**File**: `app/agent/tools.py` (line 37)
```python
# ADD VALIDATION:
from app.db.models import ComponentType
try:
    component_type_enum = ComponentType(component_type)
except ValueError:
    return f"Error: Invalid component type: {component_type}"
```

### 7. Fix Division by Zero
**File**: `app/agent/tools.py` (line 52-53)
```python
# ADD NULL/ZERO CHECKS:
query = query.filter(
    Component.benchmark_score.isnot(None),
    Component.price_dzd > 0
).order_by(
    (Component.benchmark_score / Component.price_dzd).desc()
)
```

### 8. Create .env.example
Create file: `.env.example`
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pc_builds_dz
REDIS_URL=redis://localhost:6379/0
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
TOGETHER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
DEBUG=True
ENVIRONMENT=development
```

## 🔧 CORE FUNCTIONALITY MISSING (App Runs But Doesn't Work Properly)

### 9. Agent Response Parser
**File**: `app/api/routes.py` (line 90-92)
- **Problem**: Agent returns text, but API needs structured `BuildRecommendation`
- **Fix**: Create parser to extract component IDs and build response

### 10. Component Spec Extraction
**Missing**: Logic to extract specs from component names
- Need to parse: socket type, RAM type, TDP, form factor, etc.
- **Location**: Create `app/utils/spec_extractor.py`

### 11. Benchmark Score Calculation
**Missing**: Logic to calculate performance scores
- Components have NULL `benchmark_score`, `gaming_score`, etc.
- **Location**: Create `app/utils/benchmark_calculator.py`

### 12. Ouedkniss Scraper Selectors
**File**: `app/scrapers/ouedkniss_scraper.py` (line 99)
- **Problem**: Placeholder CSS selectors won't work
- **Fix**: Inspect actual Ouedkniss.dz website and update selectors

### 13. Component Name Parsing
**Missing**: Extract manufacturer/model from scraped names
- **Location**: Create `app/utils/name_parser.py`

### 14. Detail Page Scraping
**Missing**: Scrape individual listing pages for full specs
- **Location**: Add method to `OuedknissScraper` class

## 📋 CHECKLIST

- [ ] Fix broken imports in `builder.py`
- [ ] Fix Together AI import
- [ ] Fix async cache decorator
- [ ] Fix database query in health check
- [ ] Fix deprecated `from_orm`
- [ ] Fix component type validation
- [ ] Fix division by zero
- [ ] Create `.env.example`
- [ ] Create Alembic migration
- [ ] Implement agent response parser
- [ ] Implement spec extraction
- [ ] Implement benchmark scoring
- [ ] Update Ouedkniss scraper selectors
- [ ] Add component name parsing
- [ ] Add detail page scraping
- [ ] Add Playwright browser install to Dockerfile
- [ ] Test scraper on actual website
- [ ] Test agent end-to-end

## 🎯 Priority Order

1. **Fix all "IMMEDIATE FIXES"** - App won't run without these
2. **Implement spec extraction** - Without this, compatibility checks fail
3. **Implement benchmark scoring** - Without this, agent can't filter by performance
4. **Fix scraper selectors** - Without this, no data is collected
5. **Implement agent parser** - Without this, API returns invalid format

## 📝 Notes

- The codebase has good structure but many critical pieces are missing
- Most issues are fixable with focused effort
- Start with Phase 1 fixes, then move to core functionality
- Test each component as you fix it

