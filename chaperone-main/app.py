import sys
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
from distutils.log import debug
from fileinput import filename
import pandas as pd
from flask import *
import os
from werkzeug.utils import secure_filename
import textwrap
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
 
UPLOAD_FOLDER = os.path.join('static', 'uploads')
 
# Define allowed files
ALLOWED_EXTENSIONS = {'faa'}
 
app = Flask(__name__)
 
# Configure upload file path flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
app.secret_key = 'This is your secret key to utilize session in Flask'
 
 
@app.route('/', methods=['GET', 'POST'])
def uploadFile():
    if request.method == 'POST':
      # upload file flask
        f = request.files.get('file')
 
        # Extracting uploaded file name
        data_filename = secure_filename(f.filename)
 
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                            data_filename))
 
        session['uploaded_data_file_path'] =os.path.join(app.config['UPLOAD_FOLDER'],data_filename)
        #index2 tells the user that the file has been uploaded successfuly 
        return render_template('index2.html')
    return render_template("index.html") #index 1 is the landing page that shows the form and asks user to upload a file
 
 
@app.route('/show_data')
def showData():
    # Uploaded File Path
    data_file_path = session.get('uploaded_data_file_path', None)
    # read .faa
    uploaded_df = open(data_file_path, 'r')
    text = uploaded_df.readlines()
    
    #start the preprocessing of faa file
    for i in text:
        if '>' in i:
            print(text.remove(i))
    
    text=str(text).strip()
    text = text.replace('*','')
    text= text.replace('[','')

    text = text.replace(']','')
    text = text.replace('"','')
    text = text.replace("'",'')
    text = text.replace("\\n",'')
    
    column_names=["sequences"]

    TESTDATA = StringIO(text)

    df = pd.read_csv(TESTDATA, sep=",", header=None)
    df = df.transpose()
    df.columns =['sequences']
    df=df.dropna() #drop rows with NaN
    df['sequences'] = df['sequences'].str.strip() #remove white spaces in df
    #start with sub-wording
    df['words'] =df.apply(lambda x: textwrap.wrap(x['sequences'],3), axis=1)
    df = df.drop('sequences', axis=1)
    
   #convert list to string so that you can remove the symbols in the text
    df['words'] = [','.join(map(str, l)) for l in df['words']]
   #replace commas with space
    df["words"] = df["words"].str.replace('[^\w\s]',' ')
    
    #uploaded_df = df
    
    ##now load the df that the model was trained on for tokenization
    df2 =  pd.read_csv("B1_FINAL_DF.csv")

    X_T = df2.words
    y_T = df2.label

    tfidf = TfidfVectorizer()
    X = tfidf.fit_transform(X_T)
    
    #load model
    model = pickle.load(open("rf_tf_idf_multiclass_SMOTE.sav", "rb"))
    model2 = pickle.load(open("rf_tf_idf_multiclass_SMOTE.sav", "rb"))
    
    #load your processed test data
    X_test = df.words
    
    
    tf_idf_features = tfidf.transform(X_test)
    
    
    #get the preds
    preds = model.predict(tf_idf_features)
    predictions=pd.DataFrame(preds, columns=['predictions'])
    
    preds = pd.concat([df, predictions], axis=1)
    
    preds['predictions'] = preds['predictions'].replace([6.0], 'ligases')
    preds['predictions'] = preds['predictions'].replace([4.0], 'lyases')
    preds['predictions'] = preds['predictions'].replace([3.0], 'hydrolases')
    preds['predictions'] = preds['predictions'].replace([5.0], 'isomerase')
    preds['predictions'] = preds['predictions'].replace([7.0], 'translocase')
    preds['predictions'] = preds['predictions'].replace([2.0], 'transferases')
    preds['predictions'] = preds['predictions'].replace([0.0], 'non enzyme')
    preds['predictions'] = preds['predictions'].replace([1.0], 'oxidoreductase')
    
    preds=preds.dropna() #drop rows with NaN
    preds['words']= preds['words'].str.replace(" ", "")
    #preds['words'] = preds['words'].str.strip() #remove white spaces in df
    
    uploaded_df = preds
    
    # Converting to html Table
    uploaded_df_html = uploaded_df.to_html()
    
    return render_template('show_csv_data.html',
                           data_var=uploaded_df_html)

#####BEGINING OF SINGLE SEQUENCE PREDICTION

@app.route("/")
def Home():

    return render_template("index.html")

@app.route("/predict", methods = ["POST"])
def predict():
    
    
    #get data data entered by the user
    
    my_features = [str(x) for x in request.form.values()]
  
    df2 =  pd.read_csv("B1_FINAL_DF.csv")

    X_T = df2.words
    y_T = df2.label

    tfidf = TfidfVectorizer()
    X = tfidf.fit_transform(X_T)

    model2 = pickle.load(open("rf_tf_idf_multiclass_SMOTE.sav", "rb"))
  

   
    
   # Start the preprocessing
    text = my_features
    text=str(text).strip()
    text = text.replace('*','')
    text= text.replace('[','')

    text = text.replace(']','')
    text = text.replace('"','')
    text = text.replace("'",'')
    text = text.replace("\\n",'')
    
    column_names=["sequences"]

    TESTDATA = StringIO(text)

    df = pd.read_csv(TESTDATA, sep=",", header=None)
    df = df.transpose()
    df.columns =['sequences']
    df=df.dropna() #drop rows with NaN
    df['sequences'] = df['sequences'].str.strip() #remove white spaces in df
    #start with sub-wording
    df['words'] =df.apply(lambda x: textwrap.wrap(x['sequences'],3), axis=1)
    df = df.drop('sequences', axis=1)
    
   #convert list to string so that you can remove the symbols in the text
    df['words'] = [','.join(map(str, l)) for l in df['words']]
   #replace commas with space
    df["words"] = df["words"].str.replace('[^\w\s]',' ')
    X = df.words
    
  
 

 
    
    tf_idf_features = tfidf.transform(X)
    
    #predict and return result in index2.html 
    prediction = model2.predict(tf_idf_features)
    return render_template("index2_s.html", prediction_text = "The prediction on the sequence is {}".format(prediction))

 
 
if __name__ == '__main__':
    app.run(debug=True)