<script lang="ts">
  import { onMount } from 'svelte';
  import { settingsStore } from '$lib/stores/settingsStore';
  import { invoke } from '@tauri-apps/api/core';
  import { save, open } from '@tauri-apps/plugin-dialog';

  interface Settings {
    claudeWorkspaceDir: string;
    databaseFilePath: string;
    databaseBackupEnabled: boolean;
    keepConversationPrompts: boolean;
    defaultClaudeModel: string;
  }

  interface DbInfo {
    path: string;
    sizeBytes: number;
    sizeMb: number;
    lastModified: string | null;
    backups: BackupInfo[];
  }

  interface BackupInfo {
    path: string;
    filename: string;
    sizeBytes: number;
    sizeMb: number;
    createdAt: string | null;
  }

  let settings = $state<Settings>({
    claudeWorkspaceDir: '',
    databaseFilePath: '',
    databaseBackupEnabled: true,
    keepConversationPrompts: true,
    defaultClaudeModel: 'sonnet'
  });
  let loading = $state(true);
  let saving = $state(false);
  let message = $state<{ type: 'success' | 'error'; text: string } | null>(null);

  // 트레이 설정 (로컬 저장)
  let minimizeToTray = $state(false);

  // DB 관리
  let dbInfo = $state<DbInfo | null>(null);
  let loadingDbInfo = $state(false);
  let dbMessage = $state<{ type: 'success' | 'error'; text: string } | null>(null);

  async function loadSettings() {
    try {
      loading = true;
      settings = await invoke<Settings>('get_settings');
    } catch (err) {
      console.error('Failed to load settings:', err);
      message = { type: 'error', text: '설정을 불러오는데 실패했습니다.' };
    } finally {
      loading = false;
    }
  }

  async function saveSettings() {
    try {
      saving = true;
      message = null;

      await invoke('update_settings', { settings });

      message = { type: 'success', text: '설정이 저장되었습니다.' };

      // 3초 후 메시지 제거
      setTimeout(() => {
        message = null;
      }, 3000);
    } catch (err: any) {
      console.error('Failed to save settings:', err);
      message = { type: 'error', text: err || '설정 저장에 실패했습니다.' };
    } finally {
      saving = false;
    }
  }

  async function loadDbInfo() {
    try {
      loadingDbInfo = true;
      dbInfo = await invoke<DbInfo>('get_db_info');
    } catch (err: any) {
      console.error('Failed to load DB info:', err);
      dbMessage = { type: 'error', text: 'DB 정보를 불러오는데 실패했습니다.' };
    } finally {
      loadingDbInfo = false;
    }
  }

  async function exportDb() {
    try {
      // File save dialog
      const destination = await save({
        title: 'Export Database',
        defaultPath: 'agi_voice.db',
        filters: [{
          name: 'SQLite Database',
          extensions: ['db']
        }]
      });

      if (!destination) return; // User cancelled

      await invoke('export_db', { destination });
      dbMessage = { type: 'success', text: 'DB를 성공적으로 내보냈습니다.' };
      setTimeout(() => { dbMessage = null; }, 3000);
    } catch (err: any) {
      dbMessage = { type: 'error', text: err || 'Export 실패' };
    }
  }

  async function importDb() {
    try {
      // File open dialog
      const source = await open({
        title: 'Import Database',
        multiple: false,
        directory: false,
        filters: [{
          name: 'SQLite Database',
          extensions: ['db']
        }]
      });

      if (!source) return; // User cancelled

      if (!confirm('현재 DB를 백업한 후 import합니다. 계속하시겠습니까?')) return;

      await invoke('import_db', { source });
      dbMessage = { type: 'success', text: 'DB를 성공적으로 가져왔습니다. 앱을 재시작하세요.' };
      loadDbInfo();
    } catch (err: any) {
      dbMessage = { type: 'error', text: err || 'Import 실패' };
    }
  }

  async function syncNow() {
    try {
      const result = await invoke<string>('sync_db_now');
      dbMessage = { type: 'success', text: result };
      setTimeout(() => { dbMessage = null; }, 3000);
    } catch (err: any) {
      dbMessage = { type: 'error', text: err || '동기화 실패' };
    }
  }

  async function restoreBackup(backupPath: string) {
    try {
      if (!confirm('이 백업으로 복원하시겠습니까? 현재 DB는 백업됩니다.')) return;

      await invoke('restore_backup', { backupPath });
      dbMessage = { type: 'success', text: '백업에서 복원했습니다. 앱을 재시작하세요.' };
      loadDbInfo();
    } catch (err: any) {
      dbMessage = { type: 'error', text: err || '복원 실패' };
    }
  }

  async function browseDatabasePath() {
    try {
      const selected = await save({
        title: '데이터베이스 파일 경로 선택',
        defaultPath: 'agi_voice.db',
        filters: [{
          name: 'SQLite Database',
          extensions: ['db']
        }]
      });

      if (selected) {
        settings.databaseFilePath = selected;
      }
    } catch (err) {
      console.error('Failed to select database path:', err);
    }
  }

  async function browseClaudeWorkspace() {
    try {
      const selected = await open({
        title: 'Claude 실행 폴더 선택',
        multiple: false,
        directory: true
      });

      if (selected) {
        settings.claudeWorkspaceDir = selected as string;
      }
    } catch (err) {
      console.error('Failed to select Claude workspace:', err);
    }
  }

  onMount(() => {
    loadSettings();
    loadDbInfo();

    // 트레이 설정 로드
    const unsubscribe = settingsStore.subscribe(state => {
      minimizeToTray = state.minimizeToTray;
    });

    return () => {
      unsubscribe();
    };
  });
</script>

<div class="app-settings">
  <div class="page-header">
    <h1>⚙️ 앱 설정</h1>
    <p class="page-description">데이터베이스, 백업 및 Claude 작업 디렉토리를 관리합니다.</p>
  </div>

  {#if loading}
    <div class="loading-state">
      <p class="text-muted">설정 로딩 중...</p>
    </div>
  {:else}
    <!-- Window Settings -->
    <div class="card section">
      <h2 class="section-title text-primary">창 설정</h2>

      <div class="flex items-center justify-between">
        <div>
          <label class="block text-sm font-medium text-secondary">
            종료 시 트레이로 이동
          </label>
          <p class="text-xs mt-1 text-muted">
            창을 닫을 때 앱을 종료하지 않고 시스템 트레이로 최소화합니다.
          </p>
        </div>
        <label class="toggle-switch">
          <input
            type="checkbox"
            bind:checked={minimizeToTray}
            onchange={() => settingsStore.setMinimizeToTray(minimizeToTray)}
          />
          <div class="toggle-switch-track">
            <div class="toggle-switch-thumb"></div>
          </div>
        </label>
      </div>
    </div>

    <!-- Database Settings -->
    <div class="card section">
      <h2 class="section-title text-primary">데이터베이스 설정</h2>

      <form onsubmit={(e) => { e.preventDefault(); saveSettings(); }} class="space-y-6">
        <!-- Database File Path -->
        <div>
          <label class="block text-sm font-medium mb-2 text-secondary">
            데이터베이스 파일 경로 (원드라이브 등 동기화 경로)
          </label>
          <div class="flex gap-2">
            <input
              type="text"
              bind:value={settings.databaseFilePath}
              placeholder="예: C:\Users\username\OneDrive\AGI_Voice\agi_voice.db (비어있으면 agi_voice.db 사용)"
              class="input-field flex-1"
            />
            <button
              type="button"
              onclick={browseDatabasePath}
              class="px-4 py-3 rounded-lg border border-primary text-primary hover:bg-primary hover:text-white transition-colors"
            >
              📁 찾아보기
            </button>
          </div>
          <p class="text-xs mt-2 text-muted">
            원드라이브 등 클라우드 동기화 경로를 지정하면, 여러 PC에서 데이터를 동기화할 수 있습니다.<br>
            서버 시작/종료 시 자동으로 동기화됩니다. 비어있으면 로컬 DB만 사용합니다.
          </p>
        </div>

        <!-- Database Backup Enabled -->
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <label class="block text-sm font-medium text-secondary">
              데이터베이스 백업 활성화
            </label>
            <p class="text-xs mt-1 text-muted">
              서버 종료 시 자동으로 타임스탬프 백업을 생성합니다 (최근 10개 유지).<br>
              백업 위치: <code>backend/backups/</code>
            </p>
          </div>
          <label class="toggle-switch ml-4">
            <input
              type="checkbox"
              bind:checked={settings.databaseBackupEnabled}
            />
            <div class="toggle-switch-track">
              <div class="toggle-switch-thumb"></div>
            </div>
          </label>
        </div>
      </form>
    </div>

    <!-- Database Management -->
    <div class="card section">
      <h2 class="section-title text-primary">데이터베이스 관리</h2>

      {#if dbMessage}
        <div class="{dbMessage.type === 'success' ? 'alert-success' : 'alert-error'} mb-4">
          {dbMessage.text}
        </div>
      {/if}

      {#if loadingDbInfo}
        <p class="text-muted">DB 정보 로딩 중...</p>
      {:else if dbInfo}
        <!-- DB Info -->
        <div class="mb-6 p-4 rounded-lg bg-info-box">
          <h3 class="text-sm font-bold mb-3 text-primary">📊 DB 정보</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-secondary">위치:</span>
              <span class="text-primary font-mono text-xs">{dbInfo.path}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-secondary">크기:</span>
              <span class="text-primary">{dbInfo.sizeMb.toFixed(2)} MB</span>
            </div>
            {#if dbInfo.lastModified}
              <div class="flex justify-between">
                <span class="text-secondary">마지막 수정:</span>
                <span class="text-primary">{new Date(dbInfo.lastModified).toLocaleString()}</span>
              </div>
            {/if}
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-3 mb-6">
          <button onclick={exportDb} class="btn-primary flex-1">
            Export DB
          </button>
          <button onclick={importDb} class="btn-primary flex-1">
            Import DB
          </button>
          <button onclick={syncNow} class="btn-primary flex-1">
            수동 동기화
          </button>
        </div>

        <!-- Backups -->
        {#if dbInfo.backups.length > 0}
          <div>
            <h3 class="text-sm font-bold mb-3 text-primary">💾 백업 목록 (최신 {dbInfo.backups.length}개)</h3>
            <div class="space-y-2">
              {#each dbInfo.backups as backup}
                <div class="flex items-center justify-between p-3 rounded-lg border border-default">
                  <div class="flex-1">
                    <p class="text-sm font-medium text-primary">{backup.filename}</p>
                    <p class="text-xs text-muted">
                      {backup.sizeMb.toFixed(2)} MB
                      {#if backup.createdAt}
                        • {new Date(backup.createdAt).toLocaleString()}
                      {/if}
                    </p>
                  </div>
                  <button
                    onclick={() => restoreBackup(backup.path)}
                    class="btn-primary btn-sm"
                  >
                    복원
                  </button>
                </div>
              {/each}
            </div>
          </div>
        {:else}
          <p class="text-sm text-muted">백업이 없습니다.</p>
        {/if}
      {/if}
    </div>

    <!-- AI Settings -->
    <div class="card section">
      <h2 class="section-title text-primary">AI 채팅 설정</h2>

      <form onsubmit={(e) => { e.preventDefault(); saveSettings(); }} class="space-y-6">
        <!-- Claude Workspace Directory -->
        <div>
          <label class="block text-sm font-medium mb-2 text-secondary">
            Claude 실행 폴더
          </label>
          <div class="flex gap-2">
            <input
              type="text"
              bind:value={settings.claudeWorkspaceDir}
              placeholder="예: C:\Users\username\Projects\MyProject (비어있으면 AppData\Roaming\AGI_Voice_V2 사용)"
              class="input-field flex-1"
            />
            <button
              type="button"
              onclick={browseClaudeWorkspace}
              class="px-4 py-3 rounded-lg border border-primary text-primary hover:bg-primary hover:text-white transition-colors"
            >
              📁 찾아보기
            </button>
          </div>
          <p class="text-xs mt-2 text-muted">
            Claude CLI가 실행될 작업 디렉토리입니다. 비어있으면 기본값(AppData\Roaming\AGI_Voice_V2)을 사용합니다.<br>
            이 폴더에 CLAUDE.md 파일이 생성되고, 상대 경로는 이 폴더 기준입니다.
          </p>
        </div>

        <!-- Claude Model Selection -->
        <div>
          <label class="block text-sm font-medium mb-2 text-secondary">
            기본 Claude 모델
          </label>
          <select
            bind:value={settings.defaultClaudeModel}
            class="select-field w-full"
          >
            <option value="sonnet">Sonnet (균형잡힌 성능, 기본값)</option>
            <option value="opus">Opus (최고 성능, 느림)</option>
            <option value="haiku">Haiku (빠른 응답, 낮은 성능)</option>
          </select>
          <p class="text-xs mt-2 text-muted">
            AI 채팅에 사용할 Claude 모델을 선택합니다. Sonnet은 균형잡힌 성능으로 대부분의 경우 권장됩니다.
          </p>
        </div>

        <!-- Keep Conversation Prompts -->
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <label class="block text-sm font-medium text-secondary">
              기존 대화는 프롬프트 설정 유지
            </label>
            <p class="text-xs mt-1 text-muted">
              체크 시: 기존 대화는 생성 당시의 캐릭터/시스템 메시지를 계속 사용합니다.<br>
              해제 시: 기존 대화도 현재 설정된 캐릭터/시스템 메시지를 사용합니다.
            </p>
          </div>
          <label class="toggle-switch ml-4">
            <input
              type="checkbox"
              bind:checked={settings.keepConversationPrompts}
            />
            <div class="toggle-switch-track">
              <div class="toggle-switch-thumb"></div>
            </div>
          </label>
        </div>

        <!-- Message -->
        {#if message}
          <div class="{message.type === 'success' ? 'alert-success' : 'alert-error'}">
            {message.text}
          </div>
        {/if}

        <!-- Save Button -->
        <div class="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            class="btn-primary"
          >
            {saving ? '저장 중...' : '설정 저장'}
          </button>
        </div>
      </form>
    </div>

    <!-- Info Card -->
    <div class="card section">
      <h3 class="section-title text-primary">💡 설정 안내</h3>
      <ul class="space-y-2 text-sm text-secondary">
        <li>• <strong>데이터베이스 경로</strong>: 원드라이브 등 클라우드 경로를 지정하면 여러 PC에서 동기화됩니다.</li>
        <li>• <strong>백업</strong>: 앱 종료 시 자동 백업 (타임스탬프 파일명, 최근 10개 유지).</li>
        <li>• <strong>Claude 실행 폴더</strong>: AI 채팅 시 Claude CLI가 실행될 작업 디렉토리입니다.</li>
        <li>• 비어있으면 기본값(<code>AppData\Roaming\AGI_Voice_V2</code>)을 사용합니다.</li>
        <li>• 폴더가 존재하지 않으면 저장 시 오류가 발생합니다.</li>
        <li>• 설정은 <code>AppData\Roaming\AGI_Voice_V2\config.json</code>에 저장됩니다.</li>
      </ul>
    </div>
  {/if}
</div>

<style>
  .app-settings {
    max-width: 800px;
    margin: 0 auto;
  }
</style>
