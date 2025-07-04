// frontend/app.js
document.getElementById('start-btn').addEventListener('click', () => {
  const lonMin  = parseFloat(document.getElementById('lonMin').value);
  const latMin  = parseFloat(document.getElementById('latMin').value);
  const lonMax  = parseFloat(document.getElementById('lonMax').value);
  const latMax  = parseFloat(document.getElementById('latMax').value);
  const start   = document.getElementById('start').value;
  const end     = document.getElementById('end').value;
  const zoom    = document.getElementById('zoom').value;
  const workers = document.getElementById('workers').value;

  if ( [lonMin,latMin,lonMax,latMax].some(isNaN) || !start || !end ) {
    alert('Please fill in all bounding-box and time fields.');
    return;
  }

  // Build the query string
  const params = new URLSearchParams({
    lon_min:    lonMin,
    lat_min:    latMin,
    lon_max:    lonMax,
    lat_max:    latMax,
    start_iso:  new Date(start).toISOString(),
    end_iso:    new Date(end).toISOString(),
    zoom,
    max_workers: workers
  });

  const btn = document.getElementById('start-btn');
  btn.disabled = true;

  const progBar  = document.getElementById('progress-bar');
  const progTxt  = document.getElementById('progress-text');
  const progCon  = document.getElementById('progress-container');
  const videoElt = document.getElementById('output-video');

  progCon.style.display = 'block';
  progBar.style.width   = '0%';
  progTxt.textContent   = 'Initializing…';
  videoElt.style.display= 'none';
  videoElt.src          = '';

  // Open EventSource GET to /interpolate/stream
  const evtSrc = new EventSource(`/interpolate/stream?${params}`);

  evtSrc.onmessage = e => {
    const data = JSON.parse(e.data);
    progBar.style.width = data.progress + '%';
    progTxt.textContent = `${data.message} (${data.progress}%)`;
    if (data.video_url) {
      videoElt.src = data.video_url;
      videoElt.style.display = 'block';
      btn.disabled = false;
      evtSrc.close();
    }
  };

  evtSrc.onerror = () => {
    progTxt.textContent = 'Stream error';
    btn.disabled = false;
    evtSrc.close();
  };
});
