def collect_text_nodes(node, text_nodes):
    """
    Реккурсивно собирает текстовые узлы элемента node в список text_nodes
    :param node: предоставленный элемент (Element)
    :param text_nodes: список текстовых узлов (Text)
    :return: None
    """
    if node.nodeType == node.TEXT_NODE:
        text_nodes.append(node)
    elif node.nodeType == node.ELEMENT_NODE:
        for child in node.childNodes:
            collect_text_nodes(child, text_nodes)


def set_text(element, new_text: dict):
    """
    Рекурсивно заменяет весь текст в элементе, сохраняя структуру и стили.
    :param element: рассматриаваемый элемент (Element)
    :param new_text: dict[str, str]: старый текст - новый текст
    """
    # Собираем все текстовые узлы
    text_nodes = []
    collect_text_nodes(element, text_nodes)

    # Если текстовых узлов нет — выходим
    if not text_nodes:
        # print("В элементе не найдено ни одного текстового узла. Замен не произведено.")
        return

    for node in text_nodes:
        if new_text.get(node.data):
            node.data = new_text[node.data]
