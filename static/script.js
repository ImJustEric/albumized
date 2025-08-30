// For when the website is loaded 
document.addEventListener('DOMContentLoaded', function () {
    // Allow for halves to change for albumized logo
    (async function populateLogo(){
        try {
        const [itemsResp, albumsResp] = await Promise.all([
            fetch('/static/images/items/manifest.json'),
            fetch('/static/images/album_covers/manifest.json')
        ]);
        if (!itemsResp.ok || !albumsResp.ok) return;
        const items = await itemsResp.json();
        const albums = await albumsResp.json();
        const pick = (arr) => arr[Math.floor(Math.random()*arr.length)];
        const left = pick(items);
        const right = pick(albums);
        const leftImg = document.querySelector('.logo-left');
        const rightImg = document.querySelector('.logo-right');
    const cb = `cb=${Date.now()}`; // reload image even if cached 
    if (leftImg && left) leftImg.src = `/static/images/items/${left}?${cb}`;
    if (rightImg && right) rightImg.src = `/static/images/album_covers/${right}?${cb}`;
        } catch (e) { /* silent */ }
    })();
    // Grab any images inputted and its name 
    const imageInput = document.getElementById('imageInput');
    const dropZone = document.getElementById('dropZone');
    const fileName = document.getElementById('fileName');

    dropZone.addEventListener('click', () => imageInput.click());
    // Keyboard support
    dropZone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); imageInput.click(); } });

    // Change file name when file is inputted 
    imageInput.addEventListener('change', () => {
        const f = imageInput.files[0];
        fileName.textContent = f ? f.name : 'No file chosen';
        const preview = document.getElementById('previewImg');
        if (preview && f) {
        const url = URL.createObjectURL(f);
        preview.src = url;
        preview.style.display = 'block';
        }
    });
    // Dragging image into input box 
    let dragCount = 0;

    dropZone.addEventListener('dragenter', (e) => { e.preventDefault(); dragCount++; dropZone.style.borderColor = '#9aa0b3'; });
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); });
    dropZone.addEventListener('dragleave', (e) => { e.preventDefault(); dragCount = Math.max(0, dragCount-1); if (dragCount === 0) dropZone.style.borderColor = '#d9dde6'; });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault(); dragCount = 0; dropZone.style.borderColor = '#d9dde6';
        const files = e.dataTransfer.files;
        if (files.length) {
        imageInput.files = files;
        fileName.textContent = files[0].name;
        const preview = document.getElementById('previewImg');
        if (preview) { preview.src = URL.createObjectURL(files[0]); preview.style.display = 'block'; }
        }
    });
    });