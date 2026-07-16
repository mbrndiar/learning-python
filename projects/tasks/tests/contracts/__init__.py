"""Reusable contracts kept independent of any concrete adapter.

Milestone tests can focus on implementation-specific teaching points while
these helpers enforce the behavior that repositories, servers, and clients
must share.  Keeping the assertions centralized also makes a parity failure
identify the adapter parameter rather than a subtly different copied test.
"""

__all__: list[str] = []
