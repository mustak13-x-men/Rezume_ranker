from flask import Flask, request, render_template, jsonify, redirect, url_for
import os
from utils import parser, analyzer, scorer
from utils import dataset
from auth import auth_bp, login_manager, SessionLocal, UserModel
from flask_login import login_required, current_user
from models import Base
from sqlalchemy import create_engine
from paths import (
    DB_PATH,
    DATA_DIR,
    FRONTEND_STATIC_DIR,
    FRONTEND_TEMPLATES_DIR,
    RESUME_CSV_PATH,
    STORED_RESUMES_DIR,
    UPLOADS_DIR,
)

app = Flask(
    __name__,
    template_folder=str(FRONTEND_TEMPLATES_DIR),
    static_folder=str(FRONTEND_STATIC_DIR),
)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
app.secret_key = 'replace-this-with-a-secure-key'
DATA_DIR.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH.as_posix()}")
Base.metadata.create_all(engine)
app.register_blueprint(auth_bp)
login_manager.init_app(app)

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOADS_DIR)

def process_resume_file(file_path):
    if file_path.lower().endswith('.pdf'):
        text = parser.extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        text = parser.extract_text_from_docx(file_path)
    else:
        text = ''
    return text


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/dataset', methods=['GET'])
@login_required
def dataset_view():
    """Return a JSON analysis of the first few resumes in the dataset."""
    csv_path = str(RESUME_CSV_PATH)
    try:
        results = dataset.analyze_dataset(csv_path, top_n=5)
        return jsonify(results)
    except FileNotFoundError:
        return jsonify({'error': 'Dataset file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/browse', methods=['GET'])
@login_required
def browse():
    """Render a page allowing the user to filter and view dataset entries."""
    csv_path = str(RESUME_CSV_PATH)
    df = dataset.load_resume_csv(csv_path)
    category = request.args.get('category', '')
    if category:
        df = df[df['Category'].str.contains(category, case=False, na=False)]
    table_html = df.head(50).to_html(classes='browse-table', index=False)
    return render_template('browse.html', table=table_html)


@app.route('/rank', methods=['GET','POST'])
@login_required
def rank_view():
    """Allow posting a job description and return top matching resumes."""
    results = None
    if request.method == 'POST':
        jd = request.form.get('job_description', '')
        csv_path = str(RESUME_CSV_PATH)
        df = dataset.rank_resumes_against_jd(csv_path, jd, top_n=10)
        results = df.to_html(classes='browse-table', index=False)
    return render_template('rank.html', results=results)


@app.route('/history')
@login_required
def history():
    """Show past analyses for the current user."""
    from models import Analysis
    session = SessionLocal()
    entries = session.query(Analysis).filter(Analysis.user_id == current_user.id).order_by(Analysis.created_at.desc()).all()
    session.close()
    return render_template('history.html', entries=entries)


@app.route('/analyze', methods=['POST'])
def analyze():
    resume_file = request.files.get('resume')
    job_description = request.form.get('job_description', '')
    result = {}

    if not resume_file:
        return jsonify({'error': 'No resume file uploaded'}), 400
    filename = resume_file.filename
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    resume_file.save(save_path)
    if current_user.is_authenticated:
        user_folder = STORED_RESUMES_DIR / str(current_user.id)
        user_folder.mkdir(parents=True, exist_ok=True)
        user_path = user_folder / filename
        resume_file.stream.seek(0)
        resume_file.save(str(user_path))

    resume_text = process_resume_file(save_path)
    resume_text = analyzer.preprocess_text(resume_text)
    result['resume_errors'] = analyzer.detect_errors(resume_text)
    
    # Get comprehensive quality metrics
    quality_metrics = analyzer.get_resume_quality_metrics(resume_text, job_description)
    result['quality_metrics'] = quality_metrics
    result['resume_grade'] = quality_metrics['grade']
    result['quality_score'] = quality_metrics['quality_score']
    
    # Get ATS optimization report
    ats_report = analyzer.get_ats_optimization_report(resume_text, job_description)
    result['ats_optimization_report'] = ats_report
    
    if job_description.strip():
        jd_text = analyzer.preprocess_text(job_description)
        result['skill_match'] = analyzer.calculate_skill_match(resume_text, jd_text)
        result['missing_keywords'] = analyzer.find_missing_keywords(resume_text, jd_text)
        result['similarity'] = scorer.calculate_similarity(resume_text, jd_text) * 100
        result['job_suitability_score'] = round(result['similarity'], 2)
        result['ats_score'] = analyzer.compute_ats_score(resume_text, jd_text)
        result['suggested_improvements'] = analyzer.suggest_improvements(resume_text)
        result['career_advice'] = analyzer.career_advice(resume_text)
    else:
        roles = analyzer.best_suited_roles(resume_text)
        result['best_suited_roles'] = roles
        result['job_suggestions'] = analyzer.suggest_jobs(roles)
        result['ats_score'] = analyzer.compute_ats_score(resume_text)
        result['suggested_improvements'] = analyzer.suggest_improvements(resume_text)
        result['career_advice'] = analyzer.career_advice(resume_text)
    if current_user.is_authenticated:
        from models import Analysis
        session = SessionLocal()
        entry = Analysis(
            user_id=current_user.id,
            resume_text=resume_text,
            job_description=job_description or None,
            ats_score=result.get('ats_score') or 0.0,
            similarity=result.get('similarity') or 0.0
        )
        session.add(entry)
        session.commit()
        session.close()
    try:
        os.remove(save_path)
    except Exception:
        pass

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
