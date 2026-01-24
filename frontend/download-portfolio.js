/**
 * Example frontend integration for portfolio ZIP download
 * Add this to your existing frontend JavaScript
 */

// Example 1: Download portfolio from resume data
async function downloadPortfolioZip(resumeData) {
    try {
        console.log('Generating portfolio...');

        const response = await fetch('/generate-portfolio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(resumeData)
        });

        if (!response.ok) {
            throw new Error(`Failed to generate portfolio: ${response.statusText}`);
        }

        // Get the ZIP file as a blob
        const blob = await response.blob();

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'portfolio.zip';
        document.body.appendChild(a);
        a.click();

        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        console.log('✅ Portfolio downloaded successfully!');

    } catch (error) {
        console.error('❌ Error downloading portfolio:', error);
        alert('Failed to download portfolio. Please try again.');
    }
}

// Example 2: Add download button to editor page
function addDownloadButton() {
    const downloadBtn = document.createElement('button');
    downloadBtn.textContent = '📦 Download Portfolio ZIP';
    downloadBtn.className = 'btn btn-primary';
    downloadBtn.onclick = async () => {
        // Collect form data
        const resumeData = collectFormData();
        await downloadPortfolioZip(resumeData);
    };

    // Add button to form
    const form = document.querySelector('form');
    if (form) {
        form.appendChild(downloadBtn);
    }
}

// Example 3: Collect form data (adjust based on your form structure)
function collectFormData() {
    return {
        name: document.getElementById('name')?.value || '',
        headline: document.getElementById('headline')?.value || '',
        about: document.getElementById('about')?.value || '',
        email: document.getElementById('email')?.value || '',
        phone: document.getElementById('phone')?.value || '',
        skills: getSkills(),
        projects: getProjects(),
        experience: getExperience(),
        research: getResearch(),
        links: getLinks(),
        profile_image: null
    };
}

// Helper functions (customize based on your form)
function getSkills() {
    const skillsInput = document.getElementById('skills')?.value || '';
    return skillsInput.split(',').map(s => s.trim()).filter(s => s);
}

function getProjects() {
    // Implement based on your project form structure
    const projects = [];
    let index = 1;

    while (document.getElementById(`project_title_${index}`)) {
        projects.push({
            title: document.getElementById(`project_title_${index}`).value,
            description: parseDescription(document.getElementById(`project_desc_${index}`).value),
            repo: document.getElementById(`project_repo_${index}`)?.value || ''
        });
        index++;
    }

    return projects;
}

function getExperience() {
    // Implement based on your experience form structure
    const experience = [];
    let index = 1;

    while (document.getElementById(`exp_company_${index}`)) {
        experience.push({
            company: document.getElementById(`exp_company_${index}`).value,
            role: document.getElementById(`exp_role_${index}`).value,
            from: document.getElementById(`exp_from_${index}`)?.value || '',
            to: document.getElementById(`exp_to_${index}`)?.value || '',
            description: parseDescription(document.getElementById(`exp_desc_${index}`).value),
            skills: (document.getElementById(`exp_skills_${index}`)?.value || '').split(',').map(s => s.trim()).filter(s => s)
        });
        index++;
    }

    return experience;
}

function getResearch() {
    // Implement based on your research form structure
    const research = [];
    let index = 1;

    while (document.getElementById(`research_title_${index}`)) {
        research.push({
            title: document.getElementById(`research_title_${index}`).value,
            publication: document.getElementById(`research_publication_${index}`)?.value || '',
            description: parseDescription(document.getElementById(`research_desc_${index}`).value)
        });
        index++;
    }

    return research;
}

function getLinks() {
    return {
        github: document.getElementById('github')?.value || '',
        linkedin: document.getElementById('linkedin')?.value || '',
        leetcode: document.getElementById('leetcode')?.value || '',
        website: document.getElementById('website')?.value || '',
        custom: getCustomLinks()
    };
}

function getCustomLinks() {
    const customLinks = [];
    let index = 1;

    while (document.getElementById(`custom_label_${index}`)) {
        const label = document.getElementById(`custom_label_${index}`).value;
        const url = document.getElementById(`custom_url_${index}`).value;

        if (label && url) {
            customLinks.push({ label, url });
        }
        index++;
    }

    return customLinks;
}

function parseDescription(text) {
    // Convert text to array of bullet points
    return text.split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Uncomment to add download button automatically
    // addDownloadButton();
});
