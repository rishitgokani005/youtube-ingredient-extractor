document.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('extractBtn');
  const urlInput = document.getElementById('youtubeUrl');
  const status = document.getElementById('status');
  const results = document.getElementById('results');
  const ingredientList = document.getElementById('ingredientList');
  const videoInfo = document.getElementById('videoInfo');

  btn.addEventListener('click', async () => {
    const url = urlInput.value.trim();
    results.style.display = 'none';
    ingredientList.innerHTML = '';
    status.textContent = '';
    videoInfo.textContent = '';
    
    // Clear previous status classes
    status.className = 'status';

    if (!url) {
      status.textContent = 'Please paste a YouTube URL.';
      status.classList.add('error');
      return;
    }

    // Validate YouTube URL format
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    if (!youtubeRegex.test(url)) {
      status.textContent = 'Please enter a valid YouTube URL.';
      status.classList.add('error');
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Extracting...';
    status.textContent = 'Contacting server... this may take a few seconds.';
    status.classList.add('info');

    try {
      const resp = await fetch('/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ youtube_url: url })
      });

      const data = await resp.json();

      if (!resp.ok) {
        status.textContent = data.error || 'Extraction failed';
        status.classList.add('error');
      } else {
        status.textContent = '';
        
        if (data.ingredients && data.ingredients.length) {
          // Show video ID if available
          if (data.video_id) {
            videoInfo.textContent = `Ingredients extracted from video: ${data.video_id}`;
          }
          
          results.style.display = 'block';
          
          // Format and display structured ingredients
          ingredientList.innerHTML = data.ingredients.map(ingredient => {
            let displayText = '';
            
            if (ingredient.quantity) {
              displayText += `<span class="quantity">${escapeHtml(ingredient.quantity)}</span> `;
            }
            
            if (ingredient.unit) {
              displayText += `<span class="unit">${escapeHtml(ingredient.unit)}</span> `;
            }
            
            displayText += `<span class="ingredient-name">${escapeHtml(ingredient.ingredient)}</span>`;
            
            return `<li class="ingredient-item">${displayText}</li>`;
          }).join('');
        } else {
          status.textContent = 'No ingredients found. The video may not have English captions or the transcript text didn\'t match ingredient patterns.';
          status.classList.add('warning');
        }
      }
    } catch (e) {
      status.textContent = 'Request failed: ' + e.message;
      status.classList.add('error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Extract Ingredients';
    }
  });

  // Allow pressing Enter to submit
  urlInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      btn.click();
    }
  });

  function escapeHtml(str) {
    if (typeof str !== 'string') return '';
    return str.replace(/[&<>"']/g, function(m) {
      return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[m];
    });
  }
});