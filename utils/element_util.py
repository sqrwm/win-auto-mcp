def extract_element_info(element):
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

    if element.element_info.automation_id == "RootWebArea" and element.element_info.control_type == "Document" \
        and element.window_text() not in ["Favorites", "Downloads", "History"]:
        return info
    
    for child in element.children():
        info["children"].append(extract_element_info(child))
    return info