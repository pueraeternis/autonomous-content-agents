import argparse
import time
from typing import Any, cast

from langgraph.errors import GraphRecursionError

from content_agents.core.config import PublisherName
from content_agents.core.logger import logger
from content_agents.engineering.replay import ReplayContext
from content_agents.graph.state import AgentState, create_initial_state
from content_agents.graph.workflow import app
from content_agents.services.publishers.factory import set_publisher_override


def _log_final_state(final_state: AgentState) -> None:
    publish_mode = final_state.get("publish_mode")
    if publish_mode == "live" and final_state.get("final_tweet_id"):
        logger.info(
            "Session finished. Tweet published.",
            id=final_state["final_tweet_id"],
        )
    elif publish_mode == "mock":
        logger.info("Session finished. Mock publish completed.")
    else:
        reason = final_state.get("termination_reason", "unknown")
        logger.warning("Session finished but nothing was published.", reason=reason)


def _execute_workflow(
    initial_state: AgentState, *, inspect: bool = False
) -> AgentState:
    if inspect:
        final_state = dict(initial_state)
        for event in app.stream(cast(Any, initial_state), stream_mode="updates"):
            logger.info("Node update", event=event)
            for node_update in event.values():
                if isinstance(node_update, dict):
                    final_state.update(node_update)
        return cast(AgentState, final_state)

    return cast(AgentState, app.invoke(cast(Any, initial_state)))


def run_once(
    *,
    replay_snapshot: str | None = None,
    publisher: PublisherName | None = None,
    inspect: bool = False,
) -> None:
    """Single execution of the agent workflow."""
    logger.info("Starting Autonomous Session")

    if publisher is not None:
        set_publisher_override(publisher)

    initial_state = create_initial_state()

    try:
        if replay_snapshot:
            with ReplayContext(replay_snapshot):
                final_state = _execute_workflow(initial_state, inspect=inspect)
        else:
            final_state = _execute_workflow(initial_state, inspect=inspect)

        _log_final_state(final_state)
    except GraphRecursionError:
        logger.exception("Workflow exceeded recursion limit")
    except Exception as e:
        logger.exception("Critical error in agent loop", error=str(e))
    finally:
        set_publisher_override(None)


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous Content Agents")
    parser.add_argument("--loop", action="store_true", help="Run in continuous loop")
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Interval in seconds (default: 1 hour)",
    )
    parser.add_argument(
        "--replay",
        type=str,
        default=None,
        help="Path to a workflow input snapshot for deterministic replay",
    )
    parser.add_argument(
        "--publisher",
        type=str,
        choices=["twitter", "console", "markdown"],
        default=None,
        help="Publisher adapter override for this run",
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Stream per-node state updates during execution",
    )

    args = parser.parse_args()
    publisher = cast(PublisherName | None, args.publisher)

    if args.loop:
        logger.info("Starting Daemon Mode", interval=args.interval)
        while True:
            run_once(
                replay_snapshot=args.replay,
                publisher=publisher,
                inspect=args.inspect,
            )
            logger.info("Sleeping...", seconds=args.interval)
            time.sleep(args.interval)
    else:
        run_once(
            replay_snapshot=args.replay,
            publisher=publisher,
            inspect=args.inspect,
        )


if __name__ == "__main__":
    main()
