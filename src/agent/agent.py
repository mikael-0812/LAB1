import ast
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    """
    A ReAct-style Agent that follows the Thought-Action-Observation loop.
    """

    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []
        self.trace_lines: List[str] = []

    def get_system_prompt(self) -> str:
        """
        Build the system prompt with available tools and format instructions.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""
You are an intelligent assistant that can call external tools when needed.
Use the available tools only when they are required to answer the user query.

Available tools:
{tool_descriptions}

Follow this exact format:
Thought: <your reasoning here>
Action: tool_name(arg1, arg2)
Observation: <result from tool>
... (repeat Thought/Action/Observation as needed)
Final Answer: <your final answer>

If you cannot answer the question using the available tools, answer exactly:
Final Answer: [OUT_OF_SCOPE]
"""

    def run(self, user_input: str) -> str:
        """
        Execute the ReAct loop until a final answer is produced or the step limit is reached.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        self.trace_lines = []
        prompt_history = [f"User: {user_input}"]
        system_prompt = self.get_system_prompt()
        steps = 0

        while steps < self.max_steps:
            response = self.llm.generate("\n".join(prompt_history), system_prompt=system_prompt)
            content = response.get("content", "").strip()
            self.trace_lines.append(content)
            logger.log_event("AGENT_RESPONSE", {"step": steps + 1, "content": content})

            final_answer = self._extract_final_answer(content)
            if final_answer is not None:
                logger.log_event("AGENT_FINAL_ANSWER", {"answer": final_answer, "steps": steps + 1})
                return final_answer

            action_name, action_args = self._parse_action(content)
            if not action_name:
                logger.log_event("AGENT_NO_ACTION", {"step": steps + 1, "response": content})
                # If the model does not propose an action, return the raw content or fallback.
                return content if content else "[OUT_OF_SCOPE]"

            observation = self._execute_tool(action_name, action_args)
            observation_text = json.dumps(observation, ensure_ascii=False) if isinstance(observation, (dict, list)) else str(observation)
            self.trace_lines.append(f"Observation: {observation_text}")
            logger.log_event("AGENT_TOOL_CALL", {"step": steps + 1, "tool": action_name, "args": action_args, "observation": observation_text})

            thought_text = self._extract_thought(content) or "Continue reasoning with the latest observation."
            prompt_history.append(f"Thought: {thought_text}")
            prompt_history.append(f"Action: {action_name}({action_args})")
            prompt_history.append(f"Observation: {observation_text}")

            steps += 1

        logger.log_event("AGENT_END", {"steps": steps, "status": "max_steps_reached"})
        return "[OUT_OF_SCOPE]"

    def _parse_action(self, text: str) -> Tuple[Optional[str], str]:
        """
        Parse an action line of the form Action: tool_name(arg1, arg2)
        """
        match = re.search(r"Action:\s*([A-Za-z0-9_]+)\s*\((.*?)\)", text, re.IGNORECASE | re.DOTALL)
        if not match:
            return None, ""
        tool_name = match.group(1).strip()
        args = match.group(2).strip()
        return tool_name, args

    def _extract_final_answer(self, text: str) -> Optional[str]:
        match = re.search(r"Final Answer:\s*(.+)$", text, re.IGNORECASE | re.DOTALL)
        if not match:
            return None
        answer = match.group(1).strip()
        return answer

    def _extract_thought(self, text: str) -> Optional[str]:
        match = re.search(r"Thought:\s*(.+)", text, re.IGNORECASE)
        if not match:
            return None
        return match.group(1).strip()

    def _execute_tool(self, tool_name: str, args: str) -> Any:
        """
        Execute a registered tool by name and return its result.
        """
        for tool in self.tools:
            if tool["name"] == tool_name:
                func = tool.get("func")
                if not callable(func):
                    return f"Tool {tool_name} is not callable."

                parsed_args = []
                if args:
                    try:
                        raw_tuple = ast.literal_eval(f"({args},)")
                        if isinstance(raw_tuple, tuple):
                            parsed_args = list(raw_tuple)
                        else:
                            parsed_args = [raw_tuple]
                    except Exception:
                        parsed_args = [arg.strip().strip('"\'') for arg in args.split(",") if arg.strip()]

                try:
                    return func(*parsed_args)
                except TypeError:
                    # Fall back to sending raw args as a single argument when the tool expects one string.
                    if len(parsed_args) != 1:
                        return func(args)
                    return f"Invalid arguments for {tool_name}: {args}"
                except Exception as exc:
                    return f"Tool execution error: {str(exc)}"

        return f"Tool {tool_name} not found."
