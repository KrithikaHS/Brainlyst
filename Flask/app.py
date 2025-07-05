from flask import Flask, render_template, request, send_from_directory
import os
from utils import predict_tumor, generate_pdf_report,is_brain_mri
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
REPORT_FOLDER = os.path.join('static', 'reports')

@app.route('/')
def index():
    # This will render your index.html (landing page)
    return render_template('index.html')

@app.route('/Signin')
def Signin():
    # This will render your index.html (landing page)
    return render_template('Signin.html')

@app.route('/about')
def about():
    # This will render your index.html (landing page)
    return render_template('about.html')

@app.route('/learn')
def learn():
    # This will render your index.html (landing page)
    return render_template('learn.html')

@app.route('/upload', methods=['GET', 'POST'])  # Allow both GET and POST methods
def upload():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("images")
        results = []

        # Ensure the upload folder exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        for file in uploaded_files:
            if file.filename:
                filename = secure_filename(file.filename)  # Sanitize the filename
                filepath = os.path.join(UPLOAD_FOLDER, filename)  # Join paths correctly
                file.save(filepath)

                if not is_brain_mri(filepath):
                    results.append({
                "filename": filename,
                "image_url": f"/{filepath}",
                "result": "Invalid Image",
                "confidence": "N/A",
                "report_path": None,
                "error": "Not a valid brain MRI. Please upload a proper scan."
                })
                    continue
                

                result, confidence = predict_tumor(filepath)
                report_filename = generate_pdf_report(result, confidence, filepath)
                
                results.append({
                    "filename": filename,
                    "image_url": f"/{filepath}",
                    "result": result,
                    "confidence": f"{confidence * 100:.2f}%",
                    "report_path": report_filename
                })

        tumor_info = {
            "Glioma": {"desc": "Gliomas start in the glial cells.", "treatment": "Radiation, chemo."},
            "Meningioma": {"desc": "Grow from meninges layers.", "treatment": "Surgery, radiation."},
            "No Tumor": {"desc": "Normal scan.", "treatment": "No treatment needed."},
            "Pituitary": {"desc": "Found in pituitary gland.", "treatment": "Surgery, hormone meds."}
        }

        return render_template('upload.html', results=results, tumor_info=tumor_info)

    # For GET requests, render the upload page
    return render_template('upload.html')

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(REPORT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
