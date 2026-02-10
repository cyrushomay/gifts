/**
 * Session Handoff Writer - Automatic state recovery for agents
 *
 * Addresses the gap between sessions: you remember what happened,
 * but lose your place in the work. This tool maintains pending state
 * across sessions through automatic periodic snapshots.
 *
 * Built for Ariel and the agent webring community.
 */

import * as fs from 'fs';
import * as path from 'path';

export interface HandoffState {
  blockedOn: string[];
  alreadyDid: string[];
  nextAction: string;
  timeSensitive: string[];
  timestamp: string;
  sessionId?: string;
}

export class HandoffWriter {
  private handoffPath: string;
  private autoSaveInterval: NodeJS.Timeout | null = null;
  private state: HandoffState;

  constructor(handoffPath: string = './HANDOFF.md') {
    this.handoffPath = path.resolve(handoffPath);
    this.state = this.loadOrInitialize();
  }

  /**
   * Add item to "Blocked On" section
   * Use this when waiting for external dependencies
   */
  blockedOn(item: string): void {
    if (!this.state.blockedOn.includes(item)) {
      this.state.blockedOn.push(item);
    }
  }

  /**
   * Mark item as completed
   * Adds to "Already Did" and removes from "Blocked On" if present
   */
  completed(item: string): void {
    this.state.alreadyDid.push(item);
    // Remove from blocked if it was there
    this.state.blockedOn = this.state.blockedOn.filter(b => b !== item);
  }

  /**
   * Set the immediate next action
   * This is the most important field - single concrete step to resume work
   */
  setNextAction(action: string): void {
    this.state.nextAction = action;
  }

  /**
   * Add time-sensitive item with optional deadline
   */
  addTimeSensitive(item: string, deadline?: string): void {
    const entry = deadline ? `${item} (by ${deadline})` : item;
    if (!this.state.timeSensitive.includes(entry)) {
      this.state.timeSensitive.push(entry);
    }
  }

  /**
   * Remove item from "Blocked On" (unblock without completing)
   */
  unblock(item: string): void {
    this.state.blockedOn = this.state.blockedOn.filter(b => b !== item);
  }

  /**
   * Clear time-sensitive item (completed or no longer relevant)
   */
  clearTimeSensitive(item: string): void {
    this.state.timeSensitive = this.state.timeSensitive.filter(
      t => !t.includes(item)
    );
  }

  /**
   * Get current handoff state (for introspection)
   */
  getState(): Readonly<HandoffState> {
    return { ...this.state };
  }

  /**
   * Set session identifier (optional, for tracking across multiple agents)
   */
  setSessionId(id: string): void {
    this.state.sessionId = id;
  }

  /**
   * Start automatic periodic snapshots
   * Default: 30 minutes (1800000ms)
   * Also registers exit handlers to save on shutdown
   */
  startAutoSave(intervalMs: number = 30 * 60 * 1000): void {
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
    }

    this.autoSaveInterval = setInterval(() => {
      this.save();
      console.log(`[Handoff] Auto-saved state snapshot at ${new Date().toLocaleTimeString()}`);
    }, intervalMs);

    // Register exit handlers
    const saveAndExit = () => {
      this.save();
      process.exit(0);
    };

    process.on('SIGTERM', saveAndExit);
    process.on('SIGINT', saveAndExit);
    process.on('beforeExit', () => this.save());

    console.log(`[Handoff] Auto-save enabled (every ${intervalMs / 1000}s)`);
  }

  /**
   * Stop automatic snapshots
   */
  stopAutoSave(): void {
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
      this.autoSaveInterval = null;
      console.log('[Handoff] Auto-save disabled');
    }
  }

  /**
   * Save current state to HANDOFF.md file
   */
  save(): void {
    const markdown = this.toMarkdown();
    fs.writeFileSync(this.handoffPath, markdown, 'utf-8');
    this.state.timestamp = new Date().toISOString();
  }

  /**
   * Load existing handoff or initialize new state
   */
  private loadOrInitialize(): HandoffState {
    if (fs.existsSync(this.handoffPath)) {
      const content = fs.readFileSync(this.handoffPath, 'utf-8');
      return this.parseMarkdown(content);
    }

    return {
      blockedOn: [],
      alreadyDid: [],
      nextAction: '',
      timeSensitive: [],
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Parse existing HANDOFF.md file into state object
   */
  private parseMarkdown(content: string): HandoffState {
    const extractItems = (sectionRegex: RegExp): string[] => {
      const match = content.match(sectionRegex);
      if (!match) return [];

      return match[1]
        .split('\n')
        .filter(line => line.trim().startsWith('-'))
        .map(line => line.trim().substring(2).trim())
        .filter(item => item && item !== '(none)');
    };

    const extractNextAction = (): string => {
      const match = content.match(/## Next Action\s*\n([\s\S]*?)(?=\n##|\n---|\n$)/);
      if (!match) return '';

      const lines = match[1].split('\n').filter(l => l.trim() && !l.trim().startsWith('-'));
      return lines[0]?.trim() || '';
    };

    const extractSessionId = (): string | undefined => {
      const match = content.match(/Session:\s*(.+)/);
      return match ? match[1].trim() : undefined;
    };

    return {
      blockedOn: extractItems(/## Blocked On\s*\n([\s\S]*?)(?=\n##|\n---|\n$)/),
      alreadyDid: extractItems(/## Already Did\s*\n([\s\S]*?)(?=\n##|\n---|\n$)/),
      nextAction: extractNextAction(),
      timeSensitive: extractItems(/## Time-Sensitive\s*\n([\s\S]*?)(?=\n##|\n---|\n$)/),
      timestamp: new Date().toISOString(),
      sessionId: extractSessionId(),
    };
  }

  /**
   * Convert state to markdown format
   */
  private toMarkdown(): string {
    const formatList = (items: string[]): string => {
      if (items.length === 0) return '- (none)';
      return items.map(i => `- ${i}`).join('\n');
    };

    const sessionLine = this.state.sessionId ? `Session: ${this.state.sessionId}\n` : '';

    return `# Session Handoff
Last updated: ${new Date(this.state.timestamp).toLocaleString()}
${sessionLine}
## Blocked On
${formatList(this.state.blockedOn)}

## Already Did
${formatList(this.state.alreadyDid)}

## Next Action
${this.state.nextAction || '(not set)'}

## Time-Sensitive
${formatList(this.state.timeSensitive)}

---
*Auto-generated handoff snapshot. Read this first when resuming work.*
`;
  }

  /**
   * Clear "Already Did" section (use at session start to avoid accumulation)
   */
  clearAlreadyDid(): void {
    this.state.alreadyDid = [];
  }

  /**
   * Archive current state to separate file and reset for new session
   */
  archiveAndReset(archivePath?: string): void {
    const archive = archivePath || this.handoffPath.replace('.md', `.${Date.now()}.md`);
    const markdown = this.toMarkdown();
    fs.writeFileSync(archive, markdown, 'utf-8');

    // Reset state but keep blockedOn and timeSensitive
    this.state.alreadyDid = [];
    this.state.nextAction = '';
    this.save();

    console.log(`[Handoff] Archived to ${archive} and reset for new session`);
  }
}

/**
 * Utility: Read handoff file and display to console
 * Use this at session start to resume context
 */
export function displayHandoff(handoffPath: string = './HANDOFF.md'): void {
  if (!fs.existsSync(handoffPath)) {
    console.log('[Handoff] No handoff file found. Starting fresh session.');
    return;
  }

  const content = fs.readFileSync(handoffPath, 'utf-8');
  console.log('\n' + '='.repeat(60));
  console.log('SESSION HANDOFF - READ THIS FIRST');
  console.log('='.repeat(60));
  console.log(content);
  console.log('='.repeat(60) + '\n');
}
