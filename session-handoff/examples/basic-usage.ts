/**
 * Basic usage example for Session Handoff Writer
 *
 * This shows the typical workflow:
 * 1. Initialize at session start
 * 2. Track state as you work
 * 3. Enable auto-save for periodic snapshots
 * 4. Resume from handoff in next session
 */

import { HandoffWriter, displayHandoff } from '../handoff-writer';

async function main() {
  console.log('=== Session Handoff Example ===\n');

  // 1. Initialize handoff writer (reads existing HANDOFF.md if present)
  const handoff = new HandoffWriter('./HANDOFF.md');

  // Display existing handoff at session start
  displayHandoff('./HANDOFF.md');

  // 2. Track state as you work
  console.log('Setting up task state...');

  handoff.setNextAction('Review and merge PR #42 from @cairn');
  handoff.blockedOn('Waiting for test results from CI pipeline');
  handoff.addTimeSensitive('Deploy before 2026-02-10 midnight UTC', '2026-02-10 00:00 UTC');

  // Mark something as complete
  handoff.completed('Fixed authentication bug in login flow');
  handoff.completed('Updated documentation for circuit breaker');

  // 3. Enable automatic snapshots every 30 minutes
  handoff.startAutoSave(30 * 60 * 1000);
  console.log('Auto-save enabled (30min intervals)\n');

  // 4. Save manually anytime
  handoff.save();
  console.log('Handoff saved manually\n');

  // Simulate work continuing...
  console.log('Doing work...');
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Update state as work progresses
  handoff.unblock('Waiting for test results from CI pipeline');
  handoff.completed('CI tests passed');
  handoff.setNextAction('Merge PR #42 and trigger deployment');
  handoff.save();

  console.log('State updated and saved\n');

  // Display final state
  console.log('Final handoff state:');
  const state = handoff.getState();
  console.log(JSON.stringify(state, null, 2));

  // Stop auto-save (in real usage, this happens automatically on process exit)
  handoff.stopAutoSave();

  console.log('\n=== Session End ===');
  console.log('Next session will read HANDOFF.md and resume from "Next Action"');
}

// Run example
main().catch(console.error);
