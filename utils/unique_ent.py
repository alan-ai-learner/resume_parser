def unique_ent(data):
  entities = [] 
  for i in data:
    entities.append(i['entity'])
  summary = {el:[] for el in entities}
  for i in data:
    summary[i['entity']].append(''.join(i['text']))
  for i in list(summary.keys()):
    if i == 'name':
      summary[i] = ''.join(summary[i][:3])
    elif i in ['designation', 'company_worked_at','company_worked_at_yr']:
      summary[i] = ', '.join(summary[i])
    else:
      summary[i] = ' '.join(summary[i])
  return summary