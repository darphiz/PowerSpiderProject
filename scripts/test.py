def flatten_names(node):
    """
    Recursively flattens the node data into a list of names.
    """
    names = [node["name"]]
    for child in node["children"]:
        names += flatten_names(child)
    return names



if __name__ == "__main__":
    import json
    file = open("charity_causes.json", "r")
    res_json = json.load(file)
    causes = res_json["getCauseHierarchy"]

    # Flatten the causes into a list of names
    names = []
    for cause in causes:
        names += flatten_names(cause)

    # Print the flattened list of names
    names = sorted(names)
    with open("charity_causes.txt", "w") as f:
        for name in names:
            f.write(name + "\n")