document.addEventListener('DOMContentLoaded', () => {
    // --- 1. LOGIKA PINDAH TAB (SPA FEEL) ---
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Hapus kelas active dari semua tab & konten
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            
            // Tambahkan kelas active ke tab yang diklik
            tab.classList.add('active');
            const targetId = `tab-${tab.dataset.tab}`;
            document.getElementById(targetId).classList.add('active');
        });
    });

    // --- 2. SISTEM GANTI SKIN (3 TEMA LUXURY) ---
    const skins = ['skin-emerald', 'skin-midnight', 'skin-paper'];
    let currentSkinIndex = 0;
    
    document.getElementById('theme-toggle').addEventListener('click', () => {
        // Hapus skin lama dari body
        document.body.classList.remove(skins[currentSkinIndex]);
        
        // Pindah ke skin berikutnya (looping)
        currentSkinIndex = (currentSkinIndex + 1) % skins.length;
        document.body.classList.add(skins[currentSkinIndex]);
        
        logToPanel(`🎨 Tema diganti ke: ${skins[currentSkinIndex].replace('skin-', '').toUpperCase()}`);
    });

    // --- 3. FITUR COPY REPORT DENGAN FEEDBACK VISUAL ---
    // Fungsi ini dipanggil langsung dari HTML via onclick="copyReport(this, '...')"
    window.copyReport = function(btnElement, reportText) {
        navigator.clipboard.writeText(reportText).then(() => {
            const originalText = btnElement.innerText;
            
            // Ubah tampilan tombol saat berhasil copy
            btnElement.innerText = '✓ COPIED TO CLIPBOARD!';
            btnElement.classList.add('copied'); // Mengaktifkan CSS .action-btn.copied
            
            // Kembalikan ke semula setelah 2 detik
            setTimeout(() => {
                btnElement.innerText = originalText;
                btnElement.classList.remove('copied');
            }, 2000);
            
            logToPanel('📋 Laporan bug berhasil disalin ke clipboard!');
        }).catch(err => {
            console.error('Gagal menyalin:', err);
            alert('Gagal menyalin. Pastikan Anda membuka dashboard via HTTPS.');
        });
    };

    // --- 4. FORCE RE-SCAN VIA GITHUB ACTIONS API ---
    document.getElementById('force-rescan').addEventListener('click', async function() {
        const btn = this;
        const originalHTML = btn.innerHTML;
        
        // Ubah tombol jadi loading state
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> SCANNING...';
        btn.disabled = true;
        
        try {
            // CATATAN PENTING: Token harus disimpan di Environment Variables Vercel/Netlify
            // Jangan hardcode token di sini demi keamanan!
            const ghToken = import.meta.env.VITE_GH_TOKEN || localStorage.getItem('gh_token_temp'); 
            
            if (!ghToken) {
                throw new Error('GitHub Token tidak ditemukan. Silakan setup ENV variables.');
            }

            const response = await fetch(
                'https://api.github.com/repos/77t/ai-bounty-hunter-core/actions/workflows/hunt.yml/dispatches', 
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `token ${ghToken}`, 
                        'Accept': 'application/vnd.github.v3+json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ ref: 'main' })
                }
            );
            
            if (response.ok || response.status === 204) {
                logToPanel('✅ Perintah FORCE RE-SCAN berhasil dikirim ke server!');
            } else {
                throw new Error(`API Error: ${response.status}`);
            }
        } catch(e) {
            logToPanel(`❌ Gagal trigger scan: ${e.message}`);
        } finally {
            // Kembalikan tombol ke kondisi semula setelah 3 detik
            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.disabled = false;
            }, 3000);
        }
    });

    // --- 5. RENDER STATUS 10 AKUN FISIK (MOCK DATA) ---
    // Nanti bagian ini diganti dengan fetch real-time dari Supabase
    function renderAccountStatus() {
        const accGrid = document.getElementById('account-status-grid');
        if (!accGrid) return;

        let htmlContent = '';
        // Simulasi 10 akun dengan status acak
        for(let i = 1; i <= 10; i++) {
            const isSuccess = Math.random() > 0.3; // 70% peluang sukses
            const statusText = isSuccess ? '✅ Sukses' : '⚠️ WAF Block';
            const textColor = isSuccess ? '#10b981' : '#ef4444';
            
            htmlContent += `
                <div class="acc-item" style="color:${textColor}; font-weight:600;">
                    Akun ${i}<br>
                    <span style="font-size:0.65rem; opacity:0.8">${statusText}</span>
                </div>
            `;
        }
        accGrid.innerHTML = htmlContent;
    }

    // --- FUNGSI UTILITAS: LIVE LOG PANEL ---
    function logToPanel(message) {
        const logBox = document.getElementById('live-log');
        if (!logBox) return;
        
        const time = new Date().toLocaleTimeString('id-ID', { hour12: false });
        const logEntry = document.createElement('div');
        logEntry.innerHTML = `<span style="opacity:0.6">[${time}]</span> ${message}`;
        
        logBox.appendChild(logEntry);
        logBox.scrollTop = logBox.scrollHeight; // Auto scroll ke bawah
        
        // Batasi log maksimal 50 baris agar tidak berat di HP
        if (logBox.children.length > 50) {
            logBox.removeChild(logBox.firstChild);
        }
    }

    // --- INISIALISASI SAAT LOAD PERTAMA ---
    renderAccountStatus();
    logToPanel('🚀 AI Bounty Hunter Dashboard v1.0 Initialized');
    logToPanel('🛡️ Sistem keamanan aktif. Menunggu perintah...');
});
                                                             
