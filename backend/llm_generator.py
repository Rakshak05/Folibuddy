import requests
import json
import re


def check_ollama_available():
    """Check if Ollama server is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def fetch_github_repo_content(repo_url):
    """Fetch README and key files from a GitHub repository.
    
    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/user/repo)
    
    Returns:
        dict: Contains readme, languages, and file snippets
    """
    try:
        # Extract owner and repo from URL
        pattern = r'github\.com/([^/]+)/([^/]+)'
        match = re.search(pattern, repo_url)
        if not match:
            return None
        
        owner, repo = match.groups()
        repo = repo.replace('.git', '')  # Remove .git if present
        
        # GitHub API base URL
        api_base = f"https://api.github.com/repos/{owner}/{repo}"
        
        result = {
            "readme": "",
            "languages": [],
            "description": ""
        }
        
        # Fetch repository info
        try:
            repo_info = requests.get(api_base, timeout=5).json()
            if "description" in repo_info and repo_info["description"]:
                result["description"] = repo_info["description"]
        except:
            pass
        
        # Fetch README
        try:
            readme_response = requests.get(f"{api_base}/readme", timeout=5)
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                if "content" in readme_data:
                    import base64
                    readme_content = base64.b64decode(readme_data["content"]).decode('utf-8')
                    # Limit README to first 2000 characters
                    result["readme"] = readme_content[:2000]
        except:
            pass
        
        # Fetch languages
        try:
            lang_response = requests.get(f"{api_base}/languages", timeout=5)
            if lang_response.status_code == 200:
                languages = lang_response.json()
                result["languages"] = list(languages.keys())
        except:
            pass
        
        return result
    
    except Exception as e:
        print(f"Error fetching GitHub repo: {e}")
        return None


def generate_about_me(resume_data):
    """Generate an 'About Me' section using LLM based on resume data.
    
    Args:
        resume_data: Dictionary containing name, skills, and projects
    
    Returns:
        str: Generated about me text
    """
    try:
        name = resume_data.get("name", "the candidate")
        skills = ", ".join(resume_data.get("skills", [])[:8])  # Top 8 skills
        projects = resume_data.get("projects", [])
        
        project_titles = ", ".join([p.get("title", "") for p in projects[:3]])
        
        prompt = f"""Write a brief, professional 'About Me' section for {name}'s portfolio.

Skills: {skills}
Notable Projects: {project_titles}

Write 2-3 concise sentences in first person that:
1. Introduce their technical expertise
2. Highlight their key skills
3. Mention their passion for technology/development

Keep it professional, engaging, and authentic. Do not use emojis."""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            about_me = result.get("response", "").strip()
            return about_me
        else:
            return f"I'm a passionate developer with expertise in {skills}. I enjoy building innovative solutions and continuously learning new technologies."
    
    except Exception as e:
        print(f"Error generating about me: {e}")
        return f"A passionate developer with expertise in various technologies, dedicated to building innovative solutions."


def enhance_project_description(project_title, current_description="", repo_url=""):
    """Generate or enhance project description using LLM.
    
    If repo_url is provided, fetches repository content to generate better description.
    
    Args:
        project_title: Project title
        current_description: Existing description (if any)
        repo_url: GitHub repository URL (optional)
    
    Returns:
        str: Enhanced or generated description
    """
    try:
        # Fetch GitHub repo content if URL provided
        repo_content = None
        if repo_url and "github.com" in repo_url:
            print(f"Fetching GitHub repo for {project_title}...")
            repo_content = fetch_github_repo_content(repo_url)
        
        # Build prompt based on available information
        if repo_content and (repo_content.get("readme") or repo_content.get("description")):
            # Use repository content
            repo_desc = repo_content.get("description", "")
            readme = repo_content.get("readme", "")[:1500]  # Limit README
            languages = ", ".join(repo_content.get("languages", []))
            
            prompt = f"""Based on this GitHub repository information, write a concise project description (2-3 sentences):

Project Title: {project_title}
Repository Description: {repo_desc}
Technologies: {languages}
README snippet:
{readme}

Write a professional description that:
1. Explains what the project does
2. Highlights key technologies used
3. Mentions main features or impact

Be concise and clear. Do not use emojis."""

        elif current_description:
            # Enhance existing description
            prompt = f"""Improve this project description to be more professional and concise (2-3 sentences):

Project: {project_title}
Current description: {current_description}

Rewrite it to be clearer and more engaging while keeping the core information. Do not use emojis."""

        else:
            # Generate from title only
            prompt = f"""Write a brief professional description (2-3 sentences) for a project titled "{project_title}".

Make it sound professional and technical. Infer likely technologies and purpose from the title. Do not use emojis."""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            description = result.get("response", "").strip()
            return description
        else:
            return current_description if current_description else f"A project focused on {project_title}"
    
    except Exception as e:
        print(f"Error enhancing project description: {e}")
        return current_description if current_description else f"A comprehensive project: {project_title}"
