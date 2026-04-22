import re
import nltk
from nltk.corpus import stopwords
from unidecode import unidecode
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

SKILL_KEYWORDS = [
    'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'html', 'css',
    'react', 'angular', 'vue', 'node', 'django', 'flask', 'sql', 'postgres', 'mysql',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'linux', 'bash',
    'machine learning', 'deep learning', 'data analysis', 'pandas', 'numpy',
    'tensorflow', 'pytorch', 'excel', 'powerpoint', 'word', 'project management',
    'scrum', 'sales', 'customer service', 'marketing', 'seo', 'content',
    'accounting', 'finance', 'human resources', 'hr', 'design', 'graphic design',
    'ux', 'ui', 'teacher', 'nurse', 'doctor', 'chef', 'logistics', 'supply chain',
    'mechanical', 'electrical', 'civil', 'quality assurance', 'testing', 'automation'
]

ROLE_MAP = {
    # Software / Development
    'python': 'Data Scientist / Developer',
    'java': 'Software Engineer',
    'c++': 'Software Engineer',
    'c#': 'Software Engineer',
    'javascript': 'Frontend Developer',
    'typescript': 'Frontend Developer',
    'react': 'Frontend Developer',
    'angular': 'Frontend Developer',
    'vue': 'Frontend Developer',
    'node': 'Backend Developer',
    'django': 'Backend Developer',
    'flask': 'Backend Developer',
    'sql': 'Database Developer / Engineer',
    'postgres': 'Database Developer / Engineer',
    'mysql': 'Database Developer / Engineer',

    # Data / ML
    'machine learning': 'Machine Learning Engineer',
    'deep learning': 'Machine Learning Engineer',
    'pandas': 'Data Analyst',
    'numpy': 'Data Analyst',
    'tensorflow': 'Machine Learning Engineer',
    'pytorch': 'Machine Learning Engineer',

    # Cloud / DevOps / Infra
    'aws': 'Cloud Engineer',
    'azure': 'Cloud Engineer',
    'gcp': 'Cloud Engineer',
    'docker': 'DevOps Engineer',
    'kubernetes': 'DevOps Engineer',
    'git': 'Software Engineer',
    'linux': 'System Administrator',

    # QA / Testing
    'quality assurance': 'QA Engineer',
    'testing': 'QA Engineer',
    'automation': 'Automation Test Engineer',

    # Product / Management / Business
    'project management': 'Project Manager',
    'scrum': 'Scrum Master',
    'business analyst': 'Business Analyst',
    'product manager': 'Product Manager',

    # Sales / Marketing / Support
    'sales': 'Sales Executive',
    'marketing': 'Marketing Manager',
    'seo': 'SEO Specialist',
    'customer service': 'Customer Support',

    # Design / Creative
    'design': 'Graphic / UX Designer',
    'graphic design': 'Graphic Designer',
    'ux': 'UX Designer',
    'ui': 'UI Designer',

    # Finance / HR / Ops
    'excel': 'Business Analyst / Accountant',
    'accounting': 'Accountant',
    'finance': 'Finance Analyst',
    'human resources': 'HR Manager',
    'hr': 'HR Manager',
    'logistics': 'Supply Chain / Logistics Manager',
    'supply chain': 'Supply Chain / Logistics Manager',

    # Non-IT / Trades / Healthcare / Education
    'teacher': 'Teacher / Educator',
    'nurse': 'Nurse / Healthcare',
    'doctor': 'Physician / Healthcare',
    'chef': 'Chef / Culinary',
    'mechanical': 'Mechanical Engineer',
    'electrical': 'Electrical Engineer',
    'civil': 'Civil Engineer',
}


# Industry-specific keywords by role
INDUSTRY_KEYWORDS = {
    'Data Science': {
        'technical': ['python', 'r', 'sql', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 
                     'pytorch', 'spark', 'hadoop', 'tableau', 'power bi', 'jupyter', 'machine learning',
                     'deep learning', 'statistical analysis', 'data mining', 'nlp', 'computer vision'],
        'soft_skills': ['problem solving', 'communication', 'collaboration', 'analytical thinking', 
                       'stakeholder management', 'presentation', 'business acumen'],
        'metrics': ['accuracy', 'precision', 'recall', 'roc-auc', 'model performance', 'data quality',
                   'efficiency gain', 'automation', 'cost reduction', 'roi']
    },
    'Machine Learning': {
        'technical': ['python', 'tensorflow', 'keras', 'pytorch', 'scikit-learn', 'opencv', 'nlp',
                     'deep learning', 'neural networks', 'cnn', 'rnn', 'transformers', 'hugging face',
                     'model deployment', 'mlops', 'docker', 'kubernetes', 'api', 'aws sagemaker'],
        'soft_skills': ['innovation', 'research', 'documentation', 'mentoring', 'agile', 'leadership'],
        'metrics': ['model accuracy', 'inference speed', 'training time', 'optimization', 'scalability']
    },
    'Software Development': {
        'technical': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'react', 'angular',
                     'vue', 'node.js', 'express', 'django', 'flask', 'spring', '.net', 'microservices',
                     'rest api', 'graphql', 'git', 'agile', 'ci/cd', 'testing', 'debugging'],
        'soft_skills': ['teamwork', 'code review', 'documentation', 'mentoring', 'problem-solving'],
        'metrics': ['code quality', 'test coverage', 'performance', 'bug resolution', 'deployment speed']
    },
    'Cloud Engineering': {
        'technical': ['aws', 'azure', 'gcp', 'ec2', 's3', 'lambda', 'rds', 'docker', 'kubernetes',
                     'terraform', 'cloudformation', 'jenkins', 'ci/cd', 'monitoring', 'logging',
                     'security', 'networking', 'devops', 'infrastructure as code'],
        'soft_skills': ['infrastructure design', 'troubleshooting', 'documentation', 'collaboration'],
        'metrics': ['uptime', 'cost optimization', 'scalability', 'performance', 'security score']
    },
    'Automation Testing': {
        'technical': ['selenium', 'pytest', 'unittest', 'java', 'python', 'cucumber', 'jira', 'git',
                     'ci/cd', 'jenkins', 'rest api testing', 'sql', 'load testing', 'performance testing',
                     'postman', 'insomnia', 'mobile testing', 'appium'],
        'soft_skills': ['attention to detail', 'communication', 'analytical', 'documentation'],
        'metrics': ['test coverage', 'bug detection', 'time to market', 'quality assurance', 'defect rate']
    }
}

STRONG_ACTION_VERBS = {
    'achievement': ['accomplished', 'achieved', 'delivered', 'exceeded', 'surpassed', 'attained', 'realized'],
    'creation': ['built', 'created', 'designed', 'developed', 'engineered', 'produced', 'constructed'],
    'improvement': ['improved', 'enhanced', 'optimized', 'streamlined', 'refined', 'elevated', 'accelerated'],
    'leadership': ['led', 'managed', 'directed', 'orchestrated', 'coordinated', 'spearheaded', 'championed'],
    'analysis': ['analyzed', 'evaluated', 'assessed', 'examined', 'investigated', 'scrutinized', 'diagnosed'],
    'implementation': ['implemented', 'deployed', 'rolled out', 'executed', 'launched', 'initiated', 'established'],
    'increase': ['increased', 'boosted', 'amplified', 'multiplied', 'scaled', 'expanded', 'grew'],
    'reduction': ['reduced', 'minimized', 'decreased', 'cut', 'eliminated', 'slashed', 'lowered'],
    'automation': ['automated', 'mechanized', 'streamlined', 'systematized', 'simplified', 'accelerated'],
    'collaboration': ['collaborated', 'partnered', 'coordinated', 'communicated', 'liaised', 'synergized']
}


def preprocess_text(text: str) -> str:
    """Lowercase, remove non-ascii, drop extra whitespace and punctuation."""
    text = unidecode(text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_skills(text: str) -> list:
    """Return list of candidate skills using keyword matching with scoring.
    
    Uses keyword matching with context awareness for better accuracy.
    """
    found = []
    text_lower = text.lower()
    
    for skill in SKILL_KEYWORDS:
        # Check if skill appears in text
        if skill in text_lower:
            # Prioritize exact word boundaries for better matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.append(skill)
            elif skill in text_lower:  # Fallback to substring match
                found.append(skill)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_found = []
    for skill in found:
        if skill not in seen:
            seen.add(skill)
            unique_found.append(skill)
    
    return unique_found


def calculate_skill_match(resume: str, jd: str) -> float:
    """Compute percentage of jd skills that appear in resume."""
    resume_words = set(resume.split())
    jd_words = set(jd.split())
    if not jd_words:
        return 0.0
    match = len(resume_words & jd_words)
    return round((match / len(jd_words)) * 100, 2)


def compute_ats_score(resume_text: str, jd_text: str = '') -> float:
    """Comprehensive ATS scoring with multiple factors."""
    score = 0.0
    
    # 1. Content Quality & Length (20 points)
    word_count = len(resume_text.split())
    if word_count >= 300:
        score += 20
    elif word_count >= 200:
        score += 15
    elif word_count >= 100:
        score += 10
    else:
        score += 5
    
    # 2. Section Presence (20 points) - allow variations
    section_keywords = {
        'experience': ['experience', 'work history', 'employment', 'professional'],
        'education': ['education', 'degree', 'university', 'school', 'graduated'],
        'skills': ['skills', 'competencies', 'expertise', 'proficiencies'],
        'projects': ['projects', 'portfolio', 'accomplishments'],
        'contact': ['email', 'phone', '+', '@']
    }
    
    sections_found = 0
    for section, keywords in section_keywords.items():
        if any(kw in resume_text for kw in keywords):
            sections_found += 1
    
    score += (sections_found / len(section_keywords)) * 20
    
    # 3. Contact Information (10 points)
    contact_score = 0
    if '@' in resume_text:  # Has email
        contact_score += 5
    if '+' in resume_text or 'phone' in resume_text:  # Has phone
        contact_score += 5
    score += contact_score
    
    # 4. Quantification & Metrics (15 points)
    numbers = re.findall(r'\d+', resume_text)
    achievement_keywords = ['increased', 'improved', 'reduced', 'achieved', 'delivered', 
                           'managed', 'led', 'developed', 'designed', 'implemented']
    achievement_count = sum(1 for kw in achievement_keywords if kw in resume_text)
    
    if len(numbers) >= 5:
        score += 10
    elif len(numbers) >= 3:
        score += 7
    elif len(numbers) > 0:
        score += 4
    
    if achievement_count >= 5:
        score += 5
    elif achievement_count > 0:
        score += 3
    
    # 5. Online Presence & Links (10 points)
    online_keywords = ['github', 'linkedin', 'portfolio', 'website', 'http', 'www']
    online_score = min(10, len([kw for kw in online_keywords if kw in resume_text]) * 3)
    score += online_score
    
    # 6. Professional Keywords (15 points)
    professional_keywords = ['results', 'impact', 'efficiency', 'quality', 'deadline', 
                            'collaboration', 'leadership', 'innovation', 'strategy', 'growth']
    prof_count = sum(1 for kw in professional_keywords if kw in resume_text)
    
    if prof_count >= 8:
        score += 15
    elif prof_count >= 5:
        score += 12
    elif prof_count >= 3:
        score += 8
    elif prof_count > 0:
        score += 4
    
    # 7. Action Verbs (10 points)
    action_verbs = ['developed', 'designed', 'managed', 'led', 'created', 'implemented',
                   'analyzed', 'improved', 'achieved', 'delivered', 'increased', 'reduced',
                   'built', 'engineered', 'coordinated', 'directed']
    verb_count = sum(1 for verb in action_verbs if verb in resume_text)
    
    if verb_count >= 8:
        score += 10
    elif verb_count >= 5:
        score += 8
    elif verb_count >= 3:
        score += 6
    elif verb_count > 0:
        score += 3
    
    # 8. Bonus: Job Description Match (if provided)
    if jd_text:
        # Extract important keywords from JD (skills, tools, terms)
        jd_keywords = [w for w in jd_text.split() if len(w) > 4]  # Filter short words
        resume_lower = resume_text.lower()
        matches = sum(1 for kw in jd_keywords if kw.lower() in resume_lower)
        
        if len(jd_keywords) > 0:
            match_percentage = (matches / len(jd_keywords)) * 100
            # Award up to 10 bonus points for JD match
            bonus = min(10, (matches / max(len(jd_keywords), 20)) * 10)
            score += bonus
    
    # Ensure score doesn't exceed 100
    return round(min(score, 100), 2)


def find_missing_keywords(resume_text: str, jd_text: str) -> list:
    """Return words in JD that are not in resume (minimum length 4)."""
    resume_words = set(resume_text.split())
    jd_words = set(jd_text.split())
    missing = [w for w in jd_words if w not in resume_words and len(w) > 3]
    return missing


def suggest_improvements(resume_text: str) -> list:
    """Give comprehensive suggestions based on resume analysis."""
    suggestions = []
    
    # Section presence checks
    if 'experience' not in resume_text:
        suggestions.append('Add an Experience section - this is crucial for employers')
    if 'education' not in resume_text:
        suggestions.append('Include your Education details and degree information')
    if 'skills' not in resume_text:
        suggestions.append('Add a dedicated Skills section listing your key competencies')
    if 'certifications' not in resume_text and 'certificate' not in resume_text:
        suggestions.append('Include relevant certifications or professional credentials')
    if 'projects' not in resume_text:
        suggestions.append('Add a Projects section to showcase your hands-on work')
    
    # Content quality checks
    word_count = len(resume_text.split())
    if word_count < 150:
        suggestions.append(f'Expand content - aim for at least 150 words (currently {word_count})')
    elif word_count < 300:
        suggestions.append('Add more detailed descriptions of your achievements and responsibilities')
    
    if 'achievements' not in resume_text and 'results' not in resume_text and 'improved' not in resume_text:
        suggestions.append('Use quantified achievements (e.g., "Increased sales by 25%")')
    
    # Formatting checks
    lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
    if len(lines) < 5:
        suggestions.append('Use proper line breaks and formatting to improve readability')
    
    # Action verb checks
    action_verbs = ['developed', 'designed', 'managed', 'led', 'created', 'implemented', 
                   'analyzed', 'improved', 'achieved', 'delivered', 'increased', 'reduced']
    action_verb_count = sum(1 for verb in action_verbs if verb in resume_text)
    if action_verb_count < 3:
        suggestions.append('Start bullet points with strong action verbs (e.g., "Developed", "Led", "Managed")')
    
    # Keyword density check
    if len(resume_text.split()) > 50:
        unique_words = len(set(resume_text.split()))
        diversity = unique_words / len(resume_text.split())
        if diversity < 0.4:
            suggestions.append('Avoid excessive repetition - use varied terminology')
    
    # Contact info check
    if '@' not in resume_text:
        suggestions.append('Ensure your email address/contact information is included')
    if 'phone' not in resume_text and '+' not in resume_text:
        suggestions.append('Add your phone number for easy contact')
    
    # Numeric improvement check
    numbers = re.findall(r'\d+', resume_text)
    if len(numbers) < 3:
        suggestions.append('Add numbers and metrics to your achievements (percentages, amounts, dates)')
    
    # Keywords for ATS
    ats_keywords = ['results', 'impact', 'growth', 'efficiency', 'quality', 'deadline']
    ats_keyword_count = sum(1 for kw in ats_keywords if kw in resume_text)
    if ats_keyword_count < 2:
        suggestions.append('Include ATS-friendly keywords like "results", "impact", "efficiency"')
    
    # Specificity check
    vague_terms = ['good', 'nice', 'okay', 'bad', 'worked on', 'did stuff']
    vague_count = sum(1 for term in vague_terms if term in resume_text.lower())
    if vague_count > 0:
        suggestions.append('Replace vague terms with specific accomplishments and metrics')
    
    # Remove duplicates and limit to 15 suggestions
    return list(dict.fromkeys(suggestions))[:15]


def detect_errors(text: str) -> list:
    """Return a comprehensive list of detected issues."""
    errors = []
    text_lower = text.lower()
    
    # 1. Personal pronoun usage
    personal_pronouns = ['i ', 'me ', 'my ', 'we ', 'us ']
    pronoun_count = sum(text.count(p) for p in personal_pronouns)
    if pronoun_count > len(text.split()) * 0.15:
        errors.append('❌ Avoid excessive personal pronouns ("I", "me", "my") - use action verbs instead')
    
    # 2. Weak/vague language
    weak_words = ['some', 'quite', 'rather', 'somehow', 'sort of', 'kind of', 'basically', 'literally']
    weak_count = sum(text_lower.count(w) for w in weak_words)
    if weak_count > 3:
        errors.append('❌ Remove vague language ("sort of", "kind of", "quite") - be direct and specific')
    
    # 3. Spelling/Grammar - common mistakes
    common_errors = {
        'recieved': 'received',
        'occured': 'occurred',
        'untill': 'until',
        'sucessful': 'successful',
        'responsability': 'responsibility',
        'adress': 'address',
        'managment': 'management',
        'exprience': 'experience'
    }
    
    for wrong, correct in common_errors.items():
        if wrong in text_lower:
            errors.append(f'❌ Spelling: Change "{wrong}" to "{correct}"')
    
    # 4. Excessive punctuation
    if text.count('!!!') > 0 or text.count('???') > 0:
        errors.append('❌ Avoid multiple exclamation marks or question marks - keep it professional')
    
    # 5. Inconsistent capitalization
    all_caps_words = re.findall(r'\b[A-Z]{3,}\b', text)
    if len(all_caps_words) > 5:
        errors.append('❌ Reduce ALL CAPS usage - use proper capitalization instead')
    
    # 6. Sentence fragments or very short sentences
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    short_sentences = [s for s in sentences if len(s.split()) < 2]
    if len(short_sentences) > 2:
        errors.append('❌ Avoid sentence fragments - ensure each statement is complete')
    
    # 7. Inconsistent date formats
    dates_slash = len(re.findall(r'\d{1,2}/\d{1,2}/\d{2,4}', text))
    dates_dash = len(re.findall(r'\d{1,2}-\d{1,2}-\d{2,4}', text))
    if (dates_slash > 0 and dates_dash > 0) or dates_slash > 2 or dates_dash > 2:
        errors.append('⚠️ Use consistent date formats throughout (MM/DD/YYYY or MM-DD-YYYY)')
    
    # 8. Missing periods at end of sentences
    lines = text.split('\n')
    lines_without_period = [l.strip() for l in lines if l.strip() and not l.strip().endswith(('.', ':', '-'))]
    if len(lines_without_period) > 5:
        errors.append('⚠️ Ensure bullet points and descriptions end with proper punctuation')
    
    # 9. Email format check
    if '@' in text:
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if not emails:
            errors.append('⚠️ Email format looks incorrect - use name@domain.com')
    
    # 10. Inconsistent spacing
    if '  ' in text:  # Double spaces
        errors.append('⚠️ Remove extra spaces between words for cleaner formatting')
    
    # 11. Check for action verb variety - if too few
    action_verbs = ['developed', 'designed', 'managed', 'led', 'created', 'implemented',
                   'analyzed', 'improved', 'achieved', 'delivered', 'increased', 'reduced',
                   'built', 'engineered', 'coordinated', 'directed']
    verb_count = sum(1 for verb in action_verbs if verb in text_lower)
    if verb_count < 2:
        errors.append('💡 Use strong action verbs: "Developed", "Led", "Managed", "Designed"')
    
    # 12. Check for quantification
    numbers = re.findall(r'\d+', text)
    if len(numbers) < 2:
        errors.append('💡 Add metrics and numbers to demonstrate impact (e.g., "increased by 35%")')
    
    # 13. Check for jargon overuse
    jargon_words = ['synergy', 'leverage', 'paradigm', 'circle back', 'touch base', 'bandwidth']
    jargon_count = sum(1 for j in jargon_words if j in text_lower)
    if jargon_count > 2:
        errors.append('⚠️ Reduce business jargon - use clear, concise language instead')
    
    # 14. Check for excessive length of bullet points
    bullet_lines = [l.strip() for l in text.split('\n') if l.strip().startswith(('-', '•', '*'))]
    long_bullets = [b for b in bullet_lines if len(b.split()) > 20]
    if len(long_bullets) > 2:
        errors.append('⚠️ Keep bullet points concise - aim for one or two lines per point')
    
    # Return unique errors, limit to 12
    return list(dict.fromkeys(errors))[:12]


def best_suited_roles(resume_text: str) -> list:
    """Return list of roles mapped from found skills."""
    skills = extract_skills(resume_text)
    roles = set()
    for skill in skills:
        if skill in ROLE_MAP:
            roles.add(ROLE_MAP[skill])
    return list(roles) if roles else ['General Candidate']


def career_advice(resume_text: str) -> list:
    """Return comprehensive career and resume improvement recommendations."""
    advice = []
    roles = best_suited_roles(resume_text)
    ats_score = compute_ats_score(resume_text)
    
    # Role-specific advice
    if 'Software Engineer' in roles or 'Developer' in roles:
        if 'github' not in resume_text:
            advice.append('Add your GitHub profile link to showcase coding projects')
        if 'portfolio' not in resume_text:
            advice.append('Include a portfolio or personal website showcasing your work')
    
    if 'Machine Learning Engineer' in roles or 'Data Scientist' in roles:
        if 'python' not in resume_text:
            advice.append('Emphasize Python expertise for ML roles')
        if 'tensorflow' not in resume_text and 'pytorch' not in resume_text:
            advice.append('Mention experience with ML frameworks (TensorFlow, PyTorch)')
        if 'kaggle' not in resume_text:
            advice.append('Include Kaggle competitions or personal ML projects')
    
    if 'Cloud Engineer' in roles or 'DevOps Engineer' in roles:
        if 'aws' not in resume_text and 'azure' not in resume_text and 'gcp' not in resume_text:
            advice.append('Add cloud platform certifications (AWS, Azure, GCP)')
        if 'docker' not in resume_text and 'kubernetes' not in resume_text:
            advice.append('Highlight containerization and orchestration skills')
    
    if 'Data Analyst' in roles or 'Business Analyst' in roles:
        if 'sql' not in resume_text:
            advice.append('Include SQL proficiency - essential for data roles')
        if 'tableau' not in resume_text and 'power bi' not in resume_text:
            advice.append('Mention data visualization tools (Tableau, Power BI, Excel)')
    
    # Content improvement advice
    word_count = len(resume_text.split())
    if word_count < 200:
        advice.append('Expand your resume with more specific achievements and metrics')
    
    if 'linkedin' not in resume_text:
        advice.append('Add your LinkedIn profile URL for professional networking')
    
    if 'measurable' not in resume_text and ':' not in resume_text:
        advice.append('Use bullet points with clear structure and measurable outcomes')
    
    # ATS optimization
    if ats_score < 50:
        advice.append('Optimize for ATS: use standard section headers and proper formatting')
    
    # Generic improvement
    if len(advice) < 3:
        advice.append('Highlight your top 3-5 most relevant skills for the role')
        advice.append('Quantify your impact with numbers and percentages')
        advice.append('Use industry-specific terminology relevant to your target role')
    
    return advice[:10]


def suggest_jobs(skills: list) -> list:
    """Return a list of example job titles based on skills.

    In a full implementation this might call a real job API.
    """
    suggestions = []
    for skill in skills:
        if 'python' in skill:
            suggestions.append('Backend Developer')
        if 'aws' in skill or 'azure' in skill:
            suggestions.append('Cloud Engineer')
        if 'data' in skill or 'machine learning' in skill:
            suggestions.append('Data Scientist')
    return list(dict.fromkeys(suggestions))


def get_resume_quality_metrics(resume_text: str, jd_text: str = '') -> dict:
    """Provide detailed resume quality metrics and breakdown."""
    metrics = {}
    
    # Basic content metrics
    words = resume_text.split()
    word_count = len(words)
    sentences = [s.strip() for s in resume_text.split('.') if s.strip()]
    lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
    
    metrics['word_count'] = word_count
    metrics['sentence_count'] = len(sentences)
    metrics['readability'] = 'Excellent' if word_count >= 300 else 'Good' if word_count >= 200 else 'Fair' if word_count >= 150 else 'Poor'
    
    # Structure Assessment
    sections_found = {
        'experience': any(k in resume_text.lower() for k in ['experience', 'work history', 'employment']),
        'education': any(k in resume_text.lower() for k in ['education', 'degree', 'university']),
        'skills': 'skills' in resume_text.lower(),
        'projects': any(k in resume_text.lower() for k in ['projects', 'portfolio']),
        'contact': '@' in resume_text or '+' in resume_text
    }
    metrics['sections'] = sections_found
    metrics['completeness'] = f"{sum(sections_found.values())}/5 sections"
    
    # Skills Assessment
    skills = extract_skills(resume_text)
    metrics['skills_found'] = len(skills)
    metrics['top_skills'] = skills[:5] if skills else []
    
    # Content Quality
    action_verbs = ['developed', 'designed', 'managed', 'led', 'created', 'implemented',
                   'analyzed', 'improved', 'achieved', 'delivered', 'increased', 'reduced']
    action_verb_count = sum(1 for verb in action_verbs if verb in resume_text.lower())
    
    numbers = re.findall(r'\d+', resume_text)
    metrics['action_verb_count'] = action_verb_count
    metrics['quantification_score'] = len(numbers)
    
    # Professional keywords
    prof_keywords = ['results', 'impact', 'efficiency', 'quality', 'leadership', 'innovation']
    prof_count = sum(1 for kw in prof_keywords if kw in resume_text.lower())
    metrics['professional_language'] = prof_count
    
    # Error Assessment
    errors = detect_errors(resume_text)
    metrics['error_count'] = len(errors)
    metrics['errors'] = errors
    
    # ATS Score
    ats_score = compute_ats_score(resume_text, jd_text)
    metrics['ats_score'] = ats_score
    
    # Overall Quality Grade
    quality_score = 0
    quality_score += min(20, (word_count / 15))  # Content length
    quality_score += sum(sections_found.values()) * 16  # Structure (max 80)
    quality_score += min(10, (action_verb_count / 2))  # Action verbs
    quality_score += min(10, (len(numbers) / 3))  # Quantification
    quality_score += min(10, (prof_count * 2))  # Professional language
    quality_score -= len(errors) * 2  # Deduct for errors
    
    quality_score = max(0, min(100, quality_score))
    metrics['quality_score'] = round(quality_score, 1)
    
    # Assign Grade
    if quality_score >= 85:
        metrics['grade'] = 'A (Excellent)'
    elif quality_score >= 75:
        metrics['grade'] = 'B (Good)'
    elif quality_score >= 65:
        metrics['grade'] = 'C (Fair)'
    elif quality_score >= 50:
        metrics['grade'] = 'D (Needs Improvement)'
    else:
        metrics['grade'] = 'F (Poor)'
    
    return metrics

def get_action_verb_suggestions(resume_text: str) -> dict:
    """Return suggestions for replacing weak verbs with strong action verbs."""
    suggestions = {}
    
    weak_verbs = ['worked', 'did', 'helped', 'was', 'involved', 'responsible', 'handled', 'made']
    replacements = {
        'worked': ['developed', 'engineered', 'created', 'built', 'implemented'],
        'did': ['accomplished', 'achieved', 'delivered', 'executed', 'completed'],
        'helped': ['enabled', 'facilitated', 'supported', 'empowered', 'collaborated'],
        'was': ['served as', 'functioned as', 'became', 'proved to be'],
        'involved': ['contributed to', 'participated in', 'spearheaded', 'orchestrated'],
        'responsible': ['accountable for', 'led', 'managed', 'directed', 'oversaw'],
        'handled': ['managed', 'coordinated', 'administered', 'supervised', 'controlled'],
        'made': ['created', 'developed', 'designed', 'engineered', 'produced']
    }
    
    for weak in weak_verbs:
        if weak in resume_text.lower():
            suggestions[weak] = replacements[weak]
    
    return suggestions


def get_keyword_gap_analysis(resume_text: str, detected_roles: list) -> dict:
    """Analyze keyword gaps between resume and industry standards for roles."""
    analysis = {}
    
    for role in detected_roles[:3]:  # Top 3 roles
        if role in INDUSTRY_KEYWORDS:
            keywords = INDUSTRY_KEYWORDS[role]
            text_lower = resume_text.lower()
            
            # Check technical keywords
            tech_found = [k for k in keywords['technical'] if k in text_lower]
            tech_missing = [k for k in keywords['technical'] if k not in text_lower]
            
            # Check soft skills
            soft_found = [k for k in keywords['soft_skills'] if k in text_lower]
            soft_missing = [k for k in keywords['soft_skills'] if k not in text_lower]
            
            analysis[role] = {
                'technical_found': tech_found[:5],
                'technical_missing': tech_missing[:5],
                'soft_skills_found': soft_found[:3],
                'soft_skills_missing': soft_missing[:3],
                'coverage': round((len(tech_found) + len(soft_found)) / (len(keywords['technical']) + len(keywords['soft_skills'])) * 100, 1)
            }
    
    return analysis


def generate_professional_summary(resume_text: str, roles: list) -> str:
    """Generate an optimized professional summary."""
    skills = extract_skills(resume_text)
    
    if not skills or not roles:
        return "Results-driven professional with expertise in key technical and business domains, seeking challenging opportunities to drive innovation and deliver measurable impact."
    
    top_role = roles[0] if roles else "Professional"
    top_skills = ', '.join(skills[:4])
    
    summary = f"Accomplished {top_role} with proven expertise in {top_skills}. Demonstrated track record of designing and implementing solutions that drive business value, improve operational efficiency, and deliver measurable results. Strong background in problem-solving, collaboration, and leveraging emerging technologies to achieve organizational objectives."
    
    return summary


def rewrite_bullet_points(resume_text: str) -> dict:
    """Identify weak bullet points and suggest rewrites."""
    suggestions = {}
    
    weak_patterns = {
        'Responsible for': 'Led, managed, or directed',
        'Worked on': 'Developed, designed, or engineered',
        'Helped with': 'Enabled, facilitated, or supported',
        'Involved in': 'Spearheaded, orchestrated, or coordinated',
        'Did some': 'Accomplished, achieved, or delivered'
    }
    
    for weak, strong in weak_patterns.items():
        count = resume_text.count(weak)
        if count > 0:
            suggestions[weak] = {'replacement': strong, 'occurrences': count}
    
    return suggestions


def get_ats_optimization_report(resume_text: str, jd_text: str = '') -> dict:
    """Generate comprehensive ATS optimization report."""
    report = {}
    
    # Current state
    current_ats = compute_ats_score(resume_text, jd_text)
    roles = best_suited_roles(resume_text)
    metrics = get_resume_quality_metrics(resume_text, jd_text)
    errors = detect_errors(resume_text)
    
    report['current_ats_score'] = current_ats
    report['target_ats_score'] = '90+'
    
    # Section Analysis
    sections_needed = {
        'professional_summary': 'Professional Summary' not in resume_text and 'Summary' not in resume_text,
        'experience': not any(k in resume_text.lower() for k in ['experience', 'employment']),
        'skills': 'skills' not in resume_text.lower(),
        'projects': not any(k in resume_text.lower() for k in ['projects', 'portfolio']),
        'certifications': not any(k in resume_text.lower() for k in ['certifications', 'certified']),
        'online_presence': not any(k in resume_text.lower() for k in ['github', 'linkedin', 'portfolio'])
    }
    report['missing_sections'] = [s.replace('_', ' ').title() for s, missing in sections_needed.items() if missing]
    
    # Keyword Analysis
    keyword_gaps = get_keyword_gap_analysis(resume_text, roles)
    report['keyword_gaps'] = keyword_gaps
    
    # Action Verb Analysis
    action_verb_suggestions = get_action_verb_suggestions(resume_text)
    report['weak_verbs_found'] = len(action_verb_suggestions)
    report['verb_replacements'] = action_verb_suggestions
    
    # Bullet Point Analysis
    bullet_suggestions = rewrite_bullet_points(resume_text)
    report['weak_bullets_found'] = len(bullet_suggestions)
    report['bullet_improvements'] = bullet_suggestions
    
    # Professional Summary
    report['optimized_professional_summary'] = generate_professional_summary(resume_text, roles)
    
    # Skills Optimization
    skills = extract_skills(resume_text)
    report['current_skills_identified'] = skills[:8]
    
    if roles:
        role = roles[0]
        if role in INDUSTRY_KEYWORDS:
            suggested = INDUSTRY_KEYWORDS[role]['technical'][:5]
            report['suggested_skills_to_add'] = [s for s in suggested if s not in resume_text.lower()][:5]
    
    # Keywords for ATS
    ats_keywords = ['impact', 'results', 'achieved', 'delivered', 'improved', 'managed', 'led',
                   'analyzed', 'implemented', 'optimized', 'designed', 'developed', 'engineered']
    ats_kw_found = [k for k in ats_keywords if k in resume_text.lower()]
    report['ats_keyword_density'] = f"{len(ats_kw_found)}/13 key ATS terms found"
    
    # Formatting recommendations
    formatting_tips = []
    if len(resume_text.split('\n')) < 20:
        formatting_tips.append("Add more structure with clear section breaks and bullet points")
    if not re.search(r'\b\d{1,3}%|\b\d+\s*(dollars|employees|projects|minutes|hours)', resume_text):
        formatting_tips.append("Include quantifiable metrics (%, numbers, dollar amounts)")
    if resume_text.count('*') < 3 and resume_text.count('•') < 3 and resume_text.count('-') < 5:
        formatting_tips.append("Use consistent bullet points for better ATS parsing")
    
    report['formatting_recommendations'] = formatting_tips
    
    # Estimated improvement
    potential_score_boost = 0
    if report['missing_sections']:
        potential_score_boost += len(report['missing_sections']) * 5
    potential_score_boost += min(report['weak_verbs_found'] * 2, 15)
    potential_score_boost += min(len(ats_keywords) - len(ats_kw_found), 10)
    
    improved_score = min(current_ats + potential_score_boost, 100)
    report['estimated_improved_score'] = improved_score
    report['improvement_potential'] = improved_score - current_ats
    
    # Priority recommendations
    priority = []
    if report['missing_sections']:
        priority.append(f"Add missing sections: {', '.join(report['missing_sections'][:3])}")
    if report['weak_verbs_found'] > 0:
        priority.append(f"Replace {report['weak_verbs_found']} weak verbs with action words")
    if len(keyword_gaps) > 0:
        first_role = list(keyword_gaps.keys())[0] if keyword_gaps else None
        if first_role and keyword_gaps[first_role]['coverage'] < 50:
            priority.append(f"Add relevant keywords for {first_role} role")
    if not any(k in resume_text.lower() for k in ['github', 'linkedin', 'portfolio']):
        priority.append("Include links to GitHub, LinkedIn, or Portfolio")
    
    report['priority_recommendations'] = priority[:5]
    
    return report