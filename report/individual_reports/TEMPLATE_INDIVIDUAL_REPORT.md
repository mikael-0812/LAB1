# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Đào Quang Thắng
- **Student ID**: 2A202600030
- **Date**: 4/6/2026

---

## I. Technical Contribution (15 Points)

- **Modules Implemented**:
  - `agent.py`:vòng lặp ReAct (Thought → Action → Observation) và quản lý luồng điều khiển.
  - `logger.py`: sử dụng hệ thống logging để ghi lại các sự kiện `thought`, `action`, `observation`, và `response`.
  - `tools.py`: tích hợp nhiều công cụ theo ngữ cảnh (fashion, course, restaurant, travel, banking, GitHub) để agent có thể gọi khi cần.

- **Code Highlights**:
  - Trong `agent.py`, hàm `run()` thực hiện vòng lặp tối đa 3 lần, sinh `Thought`, quyết định `Action`, thực thi công cụ và ghi lại `Observation`.
  - Hàm `think()` giải mã truy vấn, xác định loại hành động cần gọi và chuyển tiếp quan sát trước đó vào quá trình suy luận.
  - Hàm `decide_action()` ánh xạ chuỗi `thought` sang tên công cụ và tham số cụ thể.
  - Hàm `execute_action()` gọi đúng công cụ trong `self.tools`, xử lý đặc biệt cho các công cụ như `optimize_plan`, `search_fashion` và GitHub.
  - Hệ thống logging trong `logger.py` ghi chi tiết theo định dạng `Event: ..., System: ..., Question: ..., Details: ...` vào `results.log`.

- **Documentation**:
  - `agent.py` mô tả rõ ràng chu kỳ ReAct và nơi agent chuyển từ suy nghĩ sang thực thi công cụ.
  - `logger.py` cung cấp wrapper `log_event()` để giữ cho toàn bộ hệ thống dễ mở rộng và dễ đọc log.
  - Mỗi bước trong `run()` được gán rõ nhãn `Thought`, `Action`, `Observation`, giúp phân tích lỗi và so sánh với chatbot dễ dàng.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**:
  - Agent đôi khi trả về `Câu trả lời cuối cùng` quá sớm hoặc sai do `observation` được chuyển thành chuỗi và không khớp với định dạng mong đợi.
  - Ví dụ: khi `observation` là chuỗi JSON-style từ `search_fashion`, logic trong `think()` có thể không phân tích đúng nếu định dạng chuỗi thay đổi.

- **Log Source**:
  - `logger.py` ghi lại sự kiện `thought`, `action`, `observation`, và `response` vào `results.log`.
  - Mẫu log: `Event: observation, System: Agent, Question: ..., Details: ...`.

- **Diagnosis**:
  - Nguyên nhân chính là sự kết hợp giữa prompt/logic nội bộ và định dạng trả về công cụ.
  - `think()` hiện tại giả lập suy nghĩ bằng cách kiểm tra chuỗi `query_lower`; do đó nếu truy vấn không khớp mẫu cứng, agent dễ chọn hành động sai hoặc bỏ qua bước cần thiết.
  - Cấu trúc công cụ và parser `execute_action()` cũng khiến agent dễ gặp lỗi nếu action string không có đúng số tham số.

- **Solution**:
  - Cải thiện chuỗi logic trong `think()` để xử lý rõ ràng hơn các điều kiện và tránh chuyển sang `Câu trả lời cuối cùng` khi observation chưa được chuẩn hóa.
  - Sửa `execute_action()` để tách tham số an toàn hơn và xác minh `tool_name` trước khi gọi.
  - Thêm log chi tiết cho từng bước: `thought`, `action`, `observation`, `response`, giúp dễ truy vết sự cố hơn.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: `Thought` block giúp agent kiểm tra lại truy vấn và quyết định bước tiếp theo trước khi gọi công cụ. So với chatbot trả lời trực tiếp, ReAct cho phép tách rõ phần suy luận và phần thao tác dữ liệu.
2. **Reliability**: Agent có thể hoạt động kém hơn khi câu hỏi đơn giản không cần gọi công cụ, vì vòng lặp ReAct hiện tại thêm độ phức tạp và phụ thuộc vào logic cứng. Nếu `think()` không nhận diện chính xác intent, agent sẽ mất bước hoặc chọn sai tool, làm kết quả kém tin cậy hơn chatbot thuần túy.
3. **Observation**: Phản hồi môi trường (`Observation`) giúp agent điều chỉnh bước tiếp theo. Khi tool trả về dữ liệu cụ thể, agent dùng nó để kết thúc vòng lặp hoặc tiếp tục gọi công cụ khác, thay vì đoán mò.

---

## IV. Future Improvements (5 Points)

- **Scalability**:
  - Chuyển sang kiến trúc bất đồng bộ với hàng đợi công cụ để xử lý nhiều truy vấn song song.
  - Tách `ReAct loop` ra thành module riêng, cho phép mở rộng bộ công cụ và thêm middleware kiểm soát.

- **Safety**:
  - Thêm một lớp giám sát (`Supervisor LLM`) để xác thực các hành động trước khi thực thi, giảm rủi ro gọi nhầm tool hoặc thao tác không an toàn.
  - Kiểm tra dạng đầu vào và đầu ra tool chặt chẽ, tránh injection qua chuỗi action.

- **Performance**:
  - Lưu cache kết quả tool phổ biến hoặc dùng vector DB cho truy vấn nhiều công cụ, giảm số lần gọi API.
  - Tối ưu hóa định dạng `observation` trong JSON/struct thay vì dùng chuỗi, giúp parser nhanh hơn và ít lỗi hơn.

---


