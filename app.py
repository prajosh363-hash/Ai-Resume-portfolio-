import streamlit as st
import json
import os
from jinja2 import Environment, FileSystemLoader

# Import custom modules
from utils.ats import extract_keywords, merge_keywords, keyword_match_score
from utils.llm import generate_text
from utils.generate_docx import render_docx
from utils.generate_pdf import render_pdf
from utils.portfolio import make_portfolio_zip

# Configure Streamlit page
st.set_page_config(
    page_title="AI Resume & Portfolio Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-top: 1.5rem;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #10B981;
    }
    .info-box {
        background-color: #E0F2FE;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Title and description
    st.markdown('<h1 class="main-header">🤖 AI Resume & Portfolio Builder</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
    Generate tailored, ATS-aware resumes, cover letters, and portfolios from student profile JSON.
    Upload your profile data and let AI craft the perfect job application materials.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Template selection
        template_choice = st.selectbox(
            "Choose Resume Template",
            ["modern", "classic", "professional"],
            help="Select a design template for your resume"
        )
        
        # Export format
        export_format = st.selectbox(
            "Export Format",
            ["PDF", "DOCX", "BOTH"],
            help="Choose the file format for download"
        )
        
        # ATS optimization toggle
        optimize_ats = st.checkbox(
            "Enable ATS Optimization",
            value=True,
            help="Optimize resume for Applicant Tracking Systems"
        )
        
        # Additional options
        st.header("🎨 Customization")
        include_portfolio = st.checkbox("Include Portfolio", value=True)
        include_cover_letter = st.checkbox("Include Cover Letter", value=True)
        
        st.divider()
        
        # Example JSON button
        if st.button("📋 Load Example Profile"):
            example_profile = {
                "name": "Jane Smith",
                "email": "jane.smith@email.com",
                "phone": "+1 (555) 123-4567",
                "location": "San Francisco, CA",
                "education": [
                    {
                        "degree": "Bachelor of Science in Computer Science",
                        "university": "Stanford University",
                        "graduation_year": "2023",
                        "gpa": "3.8"
                    }
                ],
                "experience": [
                    {
                        "title": "Software Engineering Intern",
                        "company": "TechCorp Inc.",
                        "duration": "Jun 2022 - Aug 2022",
                        "actions": [
                            "Developed full-stack web applications using React and Node.js",
                            "Implemented RESTful APIs serving 10,000+ daily requests",
                            "Collaborated with cross-functional teams using Agile methodology"
                        ],
                        "outcomes": [
                            "Reduced API response time by 40%",
                            "Improved application performance by 25%"
                        ]
                    }
                ],
                "skills": {
                    "technical": ["Python", "JavaScript", "React", "Node.js", "SQL", "AWS"],
                    "soft": ["Leadership", "Communication", "Problem Solving"]
                },
                "projects": [
                    {
                        "name": "AI Resume Analyzer",
                        "description": "Built a machine learning model to analyze resume effectiveness",
                        "technologies": ["Python", "scikit-learn", "FastAPI"]
                    }
                ],
                "achievements": [
                    "Dean's List for 4 consecutive semesters",
                    "First place in University Hackathon 2022"
                ],
                "targets": {
                    "role": "Software Engineer",
                    "industry": "Technology",
                    "job_description": "Seeking a skilled software engineer with experience in Python, JavaScript, React, and cloud technologies. The ideal candidate should have strong problem-solving skills and experience with full-stack development."
                },
                "summary_preferences": {
                    "tone": "professional",
                    "length": "medium"
                }
            }
            st.session_state.profile_json = json.dumps(example_profile, indent=2)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📥 Input Profile Data")
        
        # File upload option
        uploaded_file = st.file_uploader(
            "Upload JSON file",
            type=['json'],
            help="Upload your profile data in JSON format"
        )
        
        # Text area for JSON input
        if uploaded_file is not None:
            profile_json = uploaded_file.read().decode("utf-8")
        else:
            profile_json = st.text_area(
                "Or paste your JSON profile here:",
                height=400,
                value=st.session_state.get('profile_json', ''),
                placeholder='Paste your student profile JSON here...'
            )
    
    with col2:
        st.subheader("🔍 Preview & Validation")
        
        if profile_json:
            try:
                profile = json.loads(profile_json)
                st.success("✅ Valid JSON format detected!")
                
                # Display basic info
                with st.expander("📊 Profile Overview"):
                    st.write(f"**Name:** {profile.get('name', 'Not specified')}")
                    st.write(f"**Target Role:** {profile.get('targets', {}).get('role', 'Not specified')}")
                    st.write(f"**Experience Items:** {len(profile.get('experience', []))}")
                    st.write(f"**Technical Skills:** {len(profile.get('skills', {}).get('technical', []))}")
                    
                    # ATS Score calculation
                    if optimize_ats:
                        jd = profile.get("targets", {}).get("job_description", "")
                        if jd:
                            score = keyword_match_score(profile, jd)
                            st.metric("📈 ATS Match Score", f"{score}%")
                
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON format: {str(e)}")
                st.stop()
    
    # Generate button
    if st.button("🚀 Generate Resume & Portfolio", type="primary", use_container_width=True):
        if not profile_json:
            st.warning("Please enter profile data first!")
            return
            
        try:
            profile = json.loads(profile_json)
            
            with st.spinner("🤖 AI is crafting your resume..."):
                # Extract ATS keywords if enabled
                jd = profile.get("targets", {}).get("job_description", "")
                if optimize_ats and jd:
                    ats_keywords = extract_keywords(jd)
                    profile = merge_keywords(profile, ats_keywords)
                else:
                    ats_keywords = []
                
                # Generate content
                summary = generate_text("summary", profile)
                
                bullets = []
                for exp in profile.get("experience", []):
                    bullet = generate_text("bullets", {
                        **profile,
                        "experience_item": exp,
                        "ats_keywords": ats_keywords
                    })
                    bullets.append(bullet)
                
                if include_cover_letter:
                    cover_letter = generate_text("cover_letter", profile)
                else:
                    cover_letter = ""
                
                # Render resume HTML
                env = Environment(loader=FileSystemLoader("utils/templates"))
                tmpl = env.get_template(f"resume_{template_choice}.html")
                
                exp_with_bullets = list(zip(profile.get("experience", []), bullets))
                
                resume_html = tmpl.render(
                    profile=profile,
                    summary=summary,
                    exp_with_bullets=exp_with_bullets,
                    include_portfolio=include_portfolio
                )
                
                # Display results
                st.markdown('<h2 class="sub-header">📄 Resume Preview</h2>', unsafe_allow_html=True)
                st.components.v1.html(resume_html, height=800, scrolling=True)
                
                if include_cover_letter:
                    st.markdown('<h2 class="sub-header">✉️ Cover Letter</h2>', unsafe_allow_html=True)
                    st.text_area("Generated Cover Letter", cover_letter, height=300)
                
                # Generate download files
                st.markdown('<h2 class="sub-header">📥 Download Files</h2>', unsafe_allow_html=True)
                
                files = []
                
                # Generate DOCX
                if export_format in ["DOCX", "BOTH"]:
                    with st.spinner("Creating DOCX file..."):
                        docx_file = render_docx(resume_html)
                        files.append(("Resume", docx_file, "docx"))
                
                # Generate PDF
                if export_format in ["PDF", "BOTH"]:
                    with st.spinner("Creating PDF file..."):
                        pdf_file = render_pdf(resume_html)
                        files.append(("Resume", pdf_file, "pdf"))
                
                # Generate portfolio
                if include_portfolio:
                    with st.spinner("Creating portfolio package..."):
                        portfolio_file = make_portfolio_zip(profile, resume_html, cover_letter)
                        files.append(("Portfolio", portfolio_file, "zip"))
                
                # Create download buttons
                col1, col2, col3 = st.columns(3)
                
                for i, (name, file_path, ext) in enumerate(files):
                    col = [col1, col2, col3][i % 3]
                    with col:
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label=f"📥 Download {name}.{ext.upper()}",
                                data=f,
                                file_name=f"{profile.get('name', 'resume')}_{name.lower()}.{ext}",
                                mime="application/octet-stream",
                                use_container_width=True
                            )
                
                st.success("🎉 Generation complete! Your files are ready for download.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Running in development mode with sample output...")
            
            # Fallback to sample data
            st.write("**Sample Resume Output:**")
            st.code("This would be your generated resume content...")

if __name__ == "__main__":
    main()
