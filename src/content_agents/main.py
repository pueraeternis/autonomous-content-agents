import argparse
import time

from src.content_agents.core.logger import logger
from src.content_agents.graph.workflow import app


def run_once() -> None:
    """Single execution of the agent workflow."""
    logger.info("🚀 Starting Autonomous Session")

    initial_state = {
        "topic": "",
        "articles": [],
        "draft": None,
        "critique_history": [],
        "iteration_count": 0,
        "final_tweet_id": None,
    }

    try:
        final_state = app.invoke(initial_state)

        if final_state.get("final_tweet_id"):
            logger.info("✅ Session finished. Tweet published.", id=final_state["final_tweet_id"])
        else:
            logger.warning("⚠️ Session finished but nothing was published.")

    except Exception as e:
        logger.exception("🔥 Critical error in agent loop", error=str(e))


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous Content Agents")
    parser.add_argument("--loop", action="store_true", help="Run in continuous loop")
    parser.add_argument("--interval", type=int, default=3600, help="Interval in seconds (default: 1 hour)")

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
