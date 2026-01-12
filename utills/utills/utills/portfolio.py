import zipfile
import os
import json
from datetime import datetime
from typing import Dict, Any
import tempfile

def make_portfolio_zip(profile: Dict[str, Any], resume_html: str, 
                      cover_letter: str = "") -> str:
    """
    Create a comprehensive portfolio package
    
    Args:
        profile: User profile data
        resume_html: HTML version of resume
        cover_letter: Generated cover letter
        
    Returns:
        Path to the created ZIP file
    """
    # Create temporary directory for portfolio files
    temp_dir = tempfile.mkdtemp(prefix="portfolio_")
    
    # Prepare portfolio structure
    portfolio_structure = {
        "resume": resume_html,
        "cover_letter": cover_letter,
        "profile": profile,
        "projects": profile.get("projects", []),
        "samples": [],  # Could include work samples if provided
        "readme": generate_readme(profile)
    }
    
    # 1. Save resume as HTML
    resume_path = os.path.join(temp_dir, "resume.html")
    with open(resume_path, 'w', encoding='utf-8') as f:
        f.write(resume_html)
    
    # 2. Save cover letter as TXT
    if cover_letter:
        cover_path = os.path.join(temp_dir, "cover_letter.txt")
        with open(cover_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
    
    # 3. Save profile as JSON
    profile_path = os.path.join(temp_dir, "profile.json")
    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    
    # 4. Save projects information
    projects = profile.get("projects", [])
    if projects:
        projects_path = os.path.join(temp_dir, "projects.json")
        with open(projects_path, 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
    
        # Create individual project markdown files
        projects_dir = os.path.join(temp_dir, "projects")
        os.makedirs(projects_dir, exist_ok=True)
        
        for i, project in enumerate(projects[:10]):  # Limit to 10 projects
            project_md = generate_project_markdown(project, i+1)
            project_file = os.path.join(projects_dir, f"project_{i+1}.md")
            with open(project_file, 'w', encoding='utf-8') as f:
                f.write(project_md)
    
    # 5. Create README.md
    readme_path = os.path.join(temp_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(generate_readme(profile))
    
    # 6. Create portfolio index page
    index_path = os.path.join(temp_dir, "index.html")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(generate_portfolio_index(profile, portfolio_structure))
    
    # 7. Create skills visualization
    skills_path = os.path.join(temp_dir, "skills.md")
    with open(skills_path, 'w', encoding='utf-8') as f:
        f.write(generate_skills_markdown(profile))
    
    # 8. Create ZIP file
    zip_path = os.path.join(temp_dir, "portfolio.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file != "portfolio.zip":  # Don't include the zip itself
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
    
    return zip_path

def generate_readme(profile: Dict[str, Any]) -> str:
    """Generate README.md for portfolio"""
    name = profile.get("name", "Professional Portfolio")
    role = profile.get("targets", {}).get("role", "Professional")
    
    return f"""# {name}'s Professional Portfolio

## Overview
This portfolio contains professional materials for {name}, targeting {role} positions.

## Contents
- `resume.html` - Interactive HTML resume
- `cover_letter.txt` - Tailored cover letter
- `profile.json` - Complete profile data
- `projects/` - Project documentation
- `skills.md` - Skills breakdown
- `README.md` - This file

## Generated On
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Contact
- Email: {profile.get('email', 'N/A')}
- Phone: {profile.get('phone', 'N/A')}
- Location: {profile.get('location', 'N/A')}

## Quick Start
1. Open `index.html` in a web browser for an overview
2. Review `resume.html` for the complete resume
3. Check `projects/` for detailed project information
"""

def generate_project_markdown(project: Dict[str, Any], index: int) -> str:
    """Generate markdown for a project"""
    name = project.get("name", f"Project {index}")
    description = project.get("description", "")
    technologies = project.get("technologies", [])
    duration = project.get("duration", "")
    role = project.get("role", "")
    link = project.get("link", "")
    
    return f"""# {name}

## Description
{description}

## Technologies Used
{', '.join(technologies) if technologies else 'Not specified'}

## Duration
{duration if duration else 'Not specified'}

## Role
{role if role else 'Not specified'}

## Live Demo / Repository
{link if link else 'Not available'}

## Key Features
{chr(10).join([f"- {feature}" for feature in project.get('features', [])]) if project.get('features') else '- Not specified'}

## Challenges & Solutions
{chr(10).join([f"- {challenge}" for challenge in project.get('challenges', [])]) if project.get('challenges') else '- Not specified'}
"""

def generate_portfolio_index(profile: Dict[str, Any], portfolio: Dict[str, Any]) -> str:
    """Generate HTML index page for portfolio"""
    name = profile.get("name", "Professional")
    role = profile.get("targets", {}).get("role", "Professional")
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}'s Portfolio</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        .section {{
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .file-list {{
            list-style-type: none;
            padding: 0;
        }}
        .file-list li {{
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        .file-list li:last-child {{
            border-bottom: none;
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 5px;
        }}
        .button:hover {{
            background-color: #2980b9;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{name}'s Professional Portfolio</h1>
        <h2>{role}</h2>
        <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
    </div>
    
    <div class="section">
        <h2>📁 Portfolio Contents</h2>
        <ul class="file-list">
            <li><strong>resume.html</strong> - Complete interactive resume</li>
            <li><strong>cover_letter.txt</strong> - Targeted cover letter</li>
            <li><strong>profile.json</strong> - Raw profile data</li>
            <li><strong>projects/</strong> - Project documentation</li>
            <li><strong>skills.md</strong> - Skills breakdown</li>
            <li><strong>README.md</strong> - Documentation</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>🚀 Quick Access</h2>
        <a href="resume.html" class="button">View Resume</a>
        <a href="cover_letter.txt" class="button">View Cover Letter</a>
        <a href="README.md" class="button">View README</a>
    </div>
    
    <div class="section">
        <h2>📞 Contact Information</h2>
        <p><strong>Email:</strong> {profile.get('email', 'N/A')}</p>
        <p><strong>Phone:</strong> {profile.get('phone', 'N/A')}</p>
        <p><strong>Location:</strong> {profile.get('location', 'N/A')}</p>
    </div>
</body>
</html>
"""

def generate_skills_markdown(profile: Dict[str, Any]) -> str:
    """Generate skills breakdown markdown"""
    tech_skills = profile.get("skills", {}).get("technical", [])
    soft_skills = profile.get("skills", {}).get("soft", [])
    
    # Categorize technical skills
    categories = {
        "Programming Languages": [],
        "Frameworks & Libraries": [],
        "Databases": [],
        "Cloud & DevOps": [],
        "Tools & Platforms": []
    }
    
    # Simple categorization (in real app, use more sophisticated logic)
    for skill in tech_skills:
        skill_lower = skill.lower()
        if any(lang in skill_lower for lang in ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'ruby', 'php']):
            categories["Programming Languages"].append(skill)
        elif any(fw in skill_lower for fw in ['react', 'angular', 'vue', 'django', 'flask', 'spring', '.net']):
            categories["Frameworks & Libraries"].append(skill)
        elif any(db in skill_lower for db in ['sql', 'mysql', 'postgres', 'mongodb', 'oracle', 'redis']):
            categories["Databases"].append(skill)
        elif any(cloud in skill_lower for cloud in ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform']):
            categories["Cloud & DevOps"].append(skill)
        else:
            categories["Tools & Platforms"].append(skill)
    
    # Generate markdown
    md = "# Skills Breakdown\n\n"
    
    for category, skills in categories.items():
        if skills:
            md += f"## {category}\n"
            md += ", ".join(skills) + "\n\n"
    
    if soft_skills:
        md += "## Soft Skills\n"
        md += ", ".join(soft_skills) + "\n\n"
    
    md += "## Proficiency Levels\n"
    md += "- ⭐⭐⭐⭐⭐ Expert: Deep expertise, can teach others\n"
    md += "- ⭐⭐⭐⭐ Advanced: Strong practical experience\n"
    md += "- ⭐⭐⭐ Intermediate: Can work independently\n"
    md += "- ⭐⭐ Beginner: Learning, basic understanding\n"
    md += "- ⭐ Novice: Just starting out\n"
    
    return md
