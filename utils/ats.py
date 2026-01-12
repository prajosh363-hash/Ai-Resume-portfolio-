from collections import Counter
import re
from typing import List, Dict, Set

class ATSExtractor:
    """ATS (Applicant Tracking System) keyword extractor and analyzer"""
    
    # Common stopwords to ignore
    STOPWORDS = {
        "and", "or", "the", "with", "from", "into", "about", "across", "within",
        "for", "that", "this", "your", "that", "will", "have", "has",
        "are", "was", "were", "to", "in", "on", "of", "by", "as", "at", "an",
        "job", "role", "responsibilities", "requirements", "skills", "experience",
        "should", "must", "would", "could", "may", "might", "can", "able",
        "work", "working", "strong", "excellent", "good", "knowledge",
        "understanding", "ability", "team", "individual", "company", "organization"
    }
    
    # Technical skill categories for better classification
    TECH_CATEGORIES = {
        "programming": ["python", "java", "javascript", "c++", "c#", "ruby", "go", "rust", "swift", "kotlin"],
        "web": ["html", "css", "react", "angular", "vue", "django", "flask", "node", "express", "spring"],
        "database": ["sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "nosql"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd"],
        "data_science": ["machine", "learning", "ai", "pytorch", "tensorflow", "pandas", "numpy"],
        "tools": ["git", "jenkins", "jira", "confluence", "slack", "vs", "code", "intellij"]
    }
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Lowercase and remove special characters"""
        if not text:
            return ""
        text = re.sub(r'[^A-Za-z0-9\s\-/&+]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.lower().strip()
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Split text into meaningful tokens"""
        text = ATSExtractor.clean_text(text)
        words = text.split()
        
        tokens = []
        for word in words:
            # Skip stopwords and short words
            if len(word) >= 3 and word not in ATSExtractor.STOPWORDS:
                # Clean up the word
                word = word.strip('.,-/_&+')
                if len(word) >= 2:  # Minimum length after cleaning
                    tokens.append(word)
        
        return tokens
    
    @staticmethod
    def extract_keywords(job_description: str, top_n: int = 30) -> List[str]:
        """
        Extract top keywords from job description with frequency analysis
        
        Args:
            job_description: The job description text
            top_n: Number of top keywords to return
            
        Returns:
            List of keywords sorted by frequency and importance
        """
        if not job_description:
            return []
        
        tokens = ATSExtractor.tokenize(job_description)
        
        if not tokens:
            return []
        
        # Count frequencies
        freq = Counter(tokens)
        
        # Boost score for technical skills
        scored_keywords = []
        for word, count in freq.items():
            score = count
            
            # Boost technical terms
            for category, terms in ATSExtractor.TECH_CATEGORIES.items():
                if word in terms:
                    score *= 2  # Double the score for technical skills
                    break
            
            scored_keywords.append((word, score, count))
        
        # Sort by boosted score, then original frequency, then alphabetically
        scored_keywords.sort(key=lambda x: (-x[1], -x[2], x[0]))
        
        # Get unique keywords
        keywords = []
        seen = set()
        for word, score, count in scored_keywords[:top_n*2]:  # Get extra for deduplication
            if word not in seen:
                keywords.append(word)
                seen.add(word)
            if len(keywords) >= top_n:
                break
        
        return keywords
    
    @staticmethod
    def merge_keywords(profile: Dict, keywords: List[str]) -> Dict:
        """Attach extracted ATS keywords to profile"""
        profile_copy = profile.copy()
        profile_copy['ats_keywords'] = keywords
        
        # Also store keyword categories for better matching
        categorized = {}
        for category, terms in ATSExtractor.TECH_CATEGORIES.items():
            category_keywords = [kw for kw in keywords if kw in terms]
            if category_keywords:
                categorized[category] = category_keywords
        
        profile_copy['ats_keyword_categories'] = categorized
        return profile_copy
    
    @staticmethod
    def keyword_match_score(profile: Dict, job_description: str) -> float:
        """Calculate match score between profile and job description"""
        if not job_description:
            return 0.0
        
        jd_keywords = set(ATSExtractor.extract_keywords(job_description))
        
        if not jd_keywords:
            return 0.0
        
        # Get profile skills
        profile_skills = set()
        
        # Technical skills from profile
        tech_skills = profile.get("skills", {}).get("technical", [])
        if isinstance(tech_skills, list):
            profile_skills.update(ATSExtractor.tokenize(' '.join(tech_skills)))
        
        # Skills from experience
        for exp in profile.get("experience", []):
            actions = exp.get("actions", [])
            if isinstance(actions, list):
                profile_skills.update(ATSExtractor.tokenize(' '.join(actions)))
            
            outcomes = exp.get("outcomes", [])
            if isinstance(outcomes, list):
                profile_skills.update(ATSExtractor.tokenize(' '.join(outcomes)))
        
        # Skills from projects
        for project in profile.get("projects", []):
            technologies = project.get("technologies", [])
            if isinstance(technologies, list):
                profile_skills.update(ATSExtractor.tokenize(' '.join(technologies)))
        
        # Calculate overlap
        overlap = jd_keywords.intersection(profile_skills)
        
        # Calculate weighted score (technical matches are more important)
        total_score = 0
        max_score = len(jd_keywords) * 2  # Maximum possible score
        
        for keyword in jd_keywords:
            if keyword in overlap:
                # Check if it's a technical skill
                is_technical = False
                for category_terms in ATSExtractor.TECH_CATEGORIES.values():
                    if keyword in category_terms:
                        is_technical = True
                        break
                
                if is_technical:
                    total_score += 2  # Technical skills get double points
                else:
                    total_score += 1
        
        if max_score == 0:
            return 0.0
        
        return round((total_score / max_score) * 100, 1)
    
    @staticmethod
    def generate_ats_tips(profile: Dict, job_description: str) -> List[str]:
        """Generate ATS optimization tips"""
        tips = []
        
        jd_keywords = set(extract_keywords(job_description))
        profile_keywords = set()
        
        # Collect all keywords from profile
        tech_skills = profile.get("skills", {}).get("technical", [])
        profile_keywords.update(ATSExtractor.tokenize(' '.join(tech_skills)))
        
        # Find missing keywords
        missing = jd_keywords - profile_keywords
        
        if missing:
            tips.append(f"**Add these keywords to your resume:** {', '.join(list(missing)[:10])}")
        
        # Check for action verbs
        action_verbs = {"developed", "implemented", "created", "managed", "led", "improved", 
                       "increased", "decreased", "optimized", "designed", "built"}
        found_verbs = profile_keywords.intersection(action_verbs)
        
        if len(found_verbs) < 5:
            tips.append("**Use more action verbs** like 'developed', 'implemented', 'led' to start bullet points")
        
        # Check for metrics
        metric_indicators = {"%", "percent", "increased", "decreased", "reduced", "improved"}
        profile_text = str(profile).lower()
        has_metrics = any(indicator in profile_text for indicator in metric_indicators)
        
        if not has_metrics:
            tips.append("**Add quantifiable metrics** to show impact (e.g., 'increased efficiency by 20%')")
        
        return tips

# Alias functions for backward compatibility
extract_keywords = ATSExtractor.extract_keywords
merge_keywords = ATSExtractor.merge_keywords
keyword_match_score = ATSExtractor.keyword_match_score
