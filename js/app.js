// Fewly Repo - Dopamine Jailbreak Client Engine
document.addEventListener('DOMContentLoaded', () => {
  const REPO_URL = 'https://fewly11.github.io/';
  let allPackages = [];
  let currentCategory = 'all';
  let searchQuery = '';

  const packagesContainer = document.getElementById('packageGrid');
  const searchInput = document.getElementById('searchInput');
  const countBadge = document.getElementById('packageCount');
  const toast = document.getElementById('toastNotice');
  const copyBtns = document.querySelectorAll('.copy-repo-btn');

  // Copy Repo URL
  copyBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      navigator.clipboard.writeText(REPO_URL).then(() => {
        showToast('Đã sao chép link nguồn: ' + REPO_URL);
      }).catch(() => {
        // Fallback
        const temp = document.createElement('input');
        temp.value = REPO_URL;
        document.body.appendChild(temp);
        temp.select();
        document.execCommand('copy');
        document.body.removeChild(temp);
        showToast('Đã sao chép link nguồn: ' + REPO_URL);
      });
    });
  });

  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2800);
  }

  // Load Packages (busting browser cache with timestamp)
  fetch('packages.json?t=' + Date.now())
    .then(res => res.json())
    .then(data => {
      allPackages = data;
      renderPackages();
    })
    .catch(err => {
      console.warn('Could not fetch packages.json, rendering fallback message', err);
      // If fetched over file:// or error, fallback to embedded/static
      if (window.__STATIC_PACKAGES__) {
        allPackages = window.__STATIC_PACKAGES__;
        renderPackages();
      }
    });

  // Search input
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      renderPackages();
    });
  }

  // Category filter
  const categoryChips = document.querySelectorAll('.chip');
  categoryChips.forEach(chip => {
    chip.addEventListener('click', () => {
      categoryChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentCategory = chip.getAttribute('data-cat') || 'all';
      renderPackages();
    });
  });

  function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  function renderPackages() {
    if (!packagesContainer) return;

    const filtered = allPackages.filter(pkg => {
      const matchSearch = !searchQuery || 
        (pkg.name && pkg.name.toLowerCase().includes(searchQuery)) ||
        (pkg.package && pkg.package.toLowerCase().includes(searchQuery)) ||
        (pkg.author && pkg.author.toLowerCase().includes(searchQuery)) ||
        (pkg.description && pkg.description.toLowerCase().includes(searchQuery));

      if (!matchSearch) return false;

      if (currentCategory === 'all') return true;
      if (currentCategory === 'media') {
        const n = (pkg.name + ' ' + pkg.package).toLowerCase();
        return n.includes('youtube') || n.includes('cercube') || n.includes('pip') || n.includes('tiktok');
      }
      if (currentCategory === 'games') {
        const n = (pkg.name + ' ' + pkg.package).toLowerCase();
        return n.includes('game') || n.includes('lienquan') || n.includes('pubg') || n.includes('freefire') || n.includes('mlbb') || n.includes('60fps');
      }
      if (currentCategory === 'tools') {
        const n = (pkg.name + ' ' + pkg.package).toLowerCase();
        return n.includes('app') || n.includes('bypass') || n.includes('choicy') || n.includes('hack') || n.includes('vpn') || n.includes('term');
      }
      return true;
    });

    if (countBadge) {
      countBadge.textContent = `${filtered.length} tweak`;
    }

    if (filtered.length === 0) {
      packagesContainer.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 40px 20px; color: var(--text-dim);">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 12px; opacity: 0.5;">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <p>Không tìm thấy tweak nào khớp với từ khóa "${searchQuery}".</p>
        </div>
      `;
      return;
    }

    packagesContainer.innerHTML = filtered.map(pkg => {
      const authorText = pkg.author ? pkg.author.replace(/<.*?>/, '').trim() : 'Fewly';
      return `
        <div class="package-card">
          <div class="pkg-top">
            <div class="pkg-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
            </div>
            <div class="pkg-info">
              <div class="pkg-title-row">
                <span class="pkg-title" title="${pkg.name}">${pkg.name}</span>
                <span class="pkg-version">v${pkg.version || '1.0'}</span>
              </div>
              <div class="pkg-author">Tác giả: ${authorText}</div>
            </div>
          </div>

          <div class="pkg-desc">${pkg.description || 'Tiện ích hỗ trợ Jailbreak iPhone iOS'}</div>

          <div class="pkg-meta">
            <span class="badge-dopamine">Dopamine Ready</span>
            <span class="badge-size">${formatBytes(pkg.size || 0)}</span>
          </div>

          <div class="pkg-actions">
            <a href="${pkg.filename}" class="btn-pkg-download" download title="Tải file deb về máy">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              Tải .deb
            </a>
            <a href="sileo://package/${pkg.package}" class="btn-pkg-sileo" title="Mở gói trong Sileo">
              Sileo
            </a>
          </div>
        </div>
      `;
    }).join('');
  }

  // Music Player Controller
  const audio = document.getElementById('bgAudio');
  const playBtn = document.getElementById('musicPlayBtn');
  const playIcon = document.getElementById('playIcon');
  const pauseIcon = document.getElementById('pauseIcon');
  const waveBars = document.getElementById('waveBars');

  if (audio && playBtn) {
    playBtn.addEventListener('click', () => {
      if (audio.paused) {
        audio.play().then(() => {
          updateAudioUI(true);
        }).catch(err => {
          console.warn('Playback error or blocked by browser:', err);
        });
      } else {
        audio.pause();
        updateAudioUI(false);
      }
    });

    audio.addEventListener('ended', () => {
      updateAudioUI(false);
    });

    function updateAudioUI(isPlaying) {
      if (isPlaying) {
        playIcon.style.display = 'none';
        pauseIcon.style.display = 'block';
        if (waveBars) waveBars.classList.add('playing');
      } else {
        playIcon.style.display = 'block';
        pauseIcon.style.display = 'none';
        if (waveBars) waveBars.classList.remove('playing');
      }
    }
  }
});
