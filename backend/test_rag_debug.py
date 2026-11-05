from services.chroma_service import KnowledgeStore

store = KnowledgeStore()

questions = [
    "Tiểu đường type 2 là gì?",
    "Người mắc đái tháo đường nên lựa chọn thực phẩm như thế nào?",
    "Các yếu tố nguy cơ mắc đái tháo đường típ 2 là gì?",
    "Các triệu chứng thường gặp của đái tháo đường là gì?",
]

for question in questions:
    print("\n" + "=" * 60)
    print("Câu hỏi:", question)
    print("Unicode:", ascii(question))

    hits = store.query(question, top_k=4)

    for i, hit in enumerate(hits, 1):
        print(f"\nKết quả {i}")
        print("Distance:", round(hit["distance"], 4))
        print("Nguồn:", hit.get("source_title"))
        print("Nội dung:", hit["document"][:200])