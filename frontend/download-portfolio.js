/**
 * Production Flow for Portfolio Generation and Download
 * 
 * Flow:
 * 1. User uploads resume → Backend generates portfolio
 * 2. Backend returns download URL
 * 3. Frontend redirects to download URL
 * 4. Browser auto-downloads ZIP
 */

// Example 1: Simple auto-download after generation
async function generateAndDownloadPortfolio(resumeData) {
    try {
        console.log('Generating portfolio...');

        // Step 1: Generate portfolio
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

        const result = await response.json();

        if (result.status === 'success') {
            console.log(`✅ Portfolio generated! ID: ${result.portfolio_id}`);

            // Step 2: Redirect to download URL (auto-download)
            window.location.href = result.download_url;

            // Alternative: Show success message before download
            // setTimeout(() => {
            //     window.location.href = result.download_url;
            // }, 1000);

        } else {
            throw new Error(result.error || 'Unknown error');
        }

    } catch (error) {
        console.error('❌ Error:', error);
        alert('Failed to generate portfolio. Please try again.');
    }
}

// Example 2: With loading indicator
async function generatePortfolioWithLoading(resumeData) {
    const loadingDiv = document.getElementById('loading');
    const messageDiv = document.getElementById('message');

    try {
        // Show loading
        loadingDiv.style.display = 'block';
        messageDiv.textContent = 'Generating your portfolio...';

        const response = await fetch('/generate-portfolio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(resumeData)
        });

        const result = await response.json();

        if (result.status === 'success') {
            messageDiv.textContent = 'Portfolio ready! Download will start automatically...';

            // Wait a moment to show success message
            setTimeout(() => {
                window.location.href = result.download_url;

                // Hide loading after download starts
                setTimeout(() => {
                    loadingDiv.style.display = 'none';
                    messageDiv.textContent = 'Portfolio downloaded successfully!';
                }, 2000);
            }, 1000);
        } else {
            throw new Error(result.error);
        }

    } catch (error) {
        console.error('❌ Error:', error);
        loadingDiv.style.display = 'none';
        messageDiv.textContent = 'Error: ' + error.message;
        messageDiv.style.color = 'red';
    }
}

// Example 3: Using hidden iframe (alternative download method)
async function generatePortfolioWithIframe(resumeData) {
    try {
        const response = await fetch('/generate-portfolio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(resumeData)
        });

        const result = await response.json();

        if (result.status === 'success') {
            // Create hidden iframe for download (keeps user on same page)
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = result.download_url;
            document.body.appendChild(iframe);

            // Remove iframe after download
            setTimeout(() => {
                document.body.removeChild(iframe);
            }, 5000);

            console.log('✅ Portfolio download started!');
        }

    } catch (error) {
        console.error('❌ Error:', error);
        alert('Failed to download portfolio.');
    }
}

// Example 4: Integration with form submission
document.getElementById('portfolioForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Collect form data
    const formData = new FormData(e.target);
    const resumeData = {
        name: formData.get('name'),
        headline: formData.get('headline'),
        about: formData.get('about'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        skills: formData.get('skills').split(',').map(s => s.trim()),
        projects: [], // Collect from form
        experience: [], // Collect from form
        research: [],
        links: {
            github: formData.get('github'),
            linkedin: formData.get('linkedin')
        }
    };

    // Generate and download
    await generateAndDownloadPortfolio(resumeData);
});

// Example 5: With download button
function addDownloadButton() {
    const button = document.createElement('button');
    button.textContent = '📦 Generate & Download Portfolio';
    button.className = 'btn btn-primary';
    button.onclick = async () => {
        const resumeData = collectFormData(); // Your function to collect form data
        await generateAndDownloadPortfolio(resumeData);
    };

    document.querySelector('.form-actions')?.appendChild(button);
}

// Helper function to collect form data
function collectFormData() {
    // Implement based on your form structure
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

// Helper functions (implement based on your form)
function getSkills() {
    const skillsInput = document.getElementById('skills')?.value || '';
    return skillsInput.split(',').map(s => s.trim()).filter(s => s);
}

function getProjects() {
    // Implement based on your project form structure
    return [];
}

function getExperience() {
    // Implement based on your experience form structure
    return [];
}

function getResearch() {
    // Implement based on your research form structure
    return [];
}

function getLinks() {
    return {
        github: document.getElementById('github')?.value || '',
        linkedin: document.getElementById('linkedin')?.value || '',
        leetcode: document.getElementById('leetcode')?.value || '',
        website: document.getElementById('website')?.value || ''
    };
}
