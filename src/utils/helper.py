def list_options(options, prompt: str, message: str) -> str:
    print(message)
    for option in options:
        print(f'{options.index(option)+1}. {option["name"]}')
    selection = int(input(prompt))
    return options[selection-1]["name"]