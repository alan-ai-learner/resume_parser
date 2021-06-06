import torch
import numpy as np
from pdfminer.high_level import extract_text


def preprocess_data(data):
    text = extract_text(data)
    text = text.replace("\n", " ")
    text = text.replace("\f", " ")
    return text


def tokenize_resume(text, tokenizer, max_len):
    tok = tokenizer.encode_plus(
        text, max_length=max_len, return_offsets_mapping=True)

    curr_sent = dict()

    padding_length = max_len - len(tok['input_ids'])

    curr_sent['input_ids'] = tok['input_ids'] + ([0] * padding_length)
    curr_sent['token_type_ids'] = tok['token_type_ids'] + \
        ([0] * padding_length)
    curr_sent['attention_mask'] = tok['attention_mask'] + \
        ([0] * padding_length)

    final_data = {
        'input_ids': torch.tensor(curr_sent['input_ids'], dtype=torch.long),
        'token_type_ids': torch.tensor(curr_sent['token_type_ids'], dtype=torch.long),
        'attention_mask': torch.tensor(curr_sent['attention_mask'], dtype=torch.long),
        'offset_mapping': tok['offset_mapping']
    }

    return final_data,curr_sent


tags_vals =['company_worked_at', 'designation', 'company_worked_at_yr', 'degree',\
            'school_college', 'skills', 'location', 'name', 'stream',\
            'roles_responsibilities', 'professional_summary', 'phone', 'email',\
            'Graduation Year', 'email ', 'dob', 'percentage', 'achievements',\
            'Years of Experience', 'higest_degree', 'UNKNOWN']

idx2tag = {i: t for i, t in enumerate(tags_vals)}

resticted_lables = ["UNKNOWN", "O",'percentage', 'achievements','dob',\
                      'Years of Experience', 'higest_degree', 'email ','location']

def predict(model, tokenizer, idx2tag, device, test_resume, max_len):
    model.eval() 
    data,curr_sent = tokenize_resume(test_resume, tokenizer, max_len)
    # print(data)
    input_ids, input_mask = data['input_ids'].unsqueeze(
        0), data['attention_mask'].unsqueeze(0)
    labels = torch.tensor([1] * input_ids.size(0),
                          dtype=torch.long).unsqueeze(0)
    with torch.no_grad():
        outputs = model(
            input_ids,
            token_type_ids=None,
            attention_mask=input_mask,
            labels=labels,
        )
        tmp_eval_loss, logits = outputs[:2]

    logits = logits.cpu().detach().numpy()
    label_ids = np.argmax(logits, axis=2)

    entities = []
    for label_id, offset in zip(label_ids[0], data['offset_mapping']):
        curr_id = idx2tag[label_id]
        curr_start = offset[0]
        curr_end = offset[1]
        # print(f'curr_id:{curr_id} \n curr_start:{curr_start} \n curr_end{curr_end}',)
        if curr_id not in resticted_lables:
            if len(entities) > 0 and entities[-1]['entity'] == curr_id and curr_start - entities[-1]['end'] in [0, 1]:
                entities[-1]['end'] = curr_end
            else:
                entities.append(
                    {'entity': curr_id, 'start': curr_start, 'end': curr_end})
    for ent in entities:
        ent['text'] = test_resume[ent['start']:ent['end']]
    return entities
