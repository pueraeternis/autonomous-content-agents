import argparse
import time
from typing import Any, cast

from langgraph.errors import GraphRecursionError

from content_agents.core.logger import logger
from content_agents.graph.state import create_initial_state
from content_agents.graph.workflow import app


def run_once() -> None:
    """Single execution of the agent workflow."""
    logger.info("Starting Autonomous Session")

    initial_state = create_initial_state()

    try:
        final_state = app.invoke(cast(Any, initial_state))

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

    except GraphRecursionError:
        logger.exception("Workflow exceeded recursion limit")
    except Exception as e:
        logger.exception("Critical error in agent loop", error=str(e))


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous Content Agents")
    parser.add_argument("--loop", action="store_true", help="Run in continuous loop")
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Interval in seconds (default: 1 hour)",
    )

    args = parser.parse_args()

    if args.loop:
        logger.info("Starting Daemon Mode", interval=args.interval)
        while True:
            run_once()
            logger.info("Sleeping...", seconds=args.interval)
            time.sleep(args.interval)
    else:
        run_once()


if __name__ == "__main__":
    main()
