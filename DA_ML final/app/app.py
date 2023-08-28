from flask import Flask, render_template, request
import numpy as np
import tensorflow as tf
from transformers import BertTokenizerFast, TFBertForSequenceClassification
app = Flask(__name__)

PRETRAINED_MODEL = 'bert-base-uncased'
new_tokenizer = BertTokenizerFast.from_pretrained(PRETRAINED_MODEL)
new_model = TFBertForSequenceClassification.from_pretrained(PRETRAINED_MODEL, num_labels=1)
new_model.load_weights("../model_weights.h5")


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        blackmail_newinput = request.form['text_input']
        print("輸入值：" + blackmail_newinput)
        def new_bert_encoder(blackmails_new):
            X_test_tokens = new_tokenizer(blackmails_new, truncation=True, max_length=200, pad_to_max_length=True)
            return X_test_tokens['input_ids'], X_test_tokens['token_type_ids'], X_test_tokens['attention_mask']
        hi = new_bert_encoder(blackmail_newinput)
        bert_newinput = np.array([hi]).squeeze()
        prediction_raw = new_model.predict(bert_newinput)
        a = str(prediction_raw)
        b = []
        for i in a:
            if i in "0123456789.-]":
                b.append(i)

        find_num = [0]
        num_list = []
        for i in range(3):
            find_num.append(int(b.index("]",find_num[-1]+1)))
            del b[find_num[-1]]
            numbers = str("".join(b[find_num[-2]:find_num[-1]]))
            num_list.append(numbers)

        tf_prediction = tf.nn.softmax([[float(num_list[0])],
            [float(num_list[1])],
            [float(num_list[2])]],axis=0).numpy()
        return render_template('index.html', prediction=tf_prediction[0][0]*100, sentence=blackmail_newinput)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)