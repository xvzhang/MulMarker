import pandas as pd
import numpy as np
from flask import Flask, render_template, request, session, jsonify
import json
import os
import config

from chatbot import chat
from utils import MulMarker
from resbot import choose_sysmessage

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random session key

system_prompt = config.Qprompt

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404 

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # load files from POST request
        analysis_name = str(request.form['analysisName'])
        chosen_genes_DF = pd.read_csv(request.files['genes_file'], delimiter="\t", names=["gene"])
        clinical_filter_patient = pd.read_csv(request.files['clinical_info_file'], delimiter="\t")
        rna_filter_nor_info = pd.read_csv(request.files['rna_info_file'], delimiter="\t")
        seed = int(request.form.get('seed'))
        ratio = float(request.form.get('ratio'))

        ### Rename the columns
        clinical_filter_patient.columns = ['PATIENT_ID', 'OS_STATUS', 'OS_MONTHS']

        mm_res = MulMarker(analysis_name, chosen_genes_DF, clinical_filter_patient, rna_filter_nor_info, seed, ratio)
    
        ############ Parse parameters ##################
        uni_genes = mm_res['uni_genes']        
        uni_res_html = mm_res['uni_res_html']
        formula = mm_res['formula']
        mul_res_html = mm_res['mul_res_html']
        uni_res_file = mm_res['uni_res_file']
        mul_res_file = mm_res['mul_res_file']
        train_prefix = mm_res['train_prefix']
        test_prefix = mm_res['test_prefix']
        total_prefix = mm_res['total_prefix']
        train_res = mm_res['train_res']
        test_res = mm_res['test_res']
        total_res = mm_res['total_res']

		############ pngs to render upload.html ########
        train_img = train_prefix + ".png"
        test_img = test_prefix + ".png"
        total_img = total_prefix + ".png"

		############ Prepare for downloading files #######
        download_train_img = train_prefix + ".pdf"
        download_test_img = test_prefix + ".pdf"
        download_total_img = total_prefix + ".pdf"

		############# Prompt for GPT (res.html) ######### #############
        bot_prompt = {
                     "candidate_genes": uni_genes,
                     "formula": formula,
                     "train_threshold": train_res["threshold"],
                     "test_threshold": test_res["threshold"],
                     "total_threshold": total_res["threshold"],
                     "train_pVal": train_res["pValue"],
                     "test_pVal": test_res["pValue"],
                     "total_pVal": total_res["pValue"]
                     }         
        botAnswer = choose_sysmessage(bot_prompt)

        return render_template('results.html', 
                       uni_res = uni_res_html, uni_res_file = uni_res_file,
					   risk_formula = formula, mul_res = mul_res_html, 
                       mul_res_file = mul_res_file,
					   train_img=train_img, train_pdf = download_train_img,
					   test_img=test_img, test_pdf = download_test_img,
					   total_img=total_img, total_pdf = download_total_img,
					   report_exp = botAnswer)
 
    return render_template('upload.html')

@app.route("/chat", methods=['GET', 'POST'])
def get_chat_response():

    if request.method == 'POST':
        user_message = request.form.get('message')

        conversation_history = json.loads(session.get('conversation_history', json.dumps([{"role": "system", "content": system_prompt}])))
    
        bot_response = chat(user_message, conversation_history)
    
        # Convert back to string before storing to session
        session['conversation_history'] = json.dumps(conversation_history)
    
        return jsonify(bot_response)

    return render_template('upload.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
