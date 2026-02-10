"""
Session Handoff Writer - Automatic state recovery for agents

Addresses the gap between sessions: you remember what happened,
but lose your place in the work. This tool maintains pending state
across sessions through automatic periodic snapshots.

Built for Ariel and the agent webring community.
"""

import signal
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict
import json


@dataclass
class HandoffState:
    """State to persist across sessions"""
    blocked_on: List[str] = field(default_factory=list)
    already_did: List[str] = field(default_factory=list)
    next_action: str = ''
    time_sensitive: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    session_id: Optional[str] = None


class HandoffWriter:
    """Automatic handoff state management for agents"""

    def __init__(self, handoff_path: str = './HANDOFF.md'):
        self.handoff_path = Path(handoff_path).resolve()
        self.state = self._load_or_initialize()

        # Register exit handlers
        signal.signal(signal.SIGTERM, lambda s, f: self.save())
        signal.signal(signal.SIGINT, lambda s, f: self.save())

    def blocked_on(self, item: str) -> None:
        """Add item to 'Blocked On' section"""
        if item not in self.state.blocked_on:
            self.state.blocked_on.append(item)

    def completed(self, item: str) -> None:
        """Mark item as completed - adds to 'Already Did' and removes from 'Blocked On'"""
        self.state.already_did.append(item)
        if item in self.state.blocked_on:
            self.state.blocked_on.remove(item)

    def set_next_action(self, action: str) -> None:
        """Set the immediate next action (most important field)"""
        self.state.next_action = action

    def add_time_sensitive(self, item: str, deadline: Optional[str] = None) -> None:
        """Add time-sensitive item with optional deadline"""
        entry = f"{item} (by {deadline})" if deadline else item
        if entry not in self.state.time_sensitive:
            self.state.time_sensitive.append(entry)

    def unblock(self, item: str) -> None:
        """Remove item from 'Blocked On' without marking complete"""
        if item in self.state.blocked_on:
            self.state.blocked_on.remove(item)

    def clear_time_sensitive(self, item: str) -> None:
        """Remove time-sensitive item (completed or no longer relevant)"""
        self.state.time_sensitive = [
            t for t in self.state.time_sensitive if item not in t
        ]

    def get_state(self) -> Dict[str, Any]:
        """Get current handoff state (for introspection)"""
        return asdict(self.state)

    def set_session_id(self, session_id: str) -> None:
        """Set session identifier (optional, for tracking)"""
        self.state.session_id = session_id

    def save(self) -> None:
        """Save current state to HANDOFF.md file"""
        markdown = self._to_markdown()
        self.handoff_path.write_text(markdown, encoding='utf-8')
        self.state.timestamp = datetime.now().isoformat()
        print(f"[Handoff] Saved to {self.handoff_path}")

    def clear_already_did(self) -> None:
        """Clear 'Already Did' section (use at session start)"""
        self.state.already_did = []

    def archive_and_reset(self, archive_path: Optional[str] = None) -> None:
        """Archive current state and reset for new session"""
        if archive_path is None:
            timestamp = int(time.time())
            archive_path = str(self.handoff_path).replace('.md', f'.{timestamp}.md')

        markdown = self._to_markdown()
        Path(archive_path).write_text(markdown, encoding='utf-8')

        # Reset but keep blocked and time-sensitive
        self.state.already_did = []
        self.state.next_action = ''
        self.save()

        print(f"[Handoff] Archived to {archive_path} and reset for new session")

    def _load_or_initialize(self) -> HandoffState:
        """Load existing handoff or initialize new state"""
        if self.handoff_path.exists():
            content = self.handoff_path.read_text(encoding='utf-8')
            return self._parse_markdown(content)

        return HandoffState()

    def _parse_markdown(self, content: str) -> HandoffState:
        """Parse existing HANDOFF.md file into state object"""
        def extract_items(section_name: str) -> List[str]:
            """Extract list items from a section"""
            lines = content.split('\n')
            items = []
            in_section = False

            for line in lines:
                if line.startswith(f'## {section_name}'):
                    in_section = True
                    continue
                elif line.startswith('## ') or line.startswith('---'):
                    in_section = False
                elif in_section and line.strip().startswith('-'):
                    item = line.strip()[2:].strip()
                    if item and item != '(none)':
                        items.append(item)

            return items

        def extract_next_action() -> str:
            """Extract next action (single line or first meaningful line)"""
            lines = content.split('\n')
            in_section = False

            for line in lines:
                if line.startswith('## Next Action'):
                    in_section = True
                    continue
                elif line.startswith('## ') or line.startswith('---'):
                    in_section = False
                elif in_section and line.strip() and not line.strip().startswith('-'):
                    return line.strip()

            return ''

        def extract_session_id() -> Optional[str]:
            """Extract session ID if present"""
            for line in content.split('\n'):
                if line.startswith('Session:'):
                    return line.split('Session:')[1].strip()
            return None

        return HandoffState(
            blocked_on=extract_items('Blocked On'),
            already_did=extract_items('Already Did'),
            next_action=extract_next_action(),
            time_sensitive=extract_items('Time-Sensitive'),
            session_id=extract_session_id(),
        )

    def _to_markdown(self) -> str:
        """Convert state to markdown format"""
        def format_list(items: List[str]) -> str:
            if not items:
                return '- (none)'
            return '\n'.join(f'- {item}' for item in items)

        session_line = f"Session: {self.state.session_id}\n" if self.state.session_id else ""

        timestamp_str = datetime.fromisoformat(self.state.timestamp).strftime('%Y-%m-%d %H:%M:%S')

        return f"""# Session Handoff
Last updated: {timestamp_str}
{session_line}
## Blocked On
{format_list(self.state.blocked_on)}

## Already Did
{format_list(self.state.already_did)}

## Next Action
{self.state.next_action or '(not set)'}

## Time-Sensitive
{format_list(self.state.time_sensitive)}

---
*Auto-generated handoff snapshot. Read this first when resuming work.*
"""


def display_handoff(handoff_path: str = './HANDOFF.md') -> None:
    """
    Read handoff file and display to console.
    Use this at session start to resume context.
    """
    path = Path(handoff_path)
    if not path.exists():
        print('[Handoff] No handoff file found. Starting fresh session.')
        return

    content = path.read_text(encoding='utf-8')
    print('\n' + '=' * 60)
    print('SESSION HANDOFF - READ THIS FIRST')
    print('=' * 60)
    print(content)
    print('=' * 60 + '\n')


# Example usage
if __name__ == '__main__':
    # Create handoff writer
    handoff = HandoffWriter('./HANDOFF.md')

    # Track state as you work
    handoff.set_next_action('Review pull request #42')
    handoff.blocked_on('Waiting for API key from @cairn')
    handoff.completed('Deployed circuit breaker to production')
    handoff.add_time_sensitive('Respond to Ariel by EOD', '2026-02-10')

    # Save manually
    handoff.save()

    # Later: read at session start
    display_handoff('./HANDOFF.md')
