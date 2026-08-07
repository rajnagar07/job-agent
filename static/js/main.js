// AI Job Agent — shared front-end behavior

document.addEventListener('DOMContentLoaded', () => {

  // Mobile nav toggle
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', navLinks.classList.contains('open'));
    });
  }

  // Dismissible alerts
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => btn.closest('.alert')?.remove());
  });

  // Password show/hide toggles: <button class="input-toggle" data-target="#id">
  document.querySelectorAll('.input-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const targets = (btn.dataset.target || '').split(',').map(s => s.trim()).filter(Boolean);
      let anyHidden = false;
      targets.forEach(sel => {
        const input = document.querySelector(sel);
        if (input && input.type === 'password') anyHidden = true;
      });
      targets.forEach(sel => {
        const input = document.querySelector(sel);
        if (!input) return;
        input.type = anyHidden ? 'text' : 'password';
      });
      btn.textContent = anyHidden ? 'Hide' : 'Show';
    });
  });

  // Dropzone + file chip: <div class="dropzone"><input type="file"><div class="file-chip">
  document.querySelectorAll('.dropzone').forEach(zone => {
    const input = zone.querySelector('input[type=file]');
    const chip = zone.querySelector('.file-chip');
    if (!input || !chip) return;

    // Clicking to choose a file fires this natively.
    input.addEventListener('change', () => {
      if (input.files.length) {
        chip.textContent = '✓ ' + input.files[0].name;
        chip.classList.add('show');
      }
    });

    ['dragover', 'dragenter'].forEach(evt =>
      zone.addEventListener(evt, e => { e.preventDefault(); zone.classList.add('is-dragover'); }));

    zone.addEventListener('dragleave', e => { e.preventDefault(); zone.classList.remove('is-dragover'); });

    // Dropping a file onto the zone: the file input sits on top of the zone,
    // but calling preventDefault() here (required to allow a drop at all)
    // cancels the input's native "assign dropped file" behavior. So assign
    // the dropped file to the input manually and fire 'change' ourselves.
    zone.addEventListener('drop', e => {
      e.preventDefault();
      zone.classList.remove('is-dragover');
      const dt = e.dataTransfer;
      if (!dt || !dt.files || !dt.files.length) return;
      try {
        input.files = dt.files;
      } catch (err) {
        const clone = new DataTransfer();
        clone.items.add(dt.files[0]);
        input.files = clone.files;
      }
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });
  });

  // Forms that should show the full-screen loading overlay on submit:
  // <form data-loading> ... </form>  +  <div class="loading-overlay" id="loadingOverlay">
  document.querySelectorAll('form[data-loading]').forEach(form => {
    form.addEventListener('submit', () => {
      document.getElementById('loadingOverlay')?.classList.add('show');
    });
  });

  // Animated bar fills: <div class="bar-fill" data-width="72">
  document.querySelectorAll('.bar-fill[data-width]').forEach(bar => {
    const w = bar.getAttribute('data-width');
    requestAnimationFrame(() => { bar.style.width = w + '%'; });
  });

  // FAQ accordion: <button class="faq-q" data-faq> / <div class="faq-a">
  document.querySelectorAll('[data-faq]').forEach(q => {
    q.addEventListener('click', () => {
      const item = q.closest('.faq-item');
      item?.classList.toggle('open');
    });
  });
});
