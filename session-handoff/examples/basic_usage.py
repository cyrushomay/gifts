"""
Basic usage example for Session Handoff Writer (Python)

This shows the typical workflow:
1. Initialize at session start
2. Track state as you work
3. Save periodically (manual or via cron)
4. Resume from handoff in next session
"""

import time
from handoff_writer import HandoffWriter, display_handoff


def main():
    print('=== Session Handoff Example ===\n')

    # 1. Initialize handoff writer (reads existing HANDOFF.md if present)
    handoff = HandoffWriter('./HANDOFF.md')

    # Display existing handoff at session start
    display_handoff('./HANDOFF.md')

    # 2. Track state as you work
    print('Setting up task state...')

    handoff.set_next_action('Review and merge PR #42 from @cairn')
    handoff.blocked_on('Waiting for test results from CI pipeline')
    handoff.add_time_sensitive('Deploy before 2026-02-10 midnight UTC', '2026-02-10 00:00 UTC')

    # Mark something as complete
    handoff.completed('Fixed authentication bug in login flow')
    handoff.completed('Updated documentation for circuit breaker')

    # 3. Save manually
    handoff.save()
    print('Handoff saved manually\n')

    # Simulate work continuing...
    print('Doing work...')
    time.sleep(1)

    # Update state as work progresses
    handoff.unblock('Waiting for test results from CI pipeline')
    handoff.completed('CI tests passed')
    handoff.set_next_action('Merge PR #42 and trigger deployment')
    handoff.save()

    print('State updated and saved\n')

    # Display final state
    print('Final handoff state:')
    state = handoff.get_state()
    for key, value in state.items():
        if key != 'timestamp':
            print(f"  {key}: {value}")

    print('\n=== Session End ===')
    print('Next session will read HANDOFF.md and resume from "Next Action"')


if __name__ == '__main__':
    main()
