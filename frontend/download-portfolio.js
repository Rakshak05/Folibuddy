/**
 * Simplified Production Flow for Portfolio Generation and Download
 * 
 * Flow:
 * 1. User clicks "Generate Portfolio" button
 * 2. Frontend calls POST /generate-portfolio
 * 3. Backend generates portfolio, creates ZIP, returns file
 * 4. Frontend triggers browser download
 * 5. Backend auto-cleans up temp files
 */

// Example 1: Simple download (recommended)
async function generateAndDownloadPortfolio() {
    try {
        console.log('Generating portfolio...');

        // Call endpoint - no data needed, uses saved portfolio from /generate
        const response = await fetch('/generate-portfolio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to generate portfolio');
        }

        // Get the ZIP file as a blob
        const blob = await response.blob();

        // Create download link and trigger download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'portfolio.zip';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        console.log('✅ Portfolio downloaded successfully!');
        alert('Portfolio downloaded successfully!');

    } catch (error) {
        console.error('❌ Error:', error);
        alert('Error: ' + error.message);
    }
}

// Example 2: With loading indicator
async function generatePortfolioWithLoading() {
    const loadingDiv = document.getElementById('loading');
    const messageDiv = document.getElementById('message');

    try {
        // Show loading
        if (loadingDiv) loadingDiv.style.display = 'block';
        if (messageDiv) messageDiv.textContent = 'Generating your portfolio...';

        const response = await fetch('/generate-portfolio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to generate portfolio');
        }

        if (messageDiv) messageDiv.textContent = 'Portfolio ready! Downloading...';

        // Get blob and trigger download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'portfolio.zip';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        if (messageDiv) {
            messageDiv.textContent = 'Portfolio downloaded successfully!';
            messageDiv.style.color = 'green';
        }

    } catch (error) {
        console.error('❌ Error:', error);
        if (messageDiv) {
            messageDiv.textContent = 'Error: ' + error.message;
            messageDiv.style.color = 'red';
        }
    } finally {
        if (loadingDiv) {
            setTimeout(() => {
                loadingDiv.style.display = 'none';
            }, 2000);
        }
    }
}

// Example 3: Add download button to your page
function addDownloadButton() {
    const button = document.createElement('button');
    button.textContent = '📦 Download Portfolio ZIP';
    button.className = 'btn btn-primary download-btn';
    button.style.cssText = `
        padding: 12px 24px;
        background: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
        margin-top: 20px;
    `;

    button.addEventListener('mouseover', () => {
        button.style.background = '#45a049';
    });

    button.addEventListener('mouseout', () => {
        button.style.background = '#4CAF50';
    });

    button.onclick = async () => {
        button.disabled = true;
        button.textContent = '⏳ Generating...';

        try {
            await generateAndDownloadPortfolio();
            button.textContent = '✅ Downloaded!';
            setTimeout(() => {
                button.textContent = '📦 Download Portfolio ZIP';
                button.disabled = false;
            }, 3000);
        } catch (error) {
            button.textContent = '❌ Failed - Try Again';
            button.style.background = '#f44336';
            setTimeout(() => {
                button.textContent = '📦 Download Portfolio ZIP';
                button.style.background = '#4CAF50';
                button.disabled = false;
            }, 3000);
        }
    };

    // Add to form or page
    const form = document.querySelector('form');
    if (form) {
        form.appendChild(button);
    } else {
        document.body.appendChild(button);
    }
}

// Example 4: Integration with existing "Generate Portfolio" button
document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generatePortfolioBtn');

    if (generateBtn) {
        generateBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            await generateAndDownloadPortfolio();
        });
    }
});

// Example 5: With progress indicator
async function generateWithProgress() {
    const progressDiv = document.createElement('div');
    progressDiv.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 9999;
    `;
    progressDiv.innerHTML = `
        <div style="text-align: center;">
            <div style="font-size: 24px; margin-bottom: 10px;">⏳</div>
            <div id="progressText">Generating portfolio...</div>
        </div>
    `;
    document.body.appendChild(progressDiv);

    try {
        const response = await fetch('/generate-portfolio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        document.getElementById('progressText').textContent = 'Creating ZIP file...';

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to generate portfolio');
        }

        const blob = await response.blob();

        document.getElementById('progressText').textContent = 'Downloading...';

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'portfolio.zip';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        progressDiv.innerHTML = `
            <div style="text-align: center;">
                <div style="font-size: 24px; margin-bottom: 10px; color: green;">✅</div>
                <div>Portfolio downloaded!</div>
            </div>
        `;

        setTimeout(() => {
            document.body.removeChild(progressDiv);
        }, 2000);

    } catch (error) {
        console.error('❌ Error:', error);
        progressDiv.innerHTML = `
            <div style="text-align: center;">
                <div style="font-size: 24px; margin-bottom: 10px; color: red;">❌</div>
                <div>Error: ${error.message}</div>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="margin-top: 10px; padding: 8px 16px; cursor: pointer;">
                    Close
                </button>
            </div>
        `;
    }
}

// Helper: Initialize download button when page loads
window.addEventListener('load', () => {
    // Uncomment to automatically add download button
    // addDownloadButton();
});
