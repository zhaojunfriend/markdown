<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const API = '/api'

// Editor state
const source = ref('# Hello, Markdown!\n\nStart typing here...')
const filename = ref('untitled.md')
const files = ref([])
const statusMsg = ref('')
const statusType = ref('info') // 'info' | 'success' | 'error'
const previewMode = ref(false)

// Configure marked
marked.setOptions({ breaks: true, gfm: true })

// Live preview – rendered client-side for zero latency, sanitised to prevent XSS
const preview = computed(() => DOMPurify.sanitize(marked.parse(source.value)))

function notify(msg, type = 'info') {
  statusMsg.value = msg
  statusType.value = type
  setTimeout(() => { statusMsg.value = '' }, 3000)
}

async function fetchFiles() {
  try {
    const res = await fetch(`${API}/files`)
    files.value = await res.json()
  } catch {
    notify('Could not reach the backend server.', 'error')
  }
}

async function saveFile() {
  if (!filename.value.trim().endsWith('.md')) {
    filename.value = filename.value.trim() + '.md'
  }
  try {
    const res = await fetch(`${API}/files`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename: filename.value, content: source.value }),
    })
    if (!res.ok) {
      const err = await res.json()
      notify(err.detail || 'Save failed.', 'error')
      return
    }
    notify(`Saved "${filename.value}"`, 'success')
    await fetchFiles()
  } catch {
    notify('Save failed – check that the backend is running.', 'error')
  }
}

async function loadFile(name) {
  try {
    const res = await fetch(`${API}/files/${encodeURIComponent(name)}`)
    if (!res.ok) { notify('Load failed.', 'error'); return }
    const data = await res.json()
    source.value = data.content
    filename.value = data.filename
    notify(`Loaded "${name}"`, 'success')
  } catch {
    notify('Load failed – check that the backend is running.', 'error')
  }
}

async function deleteFile(name) {
  if (!confirm(`Delete "${name}"?`)) return
  try {
    const res = await fetch(`${API}/files/${encodeURIComponent(name)}`, { method: 'DELETE' })
    if (!res.ok) { notify('Delete failed.', 'error'); return }
    notify(`Deleted "${name}"`, 'success')
    if (filename.value === name) {
      source.value = ''
      filename.value = 'untitled.md'
    }
    await fetchFiles()
  } catch {
    notify('Delete failed – check that the backend is running.', 'error')
  }
}

function newFile() {
  source.value = ''
  filename.value = 'untitled.md'
}

onMounted(fetchFiles)
</script>

<template>
  <div class="app">
    <header>
      <span class="logo">📝 Markdown Editor</span>
      <div class="toolbar">
        <input
          v-model="filename"
          class="filename-input"
          placeholder="filename.md"
          @keyup.enter="saveFile"
        />
        <button @click="newFile">New</button>
        <button class="primary" @click="saveFile">Save</button>
        <button @click="previewMode = !previewMode">
          {{ previewMode ? 'Editor' : 'Preview' }}
        </button>
      </div>
      <div v-if="statusMsg" :class="['status', statusType]">{{ statusMsg }}</div>
    </header>

    <div class="main">
      <!-- Sidebar: file list -->
      <aside class="sidebar">
        <div class="sidebar-title">Saved Files</div>
        <ul>
          <li v-for="f in files" :key="f.filename" class="file-item">
            <span class="file-name" @click="loadFile(f.filename)">{{ f.filename }}</span>
            <button class="delete-btn" @click.stop="deleteFile(f.filename)" title="Delete">✕</button>
          </li>
          <li v-if="!files.length" class="empty-hint">No saved files yet</li>
        </ul>
      </aside>

      <!-- Editor pane -->
      <section v-if="!previewMode" class="editor-pane">
        <textarea
          v-model="source"
          class="editor"
          placeholder="Write your Markdown here…"
          spellcheck="false"
        ></textarea>
      </section>

      <!-- Preview pane -->
      <section class="preview-pane" :class="{ full: previewMode }">
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div class="preview" v-html="preview"></div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: system-ui, sans-serif;
}

header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 1rem;
  background: #1e1e2e;
  color: #cdd6f4;
  flex-wrap: wrap;
}

.logo {
  font-size: 1.2rem;
  font-weight: 700;
  white-space: nowrap;
}

.toolbar {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
  flex: 1;
}

.filename-input {
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  border: 1px solid #45475a;
  background: #313244;
  color: #cdd6f4;
  font-size: 0.9rem;
  width: 200px;
}

button {
  padding: 0.35rem 0.85rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  background: #45475a;
  color: #cdd6f4;
  transition: background 0.15s;
}
button:hover { background: #585b70; }
button.primary { background: #89b4fa; color: #1e1e2e; }
button.primary:hover { background: #b4d0ff; }

.status {
  font-size: 0.85rem;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
}
.status.success { background: #a6e3a1; color: #1e1e2e; }
.status.error   { background: #f38ba8; color: #1e1e2e; }
.status.info    { background: #89b4fa; color: #1e1e2e; }

.main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 200px;
  min-width: 160px;
  background: #181825;
  color: #cdd6f4;
  border-right: 1px solid #313244;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-title {
  padding: 0.6rem 0.8rem;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6c7086;
  border-bottom: 1px solid #313244;
}

ul { list-style: none; margin: 0; padding: 0; }

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.8rem;
  border-bottom: 1px solid #1e1e2e;
  gap: 0.4rem;
}
.file-item:hover { background: #313244; }

.file-name {
  font-size: 0.85rem;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.delete-btn {
  padding: 0.1rem 0.3rem;
  font-size: 0.7rem;
  background: transparent;
  color: #f38ba8;
}
.delete-btn:hover { background: #45475a; }

.empty-hint {
  padding: 0.8rem;
  font-size: 0.8rem;
  color: #6c7086;
}

.editor-pane {
  flex: 1;
  display: flex;
  overflow: hidden;
  border-right: 1px solid #313244;
}

.editor {
  flex: 1;
  resize: none;
  border: none;
  outline: none;
  padding: 1rem;
  font-family: 'Fira Code', 'Cascadia Code', monospace;
  font-size: 0.95rem;
  line-height: 1.6;
  background: #1e1e2e;
  color: #cdd6f4;
  tab-size: 2;
}

.preview-pane {
  flex: 1;
  overflow-y: auto;
  background: #fff;
}
.preview-pane.full { flex: 1; }

.preview {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  line-height: 1.7;
  font-size: 1rem;
  color: #333;
}

/* Basic markdown typography */
.preview :deep(h1),
.preview :deep(h2),
.preview :deep(h3),
.preview :deep(h4),
.preview :deep(h5),
.preview :deep(h6) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
  line-height: 1.25;
}
.preview :deep(h1) { font-size: 2em; border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
.preview :deep(h2) { font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
.preview :deep(p) { margin: 0.8em 0; }
.preview :deep(a) { color: #0366d6; text-decoration: none; }
.preview :deep(a:hover) { text-decoration: underline; }
.preview :deep(code) {
  background: #f6f8fa;
  padding: 0.15em 0.4em;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.9em;
}
.preview :deep(pre) {
  background: #f6f8fa;
  padding: 1em;
  border-radius: 6px;
  overflow-x: auto;
}
.preview :deep(pre code) { background: none; padding: 0; }
.preview :deep(blockquote) {
  border-left: 4px solid #dfe2e5;
  padding: 0.5em 1em;
  margin: 1em 0;
  color: #6a737d;
}
.preview :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}
.preview :deep(th),
.preview :deep(td) {
  border: 1px solid #dfe2e5;
  padding: 0.5em 1em;
}
.preview :deep(th) { background: #f6f8fa; font-weight: 600; }
.preview :deep(img) { max-width: 100%; }
.preview :deep(hr) { border: none; border-top: 1px solid #eee; margin: 2em 0; }
.preview :deep(ul),
.preview :deep(ol) { padding-left: 2em; }
</style>
