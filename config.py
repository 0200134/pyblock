BLOCKS = {
    "Print Hello": {"template": 'print("Hello")', "color": "#FFD966", "nested": False},
    "Set Variable": {"template": '{name} = "{value}"', "color": "#C6E2FF", "nested": False},
    "Print Variable": {"template": 'print({name})', "color": "#FFA07A", "nested": False},
    "Repeat N": {"template": 'for i in range({value}):\n{child_code}', "color": "#87CEEB", "nested": True},
    "If": {"template": 'if {name} > {value}:\n{child_code}', "color": "#FFB6C1", "nested": True}
}

THEMES = {
    "기본": "#e6f7ff",
    "민트": "#d1f5e0"
}
