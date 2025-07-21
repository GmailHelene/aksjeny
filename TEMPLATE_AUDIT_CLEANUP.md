# Template Audit & Cleanup Plan

## Current Template Issues to Address:

### Duplicates to Resolve:
1. **stocks/detail.html vs stocks/details.html** - Keep detail.html, remove details.html
2. **warren_buffet.html vs warren-buffet.html** - Standardize to warren_buffett.html
3. **Multiple similar analysis templates** - Consolidate

### Missing Templates (Need to Create):
- templates/analysis/fundamental.html
- templates/analysis/ai_form.html
- templates/analysis/screener.html (if not exists)
- templates/portfolio/create.html
- templates/portfolio/view.html
- templates/portfolio/watchlist.html

### Templates to Move/Reorganize:
- Move technical.html to analysis/technical.html if misplaced
- Ensure profile.html is in root templates/
- Check features.html location

### Templates to Fix/Update:
- All analysis templates showing random tokens
- Portfolio templates with proper error handling
- Market overview templates

## Action Plan:
1. Audit existing template structure
2. Remove duplicates
3. Fix broken templates
4. Create missing templates
5. Update routes to use correct templates
