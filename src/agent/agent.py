import json
import re
from typing import List, Dict, Any, Optional

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.tools.dynamic_registry import execute_dynamic_tool


class ReActAgent:
    """
    A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Implements the core loop logic and tool execution.
    """

    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 7):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history: List[Dict[str, str]] = []
        self.tool_names = {tool["name"] for tool in tools if "name" in tool}

    def get_system_prompt(self) -> str:
        """
        System prompt that instructs the agent to follow ReAct.
        """
        import json
        tool_descriptions = ""
        for t in self.tools:
            tool_descriptions += f"- {t['name']}: {t['description']}\n"

        return f"""
You are an intelligent assistant. You must solve the user's request by calling out to tools.
You have access to the following tools:
{tool_descriptions}

FASHION / WEATHER RULES:
- If the user asks for clothing or fashion suggestions based on weather, first use get_weather if real-time weather is needed.
- If get_weather fails, do NOT escalate_to_human.
- Instead, respond in Vietnamese and ask the user to describe the weather manually, for example:
  "Mình chưa lấy được dữ liệu thời tiết thực tế ở Hà Nội lúc này. Bạn cho mình biết hiện tại trời nóng hay mát, có nắng hay mưa, và bạn cần mặc để đi làm hay đi chơi, mình sẽ gợi ý các mặt hàng phù hợp hơn từ cửa hàng nhé."
- If the user already provides weather details manually, use recommend_fashion_manual.
- Only recommend clothing item names returned by the fashion recommendation tools.
- Do not invent product names that are not present in the database.

Example:
User Request: Trời nóng có nắng, mình đi chơi, gợi ý đồ giúp mình.
Thought: User already provided weather and occasion manually, so I should use the fashion recommendation tool directly.
Action: recommend_fashion_manual({{"weather": "nóng có nắng", "occasion": "đi chơi"}})

CRITICAL: If any tool (like check_payment) returns an error (e.g. Error 500) or if you cannot satisfy the user, you MUST immediately call the 'escalate_to_human' tool to escalate the problem!

Always use the following exact format for your responses:
Thought: your line of reasoning. Look at the Observation and decide what to do next. If you need to use a tool, output 'Action: tool_name(arguments)' then stop generating and wait for the Observation.
Action: tool_name(arguments_in_JSON)
Observation: the result of the tool call

When you have the final answer, output:
Final Answer: your final response to the user.
Always respond to the user in Vietnamese.
Even if tool outputs or internal reasoning are in English, the Final Answer must be in Vietnamese.

If the user asks a question that is absolutely impossible to answer using the provided tools and cannot be resolved, you MUST end your Final Answer with exactly the tag: [OUT_OF_SCOPE].

Example:
Thought: I need to check the location.
Action: get_location({{}})
Observation: Quận 1, TP.HCM
Thought: I know the location now.
Final Answer: You are currently located at Quận 1, TP.HCM.
"""

    def run(self, user_input: str) -> str:
        """
        Implements the ReAct loop logic.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        current_prompt = f"User Request: {user_input}\n"
        steps = 0
        final_answer = None

        while steps < self.max_steps:
            logger.log_event("STEP_START", {"step": steps + 1})
            
            # Generate LLM response
            response = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            result_text = response.get("content", "")
            
            # Extract Thought, Action, Final Answer
            thought_match = re.search(r"Thought:\s*(.*?)(?=(?:Action:|Final Answer:|$))", result_text, re.DOTALL)
            action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", result_text, re.DOTALL)
            final_match = re.search(r"Final Answer:\s*(.*)", result_text, re.DOTALL)
            
            thought = thought_match.group(1).strip() if thought_match else "No thought found."
            
            usage = response.get("usage", {})
            total_tokens = usage.get("total_tokens", None)
            
            logger.log_step("Agent", "Thought", thought, tokens=total_tokens)

            if final_match:
                final_answer = final_match.group(1).strip()
                logger.log_step("Agent", "Final Answer", final_answer)
                break
            
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()
                
                logger.log_step("Agent", "Action", f"{tool_name}({tool_args})")
                
                # Execute tool
                observation = self._execute_tool(tool_name, tool_args)
                logger.log_step("Tool", "Observation", observation)
                
                # Append to prompt
                current_prompt += f"\nThought: {thought}\nAction: {tool_name}({tool_args})\nObservation: {observation}\n"
            else:
                # Fallback if the agent doesn't output correct format but also doesn't output final answer.
                current_prompt += f"\nThought: {thought}\nObservation: Please use 'Action: tool_name(args)' or 'Final Answer: ...'\n"
            
            steps += 1
            
        if not final_answer:
            final_answer = "Max steps reached without a Final Answer."
            
        logger.log_event("AGENT_END", {"steps": steps, "final_answer": final_answer})
        return final_answer

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools.
        """
        if tool_name not in self.tool_names:
            return f"Error: Tool {tool_name} is not available."

        result = execute_dynamic_tool(tool_name, args)

        if result is None or result == "None":
            return "Error: No data found."

        Observation: {"ok": "false", "error": "Weather API request failed"}

        return result