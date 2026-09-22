const form = document.querySelector('#upload-form');
const status = document.querySelector('#status');

function show(job) {
  status.classList.remove('hidden');
  const warnings = (job.warnings || []).map(x => `<li>${x}</li>`).join('');
  const path = job.progress === 100 && job.status !== 'failed'
    ? `<a href="/api/jobs/${job.id}/flight-path">Download flight path</a>` : '';
  status.innerHTML = `<h2>${job.status.replaceAll('-', ' ')}</h2><div class="meter"><i style="width:${job.progress}%"></i></div><p>${job.progress}% - ${job.message}</p>${warnings ? `<ul>${warnings}</ul>` : ''}${path}`;
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = form.querySelector('button');
  button.disabled = true;
  try {
    const response = await fetch('/api/jobs', { method: 'POST', body: new FormData(form) });
    const job = await response.json();
    if (!response.ok) throw new Error(job.detail || 'Upload failed');
    show(job);
    const timer = setInterval(async () => {
      const result = await fetch(`/api/jobs/${job.id}`);
      const latest = await result.json(); show(latest);
      if (latest.progress === 100) { clearInterval(timer); button.disabled = false; }
    }, 1200);
  } catch (error) { show({status: 'failed', progress: 100, message: error.message}); button.disabled = false; }
});
