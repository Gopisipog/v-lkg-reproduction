p = r'D:\v_lkg_reproduction\app.py'
lines = open(p, encoding='utf-8').read().split('\n')

tabs = [
    'with tab_proactive:',
    'with tab_perspectives:',
    'with tab_interview:',
    'with tab_learning:',
    'with tab_competitive:',
    'with tab_sales:',
    'with tab_compliance:',
    'with tab_rd:',
    'with tab_customer:',
    'with tab_executive:',
    'with tab_orgknow:',
    'with tab_thought:',
]

out = []
for ln in lines:
    out.append(ln)
    s = ln.rstrip('\n')
    if s.strip() in tabs and s.rstrip().endswith(':'):
        base = len(s) - len(s.lstrip())   # indent of the with line
        child = ' ' * (base + 4)
        out.append(child + 'render_knowledge_layer(exclude_types=["IntelligenceDomain"])')

open(p, 'w', encoding='utf-8').write('\n'.join(out))
print('done')
