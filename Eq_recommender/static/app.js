const tabs = document.querySelectorAll('nav button');
const sections = document.querySelectorAll('main .tab');

tabs.forEach(btn => {
  btn.addEventListener('click', () => {
    sections.forEach(s => s.classList.remove('active'));
    document.getElementById(btn.dataset.tab).classList.add('active');
  });
});

const kategoriSelect = document.getElementById('kategori');
const alatList = document.getElementById('alat-list');
const formAlat = document.getElementById('form-alat');
const resetFormBtn = document.getElementById('reset-form');
const rekomList = document.getElementById('rekom-results');

async function fetchCategories() {
  const res = await fetch('/api/categories');
  const data = await res.json();
  kategoriSelect.innerHTML = data.map(c => `<option value="${c.id_kategori}">${c.nama_kategori}</option>`).join('');
}

async function fetchAlats() {
  const res = await fetch('/api/alats');
  const data = await res.json();
  alatList.innerHTML = data.map(renderAlatCard).join('');
  attachCardEvents();
}

function renderAlatCard(item) {
  const payload = encodeURIComponent(JSON.stringify(item));
  return `<div class="card-item" data-id="${item.id_alat}" data-json="${payload}">
    <div class="badge">${item.kategori || 'N/A'}</div>
    <h3>${item.nama_alat}</h3>
    <p>${item.deskripsi || ''}</p>
    <p><strong>Kebutuhan:</strong> ${item.kebutuhan_konten || '-'}</p>
    <p class="price">Rp ${item.harga_sewa}/hari</p>
    <p>Stok: ${item.stok} | Rating: ${item.rating_alat ?? 0}</p>
    <div class="actions-inline">
      <button class="edit">Edit</button>
      <button class="delete" style="background:#ef4444;border-color:#ef4444;">Hapus</button>
    </div>
  </div>`;
}

function attachCardEvents() {
  document.querySelectorAll('.card-item .edit').forEach(btn => {
    btn.onclick = () => {
      const card = btn.closest('.card-item');
      const id = card.dataset.id;
      const item = JSON.parse(decodeURIComponent(card.dataset.json || '{}'));
      document.getElementById('alat-id').value = id;
      document.getElementById('nama-alat').value = item.nama_alat || '';
      document.getElementById('kategori').value = item.id_kategori;
      document.getElementById('deskripsi').value = item.deskripsi || '';
      document.getElementById('kebutuhan').value = item.kebutuhan_konten || '';
      document.getElementById('harga').value = item.harga_sewa || 0;
      document.getElementById('stok').value = item.stok || 0;
      document.getElementById('rating').value = item.rating_alat || 0;
      document.getElementById('gambar').value = item.gambar || '';
    };
  });
  document.querySelectorAll('.card-item .delete').forEach(btn => {
    btn.onclick = async () => {
      const id = btn.closest('.card-item').dataset.id;
      if (!confirm('Hapus alat ini?')) return;
      await fetch(`/api/alats/${id}`, { method: 'DELETE' });
      fetchAlats();
    };
  });
}

formAlat.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    id_kategori: Number(kategoriSelect.value),
    nama_alat: document.getElementById('nama-alat').value,
    deskripsi: document.getElementById('deskripsi').value,
    kebutuhan_konten: document.getElementById('kebutuhan').value,
    harga_sewa: Number(document.getElementById('harga').value || 0),
    stok: Number(document.getElementById('stok').value || 0),
    rating_alat: Number(document.getElementById('rating').value || 0),
    gambar: document.getElementById('gambar').value,
  };
  const id = document.getElementById('alat-id').value;
  const method = id ? 'PUT' : 'POST';
  const url = id ? `/api/alats/${id}` : '/api/alats';
  await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  formAlat.reset();
  fetchAlats();
});

resetFormBtn.addEventListener('click', () => formAlat.reset());

const formRekom = document.getElementById('form-rekom');
formRekom.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    jenis_konten: document.getElementById('jenis-konten').value,
    deskripsi_konten: document.getElementById('deskripsi-konten').value,
    budget: Number(document.getElementById('budget').value || 0),
    lokasi: document.getElementById('lokasi').value,
  };
  const res = await fetch('/api/recommend', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  rekomList.innerHTML = data.map(r => `<div class="card-item">
      <div class="badge">${r.alat.kategori || ''}</div>
      <h3>${r.alat.nama_alat}</h3>
      <p>${r.alat.deskripsi || ''}</p>
      <p><strong>Kebutuhan:</strong> ${r.alat.kebutuhan_konten || '-'}</p>
      <p class="price">Rp ${r.alat.harga_sewa}/hari</p>
      <p>Skor: ${r.skor.toFixed(2)} | Sim: ${r.sim.toFixed(2)} | Overlap: ${r.overlap.toFixed(2)}</p>
    </div>`).join('');
  sections.forEach(s => s.classList.remove('active'));
  document.getElementById('rekom').classList.add('active');
});

fetchCategories().then(fetchAlats);
