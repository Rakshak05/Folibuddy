"""
Pure Pydantic schema definitions for resume data.
No business logic, no API calls, just data models.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Education(BaseModel):
    """Education entry."""
    degree: str = Field(description="Degree earned")
    institution: str = Field(description="Name of the institution")
    year: str = Field(default="", description="Year or range, e.g. 2020 or 2020-2024")
    gpa: str = Field(default="", description="GPA if available")


class Experience(BaseModel):
    """Work experience entry."""
    company: str = Field(description="Name of workplace")
    role: str = Field(description="Job title or role")
    from_date: str = Field(default="", alias="from", description="Start date")
    to_date: str = Field(default="", alias="to", description="End date")
    description: List[str] = Field(default_factory=list, description="List of bullet points describing responsibilities")
    skills: List[str] = Field(default_factory=list, description="Skills used in this role")
    
    class Config:
        populate_by_name = True


class Project(BaseModel):
    """Project entry."""
    title: str = Field(description="Project title")
    description: List[str] = Field(default_factory=list, description="List of bullet points describing the project")
    technologies: List[str] = Field(default_factory=list, description="List of technologies used")
    repo: str = Field(default="", description="GitHub repository URL if available")


class Research(BaseModel):
    """Research paper/publication entry."""
    title: str = Field(description="Research paper or publication title")
    description: List[str] = Field(default_factory=list, description="List of bullet points describing the research")
    publication: str = Field(default="", description="Publication venue if available")


class Resume(BaseModel):
    """Complete resume data structure."""
    name: str = Field(description="Full name of the candidate")
    email: str = Field(default="", description="Email address")
    phone: str = Field(default="", description="Phone number")
    linkedin: str = Field(default="", description="LinkedIn profile URL")
    github: str = Field(default="", description="GitHub profile URL")
    leetcode: str = Field(default="", description="LeetCode profile URL")
    website: str = Field(default="", description="Personal website URL")
    skills: List[str] = Field(default_factory=list, description="List of technical skills")
    projects: List[Dict[str, Any]] = Field(default_factory=list, description="List of projects")
    experience: List[Dict[str, Any]] = Field(default_factory=list, description="List of work experiences")
    research: List[Dict[str, Any]] = Field(default_factory=list, description="List of research papers")
    education: List[Dict[str, Any]] = Field(default_factory=list, description="List of education entries")
    extracurriculars: List[str] = Field(default_factory=list, description="Extracurricular activities")
