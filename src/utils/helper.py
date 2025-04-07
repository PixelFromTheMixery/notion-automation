def list_options(options, prompt: str, message: str, info: str = "name") -> str:
    print(message)
    for option in options:
        if info == "name":
            print(f"{options.index(option)+1}. {option["name"]}")
        if info == "basic":
            print(f"{options.index(option)+1}. {option}")
        elif info == "notion":
            print(f'{options.index(option)+1}. {option["title"][0]["text"]["content"]}')
    selection = int(input(prompt))
    return options[selection - 1]


def multi_options(options, prompt: str, message: str) -> str:
    print(message)
    for option in options:
        print(f"{options.index(option)+1}. {option}")
    print(message + "(with no spaces. E.g.: 1,3,5)")
    selection = input(prompt)
    select_list = [int(x.strip()) - 1 for x in selection.split(",")]

    results = []
    for item in select_list:
        results.append(options[item])

    return results
