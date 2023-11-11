from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import subprocess
from werkzeug.utils import secure_filename
import joblib
import pandas as pd

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FASTQC = 'outputs/output_fastqc'
OUTPUT_VELVET = 'outputs/output_velvet'
OUTPUT_PRODIGAL = 'outputs/output_prodigal'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['ALLOWED_EXTENSIONS'] = {'faa', 'fasta', 'Fasta', 'csv'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maximum upload file size (16MB)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if not os.path.exists(OUTPUT_PRODIGAL):
    os.makedirs(OUTPUT_PRODIGAL)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(OUTPUT_FASTQC):
    os.makedirs(OUTPUT_FASTQC)

if not os.path.exists(OUTPUT_VELVET):
    os.makedirs(OUTPUT_VELVET)

ALLOWED_EXTENSIONS = {'fastq', 'gz', 'fa'}

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/check_quality', methods=['GET', 'POST'])
def check_quality():
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)
    
    cmd = ['fastqc', filename, '-o', OUTPUT_FASTQC]
    subprocess.run(cmd)

    html_report = file.filename.replace('.fastq.gz', '_fastqc.html')
    zip_report = file.filename.replace('.fastq.gz', '_fastqc.zip')

    return render_template('quality_check.html', uploaded=True, html_report=html_report, zip_report=zip_report)

@app.route('/genome_assembly', methods=['GET', 'POST'])
def genome_assembly():
    feedback = None
    contigs = None
    stats = None
    proteins = None

    if 'assemble_genome' in request.form:
        files = request.files.getlist('file')

        if len(files) != 2:
            feedback = "Please upload exactly two files for paired-end reads."
            return render_template('genome_assembly.html', feedback=feedback)

        file_paths = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                file_paths.append(filepath)

        hash_length = 31
        cmd_velveth = f"velveth {OUTPUT_VELVET} {hash_length} -shortPaired -separate -fastq {' '.join(file_paths)}"
        cmd_velvetg = f"velvetg {OUTPUT_VELVET}"

        os.system(cmd_velveth)
        os.system(cmd_velvetg)

        if os.path.exists(os.path.join(OUTPUT_VELVET, 'contigs.fa')):
            contigs = 'contigs.fa'
        if os.path.exists(os.path.join(OUTPUT_VELVET, 'stats.txt')):
            stats = 'stats.txt'

        feedback = "Upload and assembly successful!"

    elif 'gene_prediction' in request.form:
        contigs_path = os.path.join(OUTPUT_VELVET, 'contigs.fa')
        if os.path.exists(contigs_path):
            output_protein_path = os.path.join(OUTPUT_PRODIGAL, "out.faa")
            cmd_prodigal = f"prodigal -i {contigs_path} -p normal -q -a {output_protein_path}"
            os.system(cmd_prodigal)
            proteins = "out.faa"
            feedback = "Gene prediction was successful!"

    return render_template('genome_assembly.html', feedback=feedback, contigs=contigs, stats=stats, proteins=proteins)

@app.route('/outputs/<path:subdir>/<filename>')
def output_files(subdir, filename):
    return send_from_directory(os.path.join('outputs', subdir), filename, as_attachment=False)

@app.route('/gene_prediction', methods=['GET', 'POST'])
def gene_prediction():
    feedback = None
    protein_file = None

    if request.args.get('from_assembly') == 'true':
        contigs_path = os.path.join(OUTPUT_VELVET, 'contigs.fa')
        if os.path.exists(contigs_path):
            output_path = os.path.join(OUTPUT_PRODIGAL, 'out.faa')
            cmd = ['prodigal', '-i', contigs_path, '-p', 'normal', '-q', '-a', output_path]
            subprocess.run(cmd)
            feedback = "Gene prediction was successful!"
            protein_file = 'out.faa'
        else:
            feedback = "contigs.fa file not found. Please run the genomic assembly first."

    elif 'file' in request.files:
        uploaded_file = request.files['file']
        
        if uploaded_file.filename == '':
            feedback = "No file selected."
        elif uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(filepath)
            output_path = os.path.join(OUTPUT_PRODIGAL, 'out.faa')
            cmd = ['prodigal', '-i', filepath, '-p', 'normal', '-q', '-a', output_path]
            subprocess.run(cmd)
            feedback = "Gene prediction was successful!"
            protein_file = 'out.faa'
        else:
            feedback = "Invalid file type. Please upload a .fa file."

    return render_template('gene_prediction.html', feedback=feedback, protein_file=protein_file)



@app.route('/predict', methods=['GET', 'POST'])
def predict():
    file_path = request.form['file_path']

    model_path = 'path/to/your/model.pkl'
    model = joblib.load(model_path)

    vectorizer_path = 'path/to/your/vectorizer.pkl'
    vectorizer = joblib.load(vectorizer_path)

    data = pd.read_csv(file_path)
    sequences = data['Protein Sequence'].tolist()
    X_test = vectorizer.transform(sequences)
    predictions = model.predict(X_test)

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
    data['Predicted Label'] = predicted_labels

    return render_template('results.html', data=data.to_html(index=False))

@app.route('/ml_preprocessing')
def ml_preprocessing():
    return render_template('placeholder.html', title="Machine Learning Preprocessing", message="Machine Learning Preprocessing functionality will be available soon.")

@app.route('/ml_classification')
def ml_classification():
    return render_template('placeholder.html', title="Machine Learning Classification", message="Machine Learning Classification functionality will be available soon.")

if __name__ == "__main__":
    app.run(debug=True)