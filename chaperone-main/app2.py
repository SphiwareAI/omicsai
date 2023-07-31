import os
import pandas as pd
from flask import Flask, render_template, request, flash
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'faa', 'fasta', 'Fasta', 'csv'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maximum upload file size (16MB)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_sequences(sequences):
    # Preprocess the sequences if needed
    # For enzyme sequences, you can apply any specific preprocessing steps here.
    return sequences

def fit_model(vectorizer, sequences):
    # Load the already trained model
    model_path = 'path_to_your_trained_model.pkl'
    model = joblib.load(model_path)

    # Transform the sequences using the vectorizer
    X_test = vectorizer.transform(sequences)

    # Get the predictions
    predictions = model.predict(X_test)

    # Map class labels to their respective names (if needed)
    class_mapping = {
        0: 'ligases',
        1: 'lyases',
        2: 'hydrolases',
        3: 'isomerase',
        4: 'translocase',
        5: 'transferases',
        6: 'non enzyme',
        7: 'oxidoreductase'
    }

    predicted_labels = [class_mapping[label] for label in predictions]

    return predicted_labels

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')

        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', error='No selected file')

        if file and allowed_file(file.filename):
            # Save the uploaded file to the UPLOAD_FOLDER
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            return render_template('index2.html', file_path=file_path)

        else:
            return render_template('index.html', error='Invalid file type')

    return render_template('index.html')

@app.route('/index2', methods=['POST'])
def upload_vectorizer():
    # Get the file_path from the form data
    file_path = request.form['file_path']

    # Check if the post request has the vectorizer file part
    if 'vectorizer' not in request.files:
        return render_template('index2.html', file_path=file_path, error='No vectorizer file part')

    vectorizer_file = request.files['vectorizer']

    if vectorizer_file.filename == '':
        return render_template('index2.html', file_path=file_path, error='No selected vectorizer file')

    if vectorizer_file and allowed_file(vectorizer_file.filename):
        # Save the uploaded vectorizer to the UPLOAD_FOLDER
        vectorizer_path = os.path.join(app.config['UPLOAD_FOLDER'], vectorizer_file.filename)
        vectorizer_file.save(vectorizer_path)

        # Load the vectorizer
        vectorizer = joblib.load(vectorizer_path)

        # Read and preprocess the sequences
        data = pd.read_csv(file_path)
        sequences = data['Protein Sequence'].tolist()
        preprocessed_sequences = preprocess_sequences(sequences)

        # Get the predictions
        predicted_labels = fit_model(vectorizer, preprocessed_sequences)

        # Combine the sequences with the predictions
        data['Predicted Label'] = predicted_labels

        # Set the file_uploaded variable to True to show the success message in the HTML
        file_uploaded = True

        return render_template('index2.html', file_path=file_path, file_uploaded=file_uploaded)

    else:
        return render_template('index2.html', file_path=file_path, error='Invalid vectorizer file type')

@app.route('/predict', methods=['POST'])
def predict():
    # Get the file_path from the form data
    file_path = request.form['file_path']

    # Load the already trained model
    model_path = 'path_to_your_trained_model.pkl'
    model = joblib.load(model_path)

    # Load the vectorizer used during training
    vectorizer_path = 'path_to_your_tfidf_vectorizer.pkl'
    vectorizer = joblib.load(vectorizer_path)

    # Read and preprocess the sequences
    data = pd.read_csv(file_path)
    sequences = data['Protein Sequence'].tolist()
    preprocessed_sequences = preprocess_sequences(sequences)

    # Transform the sequences using the vectorizer
    X_test = vectorizer.transform(preprocessed_sequences)

    # Get the predictions
    predictions = model.predict(X_test)

    # Map class labels to their respective names (if needed)
    class_mapping = {
        0: 'ligases',
        1: 'lyases',
        2: 'hydrolases',
        3: 'isomerase',
        4: 'translocase',
        5: 'transferases',
        6: 'non enzyme',
        7: 'oxidoreductase'
    }

    predicted_labels = [class_mapping[label] for label in predictions]

    # Combine the sequences with the predictions
    data['Predicted Label'] = predicted_labels

    return render_template('results.html', data=data.to_html(index=False))

if __name__ == '__main__':
    app.run(debug=True)