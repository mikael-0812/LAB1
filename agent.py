import tools
import logger

class ReActAgent:
    """
    A ReAct Agent that uses Thought -> Action -> Observation loop to reason and answer questions.
    It can call tools from tools.py to gather information.
    Stops after answering or after max 3 loops.
    """

    def __init__(self):
        self.max_loops = 3
        self.tools = {
            'check_out_of_stock': tools.check_out_of_stock,
            'discount': tools.discount,
            'price': tools.price,
            'prerequisite_check': tools.prerequisite_check,
            'elective_check': tools.elective_check,
            'course_price': tools.course_price,
            'credit_count': tools.credit_count,
            'optimize_plan': tools.optimize_plan,
            'is_open': tools.is_open,
            'average_price': tools.average_price,
            'location_search': tools.location_search,
            'flight_price': tools.flight_price,
            'hotel_availability': tools.hotel_availability,
            'discount_package': tools.discount_package,
            'check_balance': tools.check_balance,
            'loan_interest': tools.loan_interest,
            'currency_exchange': tools.currency_exchange,
            'search_fashion': tools.search_fashion,
            'create_github_issue': tools.create_github_issue,
            'get_github_repo_info': tools.get_github_repo_info,
            'list_github_issues': tools.list_github_issues,
        }

    def run(self, query):
        """
        Run the ReAct loop for a given query.
        Prints Thought, Action, Observation for each step.
        Logs each event.
        """
        loop_count = 0
        observation = ""
        final_answer = None

        while loop_count < self.max_loops:
            # Thought: Analyze the query and decide on action
            thought = self.think(query, observation)
            print(f"Thought {loop_count + 1}: {thought}")
            logger.log_event('thought', 'Agent', query, None, thought)

            if "Câu trả lời cuối cùng" in thought:
                # Extract final answer
                final_answer = thought.split("Câu trả lời cuối cùng:")[-1].strip()
                logger.log_event('response', 'Agent', query, None, final_answer)
                break

            # Action: Choose a tool to call
            action = self.decide_action(thought)
            print(f"Action {loop_count + 1}: {action}")
            logger.log_event('action', 'Agent', query, None, action)

            if action:
                # Observation: Execute the action
                observation = self.execute_action(action)
                print(f"Observation {loop_count + 1}: {observation}")
                logger.log_event('observation', 'Agent', query, None, observation)
            else:
                observation = "No action taken."
                print(f"Observation {loop_count + 1}: {observation}")
                logger.log_event('observation', 'Agent', query, None, observation)

            loop_count += 1

        if final_answer:
            return final_answer
        else:
            no_answer = "Không thể trả lời sau vòng lặp tối đa."
            logger.log_event('response', 'Agent', query, None, no_answer)
            return no_answer

    def think(self, query, observation):
        """
        Mô phỏng suy nghĩ: Dựa trên query và observation trước đó, quyết định bước tiếp theo.
        Để đơn giản, logic này được hardcode; trong triển khai thực tế, sử dụng LLM.
        """
        query_lower = query.lower()
        # Check for search criteria in fashion
        if ("fashion" in query_lower or "áo" in query_lower or "quần" in query_lower or "giày" in query_lower) and ("price" in query_lower or "giá" in query_lower):
            if "dưới" in query_lower or "<" in query_lower:
                # Extract criteria, e.g., "price < 70"
                if "dưới" in query_lower:
                    parts = query_lower.split("dưới")
                    if len(parts) > 1:
                        try:
                            value = float(parts[1].strip().split()[0])
                            return f"Cần tìm áo với giá dưới {value}. Gọi search_fashion."
                        except:
                            pass
                elif "<" in query_lower:
                    if "price <" in query_lower:
                        parts = query_lower.split("price <")
                        if len(parts) > 1:
                            try:
                                value = float(parts[1].strip().split()[0])
                                return f"Cần tìm áo với price < {value}. Gọi search_fashion."
                            except:
                                pass
        # If we have a valid observation, provide final answer
        if observation and observation != "None" and observation != "No action taken.":
            try:
                # If observation is a list of dicts (e.g., from search_fashion), format it
                if isinstance(observation, str) and observation.startswith('['):
                    import ast
                    obs_list = ast.literal_eval(observation)
                    if isinstance(obs_list, list) and obs_list and isinstance(obs_list[0], dict):
                        answers = []
                        for item in obs_list:
                            ans = f"Tên: {item.get('name', 'N/A')}, Giá: {item.get('price', 'N/A')}"
                            if item.get('discount', 0) > 0:
                                ans += f", Giảm giá: {item['discount']}"
                            answers.append(ans)
                        return f"Câu trả lời cuối cùng: {'; '.join(answers)}"
                # If observation is a dict (e.g., from price tool), format it
                if isinstance(observation, dict):
                    if 'name' in observation and 'price' in observation:
                        answer = f"Tên: {observation['name']}, Giá: {observation['price']}"
                        if 'discount' in observation and observation['discount'] > 0:
                            answer += f", Giảm giá: {observation['discount']}"
                        return f"Câu trả lời cuối cùng: {answer}"
                # If observation is a number (price, etc.), format as answer
                float(observation)
                return f"Câu trả lời cuối cùng: {observation}"
            except ValueError:
                return f"Câu trả lời cuối cùng: {observation}"
        # Otherwise, proceed with actions
        # ... (rest of the code remains the same)
        if ("fashion" in query_lower or "áo" in query_lower or "quần" in query_lower or "giày" in query_lower) and ("stock" in query_lower or "hết hàng" in query_lower):
            return "Cần kiểm tra xem mặt hàng có hết hàng không. Gọi check_out_of_stock."
        elif ("fashion" in query_lower or "áo" in query_lower or "quần" in query_lower or "giày" in query_lower) and ("discount" in query_lower or "giảm giá" in query_lower):
            return "Cần lấy giảm giá cho mặt hàng. Gọi discount."
        elif ("fashion" in query_lower or "áo" in query_lower or "quần" in query_lower or "giày" in query_lower) and ("price" in query_lower or "giá" in query_lower):
            return "Cần lấy giá của mặt hàng. Gọi price."
        elif ("course" in query_lower or "khóa học" in query_lower or "môn học" in query_lower) and ("prerequisite" in query_lower or "tiên quyết" in query_lower):
            return "Cần kiểm tra điều kiện tiên quyết. Gọi prerequisite_check."
        elif ("course" in query_lower or "khóa học" in query_lower or "môn học" in query_lower) and ("elective" in query_lower or "tự chọn" in query_lower):
            return "Cần kiểm tra xem có phải tự chọn không. Gọi elective_check."
        elif ("course" in query_lower or "khóa học" in query_lower or "môn học" in query_lower) and ("price" in query_lower or "giá" in query_lower):
            return "Cần lấy giá khóa học. Gọi course_price."
        elif ("course" in query_lower or "khóa học" in query_lower or "môn học" in query_lower) and ("credit" in query_lower or "tín chỉ" in query_lower):
            return "Cần lấy số tín chỉ. Gọi credit_count."
        elif ("course" in query_lower or "khóa học" in query_lower or "môn học" in query_lower) and ("optimize" in query_lower or "tối ưu" in query_lower):
            return "Cần tối ưu hóa kế hoạch. Gọi optimize_plan."
        elif ("restaurant" in query_lower or "nhà hàng" in query_lower or "quán ăn" in query_lower) and ("open" in query_lower or "mở cửa" in query_lower):
            return "Cần kiểm tra xem có mở cửa không. Gọi is_open."
        elif ("restaurant" in query_lower or "nhà hàng" in query_lower or "quán ăn" in query_lower) and ("price" in query_lower or "giá" in query_lower):
            return "Cần lấy giá trung bình. Gọi average_price."
        elif ("restaurant" in query_lower or "nhà hàng" in query_lower or "quán ăn" in query_lower) and ("location" in query_lower or "vị trí" in query_lower):
            return "Cần tìm kiếm theo vị trí. Gọi location_search."
        elif ("travel" in query_lower or "du lịch" in query_lower or "đặt vé" in query_lower) and ("flight" in query_lower or "máy bay" in query_lower):
            return "Cần lấy giá vé máy bay. Gọi flight_price."
        elif ("travel" in query_lower or "du lịch" in query_lower or "đặt vé" in query_lower) and ("hotel" in query_lower or "khách sạn" in query_lower):
            return "Cần kiểm tra tình trạng khách sạn. Gọi hotel_availability."
        elif ("travel" in query_lower or "du lịch" in query_lower or "đặt vé" in query_lower) and ("discount" in query_lower or "giảm giá" in query_lower):
            return "Cần lấy giảm giá gói. Gọi discount_package."
        elif ("bank" in query_lower or "ngân hàng" in query_lower or "tài khoản" in query_lower) and ("balance" in query_lower or "số dư" in query_lower):
            return "Cần kiểm tra số dư. Gọi check_balance."
        elif ("bank" in query_lower or "ngân hàng" in query_lower or "tài khoản" in query_lower) and ("interest" in query_lower or "lãi suất" in query_lower):
            return "Cần lấy lãi suất cho vay. Gọi loan_interest."
        elif ("bank" in query_lower or "ngân hàng" in query_lower or "tài khoản" in query_lower) and ("exchange" in query_lower or "tỷ giá" in query_lower):
            return "Cần lấy tỷ giá hối đoái. Gọi currency_exchange."
        elif ("github" in query_lower or "repo" in query_lower) and ("issue" in query_lower or "vấn đề" in query_lower):
            return "Cần tạo issue trên GitHub. Gọi create_github_issue."
        elif ("github" in query_lower or "repo" in query_lower) and ("info" in query_lower or "thông tin" in query_lower):
            return "Cần lấy thông tin repo. Gọi get_github_repo_info."
        elif ("github" in query_lower or "repo" in query_lower) and ("list" in query_lower or "danh sách" in query_lower):
            return "Cần liệt kê issues. Gọi list_github_issues."
        # Default actions for use cases if no specific action
        elif any(word in query_lower for word in ['fashion', 'áo', 'quần', 'giày']):
            return "Cần lấy giá của mặt hàng. Gọi price."
        elif any(word in query_lower for word in ['course', 'khóa học', 'môn học']):
            return "Cần lấy giá khóa học. Gọi course_price."
        elif any(word in query_lower for word in ['restaurant', 'nhà hàng', 'quán ăn']):
            return "Cần lấy giá trung bình. Gọi average_price."
        elif any(word in query_lower for word in ['travel', 'du lịch', 'đặt vé']):
            return "Cần lấy giá vé máy bay. Gọi flight_price."
        elif any(word in query_lower for word in ['bank', 'ngân hàng', 'tài khoản']):
            return "Cần kiểm tra số dư. Gọi check_balance."
        elif any(word in query_lower for word in ['github', 'repo']):
            return "Cần lấy thông tin repo. Gọi get_github_repo_info."
        else:
            return "Câu trả lời cuối cùng: Tôi không biết cách trả lời câu hỏi này. (Updated)"

    def decide_action(self, thought):
        """
        Quyết định hành động dựa trên thought.
        Trả về chuỗi action, e.g., "check_out_of_stock Product 1"
        """
        if "check_out_of_stock" in thought:
            return "check_out_of_stock Product 1"  # Example item
        elif "discount" in thought:
            return "discount Product 1"
        elif "price" in thought:
            return "price Product 1"
        elif "search_fashion" in thought:
            if "dưới" in thought:
                parts = thought.split("dưới")
                if len(parts) > 1:
                    try:
                        value = float(parts[1].strip().split()[0])
                        return f"search_fashion price < {value}"
                    except:
                        pass
            elif "price <" in thought:
                parts = thought.split("price <")
                if len(parts) > 1:
                    try:
                        value = float(parts[1].strip().split()[0])
                        return f"search_fashion price < {value}"
                    except:
                        pass
            return "search_fashion price < 100"  # Default
        elif "prerequisite_check" in thought:
            return "prerequisite_check Course 1"
        elif "elective_check" in thought:
            return "elective_check Course 1"
        elif "course_price" in thought:
            return "course_price Course 1"
        elif "credit_count" in thought:
            return "credit_count Course 1"
        elif "optimize_plan" in thought:
            return "optimize_plan Course 1,Course 2"
        elif "is_open" in thought:
            return "is_open Restaurant 1"
        elif "average_price" in thought:
            return "average_price Restaurant 1"
        elif "location_search" in thought:
            return "location_search Address 1"
        elif "flight_price" in thought:
            return "flight_price Destination"
        elif "hotel_availability" in thought:
            return "hotel_availability Destination"
        elif "discount_package" in thought:
            return "discount_package Destination"
        elif "check_balance" in thought:
            return "check_balance ACC001"
        elif "loan_interest" in thought:
            return "loan_interest ACC001"
        elif "currency_exchange" in thought:
            return "currency_exchange ACC001"
        elif "create_github_issue" in thought:
            return "create_github_issue mikael-0812 LAB1 Test Issue This is a test issue created by the agent."
        elif "get_github_repo_info" in thought:
            return "get_github_repo_info mikael-0812 LAB1"
        elif "list_github_issues" in thought:
            return "list_github_issues mikael-0812 LAB1 open"
        else:
            return None

    def execute_action(self, action):
        """
        Execute the action by calling the appropriate tool.
        """
        parts = action.split(' ', 3)  # Split into tool_name, arg1, arg2, rest
        tool_name = parts[0]
        if tool_name in self.tools:
            if tool_name == 'optimize_plan':
                courses = parts[1].split(',') if len(parts) > 1 else []
                return str(self.tools[tool_name](courses))
            elif tool_name == 'search_fashion':
                criteria = parts[1] if len(parts) > 1 else ""
                return str(self.tools[tool_name](criteria))
            elif tool_name == 'create_github_issue':
                # parts: tool_name, repo_owner, repo_name, title body
                repo_owner = parts[1] if len(parts) > 1 else ""
                repo_name = parts[2] if len(parts) > 2 else ""
                title_body = parts[3] if len(parts) > 3 else ""
                title, body = title_body.split(' ', 1) if ' ' in title_body else (title_body, "")
                return str(self.tools[tool_name](repo_owner, repo_name, title, body))
            elif tool_name == 'get_github_repo_info':
                repo_owner = parts[1] if len(parts) > 1 else ""
                repo_name = parts[2] if len(parts) > 2 else ""
                return str(self.tools[tool_name](repo_owner, repo_name))
            elif tool_name == 'list_github_issues':
                repo_owner = parts[1] if len(parts) > 1 else ""
                repo_name = parts[2] if len(parts) > 2 else ""
                state = parts[3] if len(parts) > 3 else "open"
                return str(self.tools[tool_name](repo_owner, repo_name, state))
            else:
                args = parts[1] if len(parts) > 1 else ""
                return str(self.tools[tool_name](args))
        return "Tool not found."