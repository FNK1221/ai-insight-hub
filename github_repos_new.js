// ===== GitHub Trending Repos =====
(function() {
  const grid = document.getElementById('repoGrid');
  const loadMoreBtn = document.getElementById('repoLoadMore');
  let currentQuery = 'topic:ai+topic:llm';
  let showCount = 12;
  let allCategoriesData = null;
  const DATA_URL = 'data/github-repos.json';

  const langColors = {
    'Python':'#3572A5','JavaScript':'#f1e05a','TypeScript':'#3178c6','Rust':'#dea584',
    'C++':'#f34b7d','C':'#555555','Go':'#00ADD8','Java':'#b07219','Jupyter Notebook':'#DA5B0B',
    'Shell':'#89e051','Lua':'#000080','Swift':'#F05138','Kotlin':'#A97BFF','Ruby':'#701516',
    'CSS':'#563d7c','HTML':'#e34c26','Dart':'#00B4AB','Zig':'#ec915c','Julia':'#9558B2',
    'R':'#198CE7','Scala':'#c22d40','Elixir':'#6e4a7e','Clojure':'#db5855'
  };

  function formatStars(n) {
    if (n >= 1000) return (n/1000).toFixed(1) + 'k';
    return n.toString();
  }

  function timeAgo(dateStr) {
    if (!dateStr) return '';
    const diff = Date.now() - new Date(dateStr).getTime();
    const days = Math.floor(diff / 86400000);
    if (days === 0) return '今天';
    if (days === 1) return '昨天';
    if (days < 30) return days + '天前';
    if (days < 365) return Math.floor(days/30) + '个月前';
    return Math.floor(days/365) + '年前';
  }

  function renderRepo(repo) {
    const langColor = langColors[repo.language] || '#8b5cf6';
    const topics = (repo.topics || []).slice(0, 4).map(t =>
      `<span class="repo-topic">${t}</span>`
    ).join('');
    const repoName = repo.full_name || repo.name || '';
    const displayName = repoName.includes('/') ? repoName.split('/')[1] : repoName;

    return `
      <div class="repo-card">
        <div class="repo-card-top">
          <span class="repo-lang-dot" style="background:${langColor}"></span>
          <a class="repo-name" href="${repo.html_url}" target="_blank" title="${repoName}">${displayName}</a>
        </div>
        <div class="repo-desc">${repo.description || '暂无描述'}</div>
        <div class="repo-stats">
          <span class="repo-stat repo-stars">&#9733; ${formatStars(repo.stargazers_count)}</span>
          <span class="repo-stat repo-forks">&#128278; ${formatStars(repo.forks_count)}</span>
          <span class="repo-stat">${repo.language || '—'}</span>
          <span class="repo-stat">更新 ${timeAgo(repo.pushed_at)}</span>
        </div>
        ${topics ? `<div class="repo-topics">${topics}</div>` : ''}
      </div>
    `;
  }

  function getFallbackRepos() {
    return [
      { full_name: 'deepseek-ai/DeepSeek-V3', html_url: 'https://github.com/deepseek-ai/DeepSeek-V3', description: 'DeepSeek-V3: A Strong, Economical, and Efficient Mixture-of-Experts Language Model', stargazers_count: 42000, forks_count: 5600, language: 'Python', pushed_at: '2026-05-28T10:00:00Z', topics: ['llm','ai','moe'] },
      { full_name: 'deepseek-ai/DeepSeek-R1', html_url: 'https://github.com/deepseek-ai/DeepSeek-R1', description: 'DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning', stargazers_count: 38000, forks_count: 4900, language: 'Python', pushed_at: '2026-05-27T10:00:00Z', topics: ['llm','ai','reasoning'] },
      { full_name: 'langgenius/dify', html_url: 'https://github.com/langgenius/dify', description: 'Dify is an open-source LLM app development platform.', stargazers_count: 62000, forks_count: 8800, language: 'TypeScript', pushed_at: '2026-05-28T08:00:00Z', topics: ['ai','agent','llm'] },
      { full_name: 'ollama/ollama', html_url: 'https://github.com/ollama/ollama', description: 'Get up and running with Llama 3, Mistral, and other large language models.', stargazers_count: 98000, forks_count: 7200, language: 'Go', pushed_at: '2026-05-28T06:00:00Z', topics: ['ai','llm','local'] },
      { full_name: 'openai/whisper', html_url: 'https://github.com/openai/whisper', description: 'Robust Speech Recognition via Large-Scale Weak Supervision', stargazers_count: 73000, forks_count: 8600, language: 'Python', pushed_at: '2026-05-20T10:00:00Z', topics: ['ai','speech','asr'] },
      { full_name: 'comfyanonymous/ComfyUI', html_url: 'https://github.com/comfyanonymous/ComfyUI', description: 'The most powerful and modular diffusion model GUI and backend.', stargazers_count: 58000, forks_count: 6200, language: 'Python', pushed_at: '2026-05-28T09:00:00Z', topics: ['ai','diffusion','comfyui'] },
      { full_name: 'langchain-ai/langchain', html_url: 'https://github.com/langchain-ai/langchain', description: 'Build context-aware reasoning applications', stargazers_count: 95000, forks_count: 15200, language: 'Python', pushed_at: '2026-05-28T07:00:00Z', topics: ['ai','llm','rag'] },
      { full_name: 'huggingface/transformers', html_url: 'https://github.com/huggingface/transformers', description: 'State-of-the-art Machine Learning for PyTorch, TensorFlow, and JAX', stargazers_count: 138000, forks_count: 27600, language: 'Python', pushed_at: '2026-05-28T11:00:00Z', topics: ['ai','nlp','transformers'] },
      { full_name: 'n8n-io/n8n', html_url: 'https://github.com/n8n-io/n8n', description: 'Fair-code workflow automation platform with native AI capabilities.', stargazers_count: 72400, forks_count: 15200, language: 'TypeScript', pushed_at: '2026-05-26T00:00:00Z', topics: ['automation','workflow','ai'] },
      { full_name: 'lobehub/lobe-chat', html_url: 'https://github.com/lobehub/lobe-chat', description: 'Lobe Chat - an open-source, modern-design AI chat framework.', stargazers_count: 64200, forks_count: 8800, language: 'TypeScript', pushed_at: '2026-05-28T00:00:00Z', topics: ['chatbot','llm','ai'] },
      { full_name: 'open-webui/open-webui', html_url: 'https://github.com/open-webui/open-webui', description: 'User-friendly AI Interface (Supports Ollama, OpenAI API, ...)', stargazers_count: 85800, forks_count: 12400, language: 'Python', pushed_at: '2026-05-27T00:00:00Z', topics: ['llm','ollama','chatgpt'] },
      { full_name: 'Mintplex-Labs/anything-llm', html_url: 'https://github.com/Mintplex-Labs/anything-llm', description: 'The all-in-one Desktop & Docker AI application with full RAG and AI Agent capabilities.', stargazers_count: 42800, forks_count: 5600, language: 'JavaScript', pushed_at: '2026-05-23T00:00:00Z', topics: ['llm','rag','ai'] }
    ];
  }

  function displayRepos(items, count) {
    grid.innerHTML = '';
    const visible = items.slice(0, count);
    visible.forEach(repo => grid.insertAdjacentHTML('beforeend', renderRepo(repo)));
    if (items.length > count) {
      loadMoreBtn.style.display = 'inline-block';
      loadMoreBtn.disabled = false;
      loadMoreBtn.textContent = '加载更多 (' + count + '/' + items.length + ')';
    } else {
      loadMoreBtn.style.display = 'none';
    }
  }

  function switchCategory(queryKey) {
    currentQuery = queryKey;
    showCount = 12;
    if (allCategoriesData && allCategoriesData.categories && allCategoriesData.categories[queryKey]) {
      const cat = allCategoriesData.categories[queryKey];
      displayRepos(cat.items, showCount);
      if (allCategoriesData.timestamp) {
        const ts = new Date(allCategoriesData.timestamp);
        const dateStr = ts.toLocaleDateString('zh-CN', { year:'numeric', month:'long', day:'numeric', hour:'2-digit', minute:'2-digit' });
        document.getElementById('lastUpdate').textContent = '最近更新：' + dateStr;
      }
    } else {
      displayRepos(getFallbackRepos(), 12);
    }
  }

  async function loadStaticData() {
    grid.innerHTML = '<div class="repo-loading"><div class="spinner"></div><div>正在加载热门项目...</div></div>';
    try {
      const resp = await fetch(DATA_URL);
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      allCategoriesData = await resp.json();
      console.log('[GitHub Repos] Loaded ' + Object.keys(allCategoriesData.categories).length + ' categories from ' + DATA_URL);
      switchCategory(currentQuery);
    } catch (err) {
      console.warn('[GitHub Repos] Failed to load static JSON:', err.message);
      grid.innerHTML = '';
      displayRepos(getFallbackRepos(), 12);
      grid.insertAdjacentHTML('beforeend',
        '<div style="text-align:center;padding:12px;font-size:12px;color:var(--text-muted);grid-column:1/-1;">&#9888; 数据文件加载失败，显示缓存推荐</div>');
    }
  }

  document.querySelectorAll('.repo-cat-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.repo-cat-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      switchCategory(btn.dataset.query);
    });
  });

  loadMoreBtn.addEventListener('click', () => {
    showCount += 12;
    if (allCategoriesData && allCategoriesData.categories[currentQuery]) {
      const items = allCategoriesData.categories[currentQuery].items;
      displayRepos(items, showCount);
    }
  });

  loadStaticData();
})();
