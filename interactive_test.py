from chatbot_baseline import ChatbotBaseline
from agent import ReActAgent
import logger

def main():
    """
    Interactive test runner for Chatbot and Agent.
    Allows user to input queries in terminal and see responses with detailed logging.
    """
    chatbot = ChatbotBaseline()
    agent = ReActAgent()

    print("Trình Chạy Thử Tương Tác")
    print("Nhập câu hỏi để thử nghiệm cả Chatbot và Agent.")
    print("Gõ 'quit' để thoát.")
    print("Gõ 'error_tests' để chạy các test case lỗi định sẵn.")
    print()

    while True:
        query = input("Nhập câu hỏi: ").strip()
        if query.lower() == 'quit':
            break
        elif query.lower() == 'error_tests':
            run_error_tests(chatbot, agent)
            continue

        print(f"\nCâu hỏi: {query}")
        print("-" * 50)

        # Chatbot response
        print("Phản hồi của Chatbot:")
        chatbot_answer = chatbot.respond(query)
        print(chatbot_answer)
        logger.log_event('response', 'Chatbot', query, None, chatbot_answer)
        print()

        # Agent response
        print("Lý luận và Phản hồi của Agent:")
        agent_answer = agent.run(query)
        print(f"Câu trả lời cuối cùng: {agent_answer}")
        print()

def run_error_tests(chatbot, agent):
    """
    Run predefined error test cases where Agent may fail to respond properly.
    """
    error_queries = [
        "What is the weather today?",  # Unrelated query
        "Price of non-existent item",  # Item not in data
        "Check balance for invalid account",  # Invalid account ID
        "Optimize plan for unknown courses",  # Unknown courses
        "Flight price to nowhere",  # No matching data
        "Restaurant search in unknown location",  # No results
    ]

    print("\nChạy Test Cases Lỗi:")
    print("=" * 50)

    for query in error_queries:
        print(f"\nTest Case Lỗi: {query}")
        print("-" * 30)

        # Chatbot response
        print("Phản hồi của Chatbot:")
        chatbot_answer = chatbot.respond(query)
        print(chatbot_answer)
        logger.log_event('response', 'Chatbot', query, None, chatbot_answer)
        print()

        # Agent response
        print("Lý luận và Phản hồi của Agent:")
        agent_answer = agent.run(query)
        print(f"Câu trả lời cuối cùng: {agent_answer}")
        print()

if __name__ == "__main__":
    main()