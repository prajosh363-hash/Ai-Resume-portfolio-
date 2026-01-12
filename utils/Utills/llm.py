import os
import requests
from typing import Dict, Any, Optional
import json

class LLMGenerator:
    """LLM-powered text generation for resumes and cover letters"""
    
    def __init__(self, api_url: Optional[str] = None, api_token: Optional[str] = None):
        self.api_url = api_url or os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
        self.api_token = api_token or os.getenv("LLM_API_TOKEN", "")
        
        # Fallback responses for development
        self.fallback_responses = {
            "summary": """Results-driven {role} with {experience} years of experience in {industry}. 
            Skilled in {skills}. Proven track record of {achievements}. Seeking to leverage expertise 
            in a challenging {role} position.""",
            
            "bullets": """• Developed and implemented {technology} solutions improving efficiency by 25%
            • Led cross-functional teams to deliver projects 15% ahead of schedule
            • Optimized processes resulting in 30% cost reduction
            • Collaborated with stakeholders to define requirements and deliverables""",
            
            "cover_letter": """Dear Hiring Manager,

            I am writing to express my interest in the {role} position. With my background in {industry} 
            and expertise in {skills}, I am confident in my ability to contribute to your team.

            My experience includes {achievements}, which align well with your requirements.

            I look forward to discussing how I can add value to your organization.

            Sincerely,
            {name}"""
        }
    
    def _call_llm_api(self, prompt: str, max_tokens: int = 500) -> str:
        """Call the LLM API"""
        if not self.api_token or "dev" in self.api_url.lower():
            return f"[LLM RESPONSE] {prompt[:200]}..."
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are an expert career coach and resume writer."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            return f"API Error: {str(e)}"
    
    def generate_summary(self, profile: Dict[str, Any]) -> str:
        """Generate professional summary"""
        role = profile.get("targets", {}).get("role", "professional")
        industry = profile.get("targets", {}).get("industry", "relevant industry")
        
        # Extract skills
        tech_skills = profile.get("skills", {}).get("technical", [])
        skills_text = ', '.join(tech_skills[:5]) if tech_skills else "relevant technical skills"
        
        # Extract achievements
        achievements = profile.get("achievements", [])
        achievements_text = ', '.join(achievements[:3]) if achievements else "achieving measurable results"
        
        # Get preferences
        tone = profile.get("summary_preferences", {}).get("tone", "professional")
        length = profile.get("summary_preferences", {}).get("length", "medium")
        
        prompt = f"""Write a {tone} professional summary for a {role} in the {industry} industry.
        
        Key Information:
        - Role: {role}
        - Industry: {industry}
        - Top Skills: {skills_text}
        - Key Achievements: {achievements_text}
        - Desired Tone: {tone}
        - Length: {length}
        
        Requirements:
        - {self._get_length_instruction(length)}
        - Include measurable results
        - Use industry-relevant terminology
        - Avoid clichés and generic phrases
        - Tailor to {role} position
        
        Professional Summary:"""
        
        result = self._call_llm_api(prompt, max_tokens=200)
        
        if result.startswith(("Error:", "API Error:", "[LLM RESPONSE]")):
            # Use fallback
            fallback = self.fallback_responses["summary"]
            return fallback.format(
                role=role,
                experience="3+",
                industry=industry,
                skills=skills_text,
                achievements=achievements_text
            )
        
        return result.strip()
    
    def generate_experience_bullets(self, experience_item: Dict[str, Any], 
                                   ats_keywords: list = None) -> str:
        """Generate STAR-formatted bullet points for experience"""
        title = experience_item.get("title", "Professional")
        company = experience_item.get("company", "Company")
        actions = experience_item.get("actions", [])
        outcomes = experience_item.get("outcomes", [])
        
        actions_text = '; '.join(actions[:3]) if actions else "various responsibilities"
        outcomes_text = '; '.join(outcomes[:2]) if outcomes else "positive results"
        
        # Prepare keywords for inclusion
        keywords_text = ""
        if ats_keywords:
            relevant_keywords = ats_keywords[:5]
            keywords_text = f" Naturally include these keywords: {', '.join(relevant_keywords)}."
        
        prompt = f"""Generate 3-5 impactful bullet points for a resume experience section.
        
        Position: {title} at {company}
        Key Responsibilities: {actions_text}
        Achievements/Outcomes: {outcomes_text}
        
        Requirements:{keywords_text}
        - Use STAR format (Situation, Task, Action, Result)
        - Start each bullet with strong action verbs
        - Include quantifiable metrics where possible
        - Keep each bullet concise (1-2 lines)
        - Show progression and impact
        - Use industry-standard terminology
        
        Bullet Points:"""
        
        result = self._call_llm_api(prompt, max_tokens=300)
        
        if result.startswith(("Error:", "API Error:", "[LLM RESPONSE]")):
            # Use fallback with formatted bullets
            fallback = self.fallback_responses["bullets"]
            return fallback.format(technology="relevant technology")
        
        return result.strip()
    
    def generate_cover_letter(self, profile: Dict[str, Any]) -> str:
        """Generate targeted cover letter"""
        name = profile.get("name", "Candidate")
        role = profile.get("targets", {}).get("role", "the position")
        company = profile.get("targets", {}).get("company", "your organization")
        
        # Extract key information
        skills = profile.get("skills", {}).get("technical", [])
        skills_text = ', '.join(skills[:5]) if skills else "relevant skills"
        
        achievements = profile.get("achievements", [])
        achievements_text = '; '.join(achievements[:3]) if achievements else "notable accomplishments"
        
        projects = profile.get("projects", [])
        if projects:
            project_names = [p.get("name", "") for p in projects[:2]]
            projects_text = ' and '.join(filter(None, project_names))
        else:
            projects_text = "various projects"
        
        prompt = f"""Write a professional cover letter for a job application.
        
        Applicant: {name}
        Target Position: {role} at {company}
        Key Skills: {skills_text}
        Major Achievements: {achievements_text}
        Relevant Projects: {projects_text}
        
        Requirements:
        - 300-400 words
        - Professional and enthusiastic tone
        - Three paragraphs: Introduction, Qualifications, Closing
        - Tailor to {role} position
        - Mention specific skills and achievements
        - Include a call to action
        - Avoid generic phrases
        - Show passion for the industry
        
        Cover Letter:"""
        
        result = self._call_llm_api(prompt, max_tokens=600)
        
        if result.startswith(("Error:", "API Error:", "[LLM RESPONSE]")):
            # Use fallback
            fallback = self.fallback_responses["cover_letter"]
            return fallback.format(
                role=role,
                industry=profile.get("targets", {}).get("industry", "the industry"),
                skills=skills_text,
                achievements=achievements_text,
                name=name
            )
        
        return result.strip()
    
    def _get_length_instruction(self, length: str) -> str:
        """Get length instruction based on preference"""
        lengths = {
            "short": "2-3 sentences, very concise",
            "medium": "3-4 sentences, balanced detail",
            "long": "4-5 sentences, comprehensive"
        }
        return lengths.get(length.lower(), "3-4 sentences, balanced detail")

# Singleton instance
_llm_generator = LLMGenerator()

# Public API functions
def generate_text(kind: str, data: Dict[str, Any]) -> str:
    """Generate text based on kind and data"""
    if kind == "summary":
        return _llm_generator.generate_summary(data)
    elif kind == "bullets":
        exp_item = data.get("experience_item", {})
        ats_keywords = data.get("ats_keywords", [])
        return _llm_generator.generate_experience_bullets(exp_item, ats_keywords)
    elif kind == "cover_letter":
        return _llm_generator.generate_cover_letter(data)
    else:
        return ""
