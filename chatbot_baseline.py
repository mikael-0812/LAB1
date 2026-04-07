class ChatbotBaseline:
    """
    A baseline chatbot that provides static, generic responses for different use cases.
    Unlike the ReActAgent, it does not call any tools or perform dynamic reasoning.
    It just gives predefined answers based on keywords in the query.
    """

    def __init__(self):
        self.responses = {
            'fashion': "Đối với các mặt hàng thời trang, giá cả thay đổi và có giảm giá. Vui lòng kiểm tra các mặt hàng cụ thể.",
            'course': "Đối với các khóa học, hãy xem xét các điều kiện tiên quyết và số tín chỉ. Giá phụ thuộc vào khóa học.",
            'restaurant': "Các nhà hàng có giờ mở cửa và giá cả khác nhau. Tìm kiếm theo vị trí để có các lựa chọn.",
            'travel': "Đặt vé du lịch bao gồm vé máy bay và khách sạn với khả năng giảm giá.",
            'banking': "Dịch vụ ngân hàng bao gồm kiểm tra số dư, lãi suất và tỷ giá hối đoái."
        }

    def respond(self, query):
        """
        Trả lời câu hỏi với câu trả lời tĩnh dựa trên từ khóa.
        """
        query_lower = query.lower()
        if 'fashion' in query_lower or 'áo' in query_lower or 'quần' in query_lower or 'giày' in query_lower:
            return self.responses['fashion']
        elif 'course' in query_lower or 'khóa học' in query_lower or 'môn học' in query_lower:
            return self.responses['course']
        elif 'restaurant' in query_lower or 'nhà hàng' in query_lower or 'quán ăn' in query_lower:
            return self.responses['restaurant']
        elif 'travel' in query_lower or 'du lịch' in query_lower or 'đặt vé' in query_lower:
            return self.responses['travel']
        elif 'bank' in query_lower or 'ngân hàng' in query_lower or 'tài khoản' in query_lower or 'balance' in query_lower or 'số dư' in query_lower or 'interest' in query_lower or 'lãi suất' in query_lower or 'exchange' in query_lower or 'tỷ giá' in query_lower:
            return self.responses['banking']
        else:
            return "Tôi xin lỗi, tôi không có thông tin về chủ đề đó. (Updated)"