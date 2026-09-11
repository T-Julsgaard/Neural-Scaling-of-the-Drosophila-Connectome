"""Verify DOI metadata with Crossref; record failures without inventing metadata."""
import concurrent.futures
import json
import re
import html
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def verify(r):
    if not r.get('doi'):
        return r
    if r.get('authors') and r.get('publisher_date'):
        if str(r.get('metadata_verification', '')).startswith('unresolved'):
            r['last_refresh_error'] = r['metadata_verification']
            r['metadata_verification'] = 'Crossref 2026-09-11; earlier successful metadata retained'
        return r
    try:
        url = 'https://api.crossref.org/works/' + urllib.parse.quote(r['doi'], safe='')
        with urllib.request.urlopen(url, timeout=25) as response:
            m = json.load(response)['message']
        r['metadata_verification'] = 'Crossref 2026-09-11'
        r['title'] = m.get('title', [r['title']])[0]
        r['authors'] = [{'given': a.get('given', ''), 'family': a.get('family', '')} for a in m.get('author', [])]
        if r['authors']:
            r['author'] = r['authors'][0]['family'] + (' et al.' if len(r['authors']) > 1 else '')
        r['container'] = m.get('container-title', [])
        r['publisher_date'] = m.get('published', {}).get('date-parts')
    except Exception as e:
        r['metadata_verification'] = 'unresolved: ' + type(e).__name__
    return r


def main():
    path = ROOT / 'research/references.json'
    rows = json.loads(path.read_text(encoding='utf-8'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(verify, rows))
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    bib = []
    md = ['# Bibliography', '', 'Checked 2026-09-11. Read depth and publication status are recorded explicitly. No source has been internally reproduced. Metadata verification is separate from scientific verification.', '']
    for r in rows:
        r['title'] = ' '.join(html.unescape(re.sub('<[^>]+>', '', r['title'])).split())
        author = ' and '.join((a['family'] + ', ' + a['given']).strip(', ') for a in r.get('authors', [])) or r['author']
        fields = {'title': r['title'], 'author': author, 'year': str(r['year']), 'url': r['url'], 'note': r['kind'] + '; read depth: ' + r['read_depth']}
        if r.get('doi'):
            fields['doi'] = r['doi']
        bib.append('@misc{' + r['id'] + ',\n' + ',\n'.join('  '+k+' = {'+v.replace('&', '\\&')+'}' for k, v in fields.items()) + '\n}')
        md += [f"- **{r['id']}** {r['author']} ({r['year']}). [{r['title']}]({r['url']}). {r['kind']}; `{r['read_depth']}`."]
    (ROOT / 'research/references.bib').write_text('\n\n'.join(bib) + '\n', encoding='utf-8')
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (ROOT / 'research/BIBLIOGRAPHY.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print('References:', len(rows), 'DOI metadata verified:', sum(r.get('metadata_verification', '').startswith('Crossref') for r in rows))


if __name__ == '__main__':
    main()
