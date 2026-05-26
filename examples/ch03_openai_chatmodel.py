from __future__ import annotations

import sys

from agent_learning.llm.chat import ChatService
from agent_learning.llm.openai import integration_enabled, load_config_from_env, new_chat_model


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What does ChatOpenAI do?"
    if not integration_enabled():
        print("OpenAI integration is disabled.")
        print("Set RUN_AGENT_LEARNING_INTEGRATION=1 and OPENAI_API_KEY to run this example.")
        return

    model = new_chat_model(load_config_from_env())
    print(ChatService(model).ask(question))


if __name__ == "__main__":
    main()
