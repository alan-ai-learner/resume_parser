import argparse
import torch
from transformers import BertTokenizerFast, BertForTokenClassification
from utils.utils import preprocess_data, predict, idx2tag
import json
from flask import Flask, request, render_template
from utils.unique_ent import unique_ent

parser = argparse.ArgumentParser(description='Train Bert-NER')
parser.add_argument('-p', type=str, help='path of trained model state dict')
args = parser.parse_args().__dict__


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


#Model preparation

MAX_LEN = 500
NUM_LABELS = 21
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = 'bert-base-uncased'
STATE_DICT = torch.load('C:/Users/Admin/PycharmProjects/flaskdemo-master/app/best_ner_model_predictor.bin', map_location=DEVICE)
TOKENIZER = BertTokenizerFast.from_pretrained("bert-base-uncased", lowercase=True)

model = BertForTokenClassification.from_pretrained(
    MODEL_PATH, state_dict=STATE_DICT['model_state_dict'], num_labels=NUM_LABELS)
model.to(DEVICE)



@app.route('/') #home page
@app.route('/index')#home page
def index():
    return render_template('home.html')


@app.route('/upload_file', methods = ['GET', 'POST'])
def upload_file():
    print('--upload-file-------------')
    if request.method == 'POST':
        f = request.files['file']
        resume_text = preprocess_data(f)
        entities = []
        length_res = len(resume_text)
        to_iterate = length_res // 500
        if to_iterate <= 1:
          entities.extend(predict(model, TOKENIZER, idx2tag,
                              DEVICE, resume_text, MAX_LEN))
        elif to_iterate > 1:
          j = 0
          for i in range(to_iterate+1):
            if i <= to_iterate + 1:
              entities.extend(predict(model, TOKENIZER, idx2tag,
                                DEVICE, resume_text[j:j+500], MAX_LEN))
              j += 500
            else:
              entities.extend(predict(model, TOKENIZER, idx2tag,
                                DEVICE, resume_text[j:], MAX_LEN))
              
        summary = unique_ent(entities)
        share = {'ent':list(summary.keys()), 'Values':list(summary.values())}
        r=json.dumps(summary)
        loaded_r = json.loads(r)
        return render_template('result.html', data =  loaded_r )


if __name__ == '__main__':
    app.run(debug=True)
