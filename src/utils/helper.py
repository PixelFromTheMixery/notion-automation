def list_options(options, prompt: str, message: str, info: str = "basic") -> str:
    print(message)
    for option in options:
        if info == "basic":
            print(f'{options.index(option)+1}. {option["name"]}')
        elif info == "notion":
            print(f'{options.index(option)+1}. {option["title"][0]["text"]["content"]}')
    selection = int(input(prompt))
    return options[selection - 1]

