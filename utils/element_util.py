def extract_element_info(element, max_web_depth=5, web_depth=0, max_web_length=3):
    info = {
        "title": element.window_text(),
        "control_type": element.element_info.control_type,
        "automation_id": element.element_info.automation_id,
        "class_name": element.element_info.class_name,
        "rectangle": {
            "left": element.rectangle().left,
            "top": element.rectangle().top,
            "right": element.rectangle().right,
            "bottom": element.rectangle().bottom
        },
        "children": []
    }
    try:
        info["value"] = element.get_value(),
    except Exception as e:
        pass

    try:
        if element.element_info.control_type == "CheckBox":
            info["is_checked"] = element.get_toggle_state() == 1
    except Exception as e:
        pass
    
    try:
        if element.element_info.control_type == "TreeItem":
            info["is_expanded"] = element.is_expanded()
        if not element.is_expanded():
            return info
    except Exception as e:
        pass

    is_web_page = False
    if element.element_info.automation_id == "RootWebArea" and element.element_info.control_type == "Document" \
        and element.window_text() not in ["Favorites", "Downloads", "History"] :
        is_web_page = True
    
    if web_depth > max_web_depth:
        return info
    
    next_web_depth = web_depth + 1 if web_depth > 0 else 0
    if is_web_page and web_depth == 0: 
        next_web_depth = 1

    idx_web_length = 0
    for child in element.children():
        if is_web_page and idx_web_length >= max_web_length:
            break
        idx_web_length += 1
        info["children"].append(extract_element_info(child, max_web_depth=max_web_depth, web_depth=next_web_depth))
    return info
