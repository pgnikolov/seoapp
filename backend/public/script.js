const API_URL = 'http://localhost:8000/analyze';

document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const urlInput = document.getElementById('urlInput');
    const url = urlInput.value.trim();
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const report = document.getElementById('report');
    
    // Reset UI
    loading.classList.remove('hidden');
    error.classList.add('hidden');
    report.classList.add('hidden');
    report.innerHTML = '';
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        renderReport(data);
        report.classList.remove('hidden');
    } catch (err) {
        error.textContent = `Грешка: ${err.message}`;
        error.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
    }
});

function renderReport(data) {
    const report = document.getElementById('report');
    const now = new Date();
    const dateStr = now.toLocaleString('bg-BG', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    let html = `
        <div class="report-header">
            <h2>Website Information Report</h2>
            <div class="url">${escapeHtml(data.url || data.final_url)}</div>
            <div class="date">Scan date: ${dateStr}</div>
        </div>
    `;
    
    // Overview Section
    html += `
        <div class="section">
            <h3 class="section-title">Overview</h3>
            <table>
                <tr>
                    <th>Domain</th>
                    <td>${escapeHtml(data.domain_and_infrastructure?.domain || 'Not detected')}</td>
                </tr>
                <tr>
                    <th>Domain Age (days)</th>
                    <td>${formatValue(data.domain_and_infrastructure?.domain_age_days)}</td>
                </tr>
                <tr>
                    <th>Registrar</th>
                    <td>${escapeHtml(data.domain_and_infrastructure?.registrar || 'Not detected')}</td>
                </tr>
                <tr>
                    <th>Expiry Date</th>
                    <td>${formatDate(data.domain_and_infrastructure?.expiry_date)}</td>
                </tr>
                <tr>
                    <th>IP Address</th>
                    <td>${escapeHtml(data.domain_and_infrastructure?.ip_address || 'Not detected')}</td>
                </tr>
                <tr>
                    <th>Web Server</th>
                    <td>${escapeHtml(data.domain_and_infrastructure?.web_server || 'Not detected')}</td>
                </tr>
                <tr>
                    <th>Server Location</th>
                    <td>${escapeHtml(data.domain_and_infrastructure?.server_location_country || 'Not detected')}</td>
                </tr>
                <tr>
                    <th>HTTP → HTTPS Redirect</th>
                    <td>${data.domain_and_infrastructure?.http_to_https_redirect ? 'Yes' : 'No'}</td>
                </tr>
            </table>
        </div>
    `;
    
    // Page Information Section
    html += `
        <div class="section">
            <h3 class="section-title">Page Information</h3>
            <table>
                <tr>
                    <th>Title</th>
                    <td>${escapeHtml(data.on_page_seo?.title || 'Not detected')}</td>
                </tr>
                <tr>
                    <th>Meta Description</th>
                    <td>${escapeHtml(data.on_page_seo?.meta_description || 'Not detected')}</td>
                </tr>
                <tr>
                    <th>Language</th>
                    <td>${escapeHtml(data.on_page_seo?.language || 'Not detected')}</td>
                </tr>
                <tr>
                    <th>Page Size</th>
                    <td>${formatBytes(data.on_page_seo?.page_size)}</td>
                </tr>
                <tr>
                    <th>Text Size</th>
                    <td>${formatBytes(data.on_page_seo?.text_size)}</td>
                </tr>
                <tr>
                    <th>Text-to-Code Ratio</th>
                    <td>${formatValue(data.on_page_seo?.text_to_code_ratio)}%</td>
                </tr>
            </table>
        </div>
    `;
    
    // Technologies Section
    html += `
        <div class="section">
            <h3 class="section-title">Technologies</h3>
    `;
    
    const tech = data.technology_detection || {};
    
    html += `
            <div class="subsection">
                <div class="subsection-title">CMS</div>
                <table>
                    <tr>
                        <th>Name</th>
                        <td>${escapeHtml(tech.cms || 'Not detected')}</td>
                    </tr>
                    <tr>
                        <th>Version</th>
                        <td>${escapeHtml(tech.cms_version || 'Not detected')}</td>
                    </tr>
                </table>
            </div>
    `;
    
    html += `
            <div class="subsection">
                <div class="subsection-title">Plugins</div>
                ${renderList(tech.plugins)}
            </div>
    `;
    
    html += `
            <div class="subsection">
                <div class="subsection-title">JavaScript Libraries</div>
                ${renderList(tech.javascript_libraries)}
            </div>
    `;
    
    html += `
            <div class="subsection">
                <div class="subsection-title">Cache Systems</div>
                ${renderList(tech.cache_systems)}
            </div>
    `;
    
    html += `
            <div class="subsection">
                <div class="subsection-title">CDN</div>
                <table>
                    <tr>
                        <th>CDN Provider</th>
                        <td>${escapeHtml(tech.cdn || 'Not detected')}</td>
                    </tr>
                </table>
            </div>
    `;
    
    html += `
            <div class="subsection">
                <div class="subsection-title">Tag Managers</div>
                ${renderList(tech.tag_managers)}
            </div>
    `;
    
    html += `
            <div class="subsection">
                <div class="subsection-title">HTTP/TLS</div>
                <table>
                    <tr>
                        <th>HTTP Version</th>
                        <td>${escapeHtml(tech.http_version || 'Not detected')}</td>
                    </tr>
                    <tr>
                        <th>TLS Version</th>
                        <td>${escapeHtml(tech.tls_version || 'Not detected')}</td>
                    </tr>
                </table>
            </div>
    `;
    
    html += `</div>`;
    
    // On-Page SEO Section
    html += `
        <div class="section">
            <h3 class="section-title">On-Page SEO</h3>
    `;
    
    // Headings
    const headings = data.on_page_seo?.headings || {};
    html += `
            <div class="subsection">
                <div class="subsection-title">Headings</div>
                <table>
                    <tr>
                        <th>H1</th>
                        <td>${formatValue(headings.h1?.count || 0)}</td>
                    </tr>
                    <tr>
                        <th>H2</th>
                        <td>${formatValue(headings.h2?.count || 0)}</td>
                    </tr>
                    <tr>
                        <th>H3</th>
                        <td>${formatValue(headings.h3?.count || 0)}</td>
                    </tr>
                    <tr>
                        <th>H4</th>
                        <td>${formatValue(headings.h4?.count || 0)}</td>
                    </tr>
                    <tr>
                        <th>H5</th>
                        <td>${formatValue(headings.h5?.count || 0)}</td>
                    </tr>
                    <tr>
                        <th>H6</th>
                        <td>${formatValue(headings.h6?.count || 0)}</td>
                    </tr>
                </table>
                ${renderHeadingContent(headings)}
            </div>
    `;
    
    // Links
    const links = data.on_page_seo?.links || {};
    html += `
            <div class="subsection">
                <div class="subsection-title">Links</div>
                <table>
                    <tr>
                        <th>Internal</th>
                        <td>${formatValue(links.internal)}</td>
                    </tr>
                    <tr>
                        <th>External</th>
                        <td>${formatValue(links.external)}</td>
                    </tr>
                    <tr>
                        <th>Nofollow</th>
                        <td>${formatValue(links.nofollow)}</td>
                    </tr>
                    <tr>
                        <th>Duplicated</th>
                        <td>${formatValue(links.duplicated)}</td>
                    </tr>
                </table>
            </div>
    `;
    
    // Images
    const images = data.on_page_seo?.images || {};
    html += `
            <div class="subsection">
                <div class="subsection-title">Images</div>
                <table>
                    <tr>
                        <th>Missing Alt</th>
                        <td>${formatValue(images.missing_alt)}</td>
                    </tr>
                    <tr>
                        <th>Duplicated</th>
                        <td>${formatValue(images.duplicated)}</td>
                    </tr>
                    <tr>
                        <th>With Title</th>
                        <td>${formatValue(images.with_title)}</td>
                    </tr>
                </table>
            </div>
    `;
    
    html += `</div>`;
    
    // Metadata Section
    html += `
        <div class="section">
            <h3 class="section-title">Metadata</h3>
    `;
    
    const metadata = data.metadata_and_structured_data || {};
    
    html += `
            <div class="subsection">
                <div class="subsection-title">Canonical</div>
                <table>
                    <tr>
                        <th>URL</th>
                        <td>${escapeHtml(metadata.canonical || 'Not detected')}</td>
                    </tr>
                </table>
            </div>
    `;
    
    html += `
            <div class="subsection">
                <div class="subsection-title">OpenGraph</div>
                ${renderKeyValueTable(metadata.open_graph)}
            </div>
    `;
    
    html += `
            <div class="subsection">
                <div class="subsection-title">Twitter Cards</div>
                ${renderKeyValueTable(metadata.twitter_cards)}
            </div>
    `;
    
    html += `
            <div class="subsection">
                <div class="subsection-title">Feeds</div>
                ${renderFeedList(metadata.feeds)}
            </div>
    `;
    
    html += `
            <div class="subsection">
                <div class="subsection-title">Robots Meta</div>
                <table>
                    <tr>
                        <th>Content</th>
                        <td>${escapeHtml(metadata.robots_meta || 'Not detected')}</td>
                    </tr>
                </table>
            </div>
    `;
    
    html += `</div>`;
    
    // Structured Data Section
    html += `
        <div class="section">
            <h3 class="section-title">Structured Data</h3>
            ${renderJSONLD(metadata.json_ld)}
        </div>
    `;
    
    // WHOIS Section
    html += `
        <div class="section">
            <h3 class="section-title">WHOIS Information</h3>
    `;
    
    const whois = data.whois_and_ip_whois || {};
    const domainWhois = whois.domain_whois || {};
    const ipWhois = whois.ip_whois || {};
    
    html += `
            <div class="subsection">
                <div class="subsection-title">Domain WHOIS</div>
                <table>
                    <tr>
                        <th>Registrar</th>
                        <td>${escapeHtml(domainWhois.registrar || 'Not detected')}</td>
                    </tr>
                    <tr>
                        <th>Creation Date</th>
                        <td>${formatDate(domainWhois.creation_date)}</td>
                    </tr>
                    <tr>
                        <th>Expiry Date</th>
                        <td>${formatDate(domainWhois.expiry_date)}</td>
                    </tr>
                    <tr>
                        <th>Status</th>
                        <td>${formatValue(domainWhois.status)}</td>
                    </tr>
                    <tr>
                        <th>Name Servers</th>
                        <td>${renderList(domainWhois.name_servers)}</td>
                    </tr>
                </table>
            </div>
    `;
    
    html += `
            <div class="subsection">
                <div class="subsection-title">IP WHOIS</div>
                <table>
                    <tr>
                        <th>IP Address</th>
                        <td>${escapeHtml(ipWhois.ip || 'Not detected')}</td>
                    </tr>
                    <tr>
                        <th>Hostname</th>
                        <td>${escapeHtml(ipWhois.hostname || 'Not detected')}</td>
                    </tr>
                    <tr>
                        <th>Organization</th>
                        <td>${escapeHtml(ipWhois.organization || 'Not detected')}</td>
                    </tr>
                    <tr>
                        <th>Country</th>
                        <td>${escapeHtml(ipWhois.country || 'Not detected')}</td>
                    </tr>
                </table>
            </div>
    `;
    
    html += `
            <div class="subsection">
                <div class="subsection-title">Same IP Websites</div>
                ${renderList(whois.same_ip_websites, 'None detected')}
            </div>
    `;
    
    html += `</div>`;
    
    report.innerHTML = html;
    
    // Setup collapsible handlers
    setupCollapsibles();
}

function renderList(items, emptyText = 'Not detected') {
    if (!items || !Array.isArray(items) || items.length === 0) {
        return `<div class="empty-list">${emptyText}</div>`;
    }
    return `<ul>${items.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`;
}

function renderKeyValueTable(obj) {
    if (!obj || typeof obj !== 'object' || Object.keys(obj).length === 0) {
        return '<div class="empty-list">Not detected</div>';
    }
    let html = '<table>';
    for (const [key, value] of Object.entries(obj)) {
        html += `
            <tr>
                <th>${escapeHtml(key)}</th>
                <td>${escapeHtml(value)}</td>
            </tr>
        `;
    }
    html += '</table>';
    return html;
}

function renderFeedList(feeds) {
    if (!feeds || !Array.isArray(feeds) || feeds.length === 0) {
        return '<div class="empty-list">Not detected</div>';
    }
    return `<ul>${feeds.map(feed => `<li><a href="${escapeHtml(feed)}" target="_blank">${escapeHtml(feed)}</a></li>`).join('')}</ul>`;
}

function renderHeadingContent(headings) {
    let hasContent = false;
    let content = '<div class="heading-content collapsible">';
    content += '<button class="collapsible-toggle" onclick="toggleCollapsible(this)">Show Heading Content</button>';
    content += '<div class="collapsible-content">';
    content += '<ul>';
    
    for (let i = 1; i <= 6; i++) {
        const tag = `h${i}`;
        const headingData = headings[tag];
        if (headingData && headingData.content && headingData.content.length > 0) {
            hasContent = true;
            headingData.content.forEach(text => {
                content += `<li><span class="heading-tag">${tag.toUpperCase()}:</span>${escapeHtml(text)}</li>`;
            });
        }
    }
    
    content += '</ul></div></div>';
    
    return hasContent ? content : '';
}

function renderJSONLD(jsonLd) {
    if (!jsonLd || !Array.isArray(jsonLd) || jsonLd.length === 0) {
        return '<div class="empty-list">Not detected</div>';
    }
    
    let html = '<div class="collapsible">';
    html += '<button class="collapsible-toggle" onclick="toggleCollapsible(this)">Show JSON-LD Data</button>';
    html += '<div class="collapsible-content">';
    html += '<pre>' + escapeHtml(JSON.stringify(jsonLd, null, 2)) + '</pre>';
    html += '</div></div>';
    
    return html;
}

function toggleCollapsible(button) {
    const content = button.nextElementSibling;
    content.classList.toggle('active');
    button.textContent = content.classList.contains('active') ? 'Hide Content' : 'Show Content';
}

window.toggleCollapsible = toggleCollapsible;

function setupCollapsibles() {
    // Already handled by onclick in HTML
}

function escapeHtml(text) {
    if (text === null || text === undefined) {
        return 'Not detected';
    }
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatValue(value) {
    if (value === null || value === undefined || value === '') {
        return '<span class="not-detected">Not detected</span>';
    }
    return escapeHtml(String(value));
}

function formatDate(dateStr) {
    if (!dateStr) {
        return '<span class="not-detected">Not detected</span>';
    }
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('bg-BG', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch {
        return escapeHtml(dateStr);
    }
}

function formatBytes(bytes) {
    if (!bytes && bytes !== 0) {
        return '<span class="not-detected">Not detected</span>';
    }
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

